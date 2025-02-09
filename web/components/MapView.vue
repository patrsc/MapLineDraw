<template>
    <div id="map" class="map-element" ref="map-element"></div>
</template>

<script setup lang="ts">

import type {
    Curve,
    ColorMap,
    CurveCache,
    PreparedColorMap,
    CurveCacheItem,
    GlobePoint,
    SplineData,
    MapSettings
} from "~/types"

import L from "leaflet"
import 'leaflet/dist/leaflet.css'

import { findNearestIndexOnLine } from "~/utils/geo"

let map: L.Map

const mapElement = useTemplateRef('map-element')

interface Props {
    colorMap: ColorMap
}

const props = defineProps<Props>()
const mapSettings = defineModel<MapSettings>('mapSettings', {required: true})
const curves = defineModel<Curve[]>('curves', {required: true})
const selectedCurveIndex = defineModel<number>('selectedCurveIndex', {required: true})
const drawMode = defineModel<boolean>('drawMode', {required: true})
const emit = defineEmits(["select-curve"])

defineExpose({
    deleteSelectedPolyline,
    toggleClosed,
})

const isCurveSelected = computed(() => selectedCurveIndex.value != -1)
const selectedCurve = computed(() => {
    const index = selectedCurveIndex.value
    return (index == -1) ? null : curves.value[index]
})

watch(drawMode, (newMode) => {
    if (newMode) {
        setLeafletCursor("crosshair")
    } else {
        setLeafletCursor("grab")
    }
})

watch(props.colorMap, update)

watch(selectedCurveIndex, selectPolyline)

watch(curves, () => {
    console.log("curves changed from outside")
    initCache()
})

watch(mapSettings, (settings) => {
    const c = settings.center
    const center = map.getCenter()
    const zoom = map.getZoom()
    if (center.lat != c.lat || center.lng != c.lon || zoom != settings.zoom) {
        map.setView(...getMapView())
    }
})

let updating = false
let curvesCache: CurveCache = []

function initCache() {
    curvesCache = curves.value.map((c) => {
        return {
            points: c.controlPoints.map((pt, i) => newPoint(pt.lat, pt.lon, i)),
            spline: {requestedId: 1, id: 0, data: null},
            layers: [],
        }
    })
}

function computeProperties() {
    const p = selectedCurve.value
    if (p == null) {
        return []
    }
    const nPoints = p.controlPoints.length
    const data = curvesCache[selectedCurveIndex.value].spline.data
    let texts = [`Points: ${nPoints}`]
    if (data) {
        const distance = data.distance[data.distance.length - 1]
        const maxCurvature = Math.max(...data.curvature.map(Math.abs))
        let minRadius = 1/maxCurvature
        let minRadiusText = ""
        if (minRadius >= 1e6) {
            minRadiusText = "∞"
        } else {
            minRadiusText = minRadius.toFixed(0)
        }
        const minSpeed = Math.min(...data.speed)
        texts.push(`Length: ${(distance/1000).toFixed(1)} km`)
        texts.push(`Radius: ${minRadiusText} m`)
        texts.push(`Speed: ${(minSpeed).toFixed(0)} km/h`)
    }
    return texts
}

function createMap() {
    if (!mapElement.value) return
    let options = {
        doubleClickZoom: false,
    }
    map = L.map(mapElement.value, options)
}

function initializeMap() {
    map.setView(...getMapView());
    const tiles = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    //const tiles = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png'
    //const tiles = 'https://tile.tracestrack.com/topo__/{z}/{x}/{y}.png?key=APIKEY'
    L.tileLayer(tiles, {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    map.on('click', addControlPoint)
    map.on('zoomend', updateMapView)
    map.on('moveend', updateMapView)
}

function getMapView(): [[number, number], number] {
    const m = mapSettings.value
    return [[m.center.lat, m.center.lon], m.zoom]
}

function updateMapView() {
    const c = map.getCenter()
    mapSettings.value = {
        center: {lat: c.lat, lon: c.lng},
        zoom: map.getZoom(),
        background: mapSettings.value.background,
    }
}

function setLeafletCursor(cursor: "grab" | "crosshair") {
    mapElement.value?.style.setProperty("cursor", cursor, "important")
}

function toggleClosed(index: number) {
    const c = curves.value[index]
    c.closed = !c.closed
    requestCurveUpdate()
    updateSingle(selectedCurveIndex.value)
}

async function addControlPoint(e: L.LeafletMouseEvent) {
    if (!drawMode.value) {
        unselect()
        return
    }
    if (!isCurveSelected.value) {
        selectedCurveIndex.value = curves.value.length
        curves.value.push(newCurve("Curve"))
        curvesCache.push({points: [], spline: {requestedId: 0, id: 0, data: null}, layers: []})
    }
    const latlng = e.latlng
    await nextTick()  // wait for selectedCurveIndex to update
    insertPoint(latlng.lat, latlng.lng, selectedCurve.value!.controlPoints.length)
    requestCurveUpdate()
}

function newCurve(name: string): Curve {
    return {
        name: name,
        controlPoints: [],
        closed: false,
    }
}

function newPoint(lat: number, lon: number, index: number) {
    const point = L.circleMarker([lat, lon], {
        className: 'control-point',
        radius: 15,
        bubblingMouseEvents: false,
    })
    moveableMarker(map, point, index)
    return point
}

function insertPoint(lat: number, lon: number, index: number) {
    // insert point at given index
    const point = { lat, lon}
    const currentPolyline = selectedCurve.value
    if (!currentPolyline) return
    currentPolyline.controlPoints.splice(index, 0, point)
    updateCache(selectedCurveIndex.value)
    updateSingle(selectedCurveIndex.value)
}


async function deletePolyline(index: number) {
    console.log("deletePolyline", index)
    deleteItems(index)
    curves.value.splice(index, 1)
    curvesCache.splice(index, 1)
    unselect()
}

function deleteSelectedPolyline() {
    console.log("deleteSelectedPolyline")
    if (isCurveSelected.value) {
        deletePolyline(selectedCurveIndex.value)
    }
}

function unselect() {
    selectedCurveIndex.value = -1
}

function selectPolyline(index: number, oldIndex: number) {
    console.log("selectPolyline", index, oldIndex)
    if (index == -1) {
        drawMode.value = false
    } else {
        updateSingle(index)
    }
    if (oldIndex != -1 && oldIndex < curves.value.length) {
        updateSingle(oldIndex)
    }
}

function getPreparedColorMap(): PreparedColorMap {
    const colorMap = props.colorMap
    const colorItemsReverse = colorMap.items.slice().reverse();
    const colors = colorItemsReverse.map((c) => c.color)
    const limits = colorItemsReverse.map((c) => c.limit).filter((c) => c != null)
    const factors = colorMap.items.map((c, i) => Math.pow(1.15, i)).reverse()
    return { colors, limits, factors }
}

function update() {
    const cm = getPreparedColorMap()
    for (let i = 0; i < curves.value.length; i++) {
        updateCurve(i, cm)
    }
}

function updateSingle(index: number) {
    const cm = getPreparedColorMap()
    updateCurve(index, cm)
}

function updateCurve(index: number, cm: PreparedColorMap) {
    console.log("updateCurve", index)
    deleteItems(index)
    drawItems(index, cm)
}

function deleteItems(index: number) {
    for (let layer of curvesCache[index].layers) {
        map.removeLayer(layer)
    }
    curvesCache[index].layers = []
}

function drawItems(polyIndex: number, cm: PreparedColorMap) {
    const p = curves.value[polyIndex]
    const cc = curvesCache[polyIndex]
    drawSplineColorMap(cc, polyIndex, cm)
    if (polyIndex == selectedCurveIndex.value) {
        drawControlLine(p, polyIndex)
        drawPoints(cc, polyIndex)
        emit("select-curve", computeProperties())
    }
}

function drawPoints(curve: CurveCacheItem, curveIndex: number) {
    curve.points.forEach((point, pointIndex) => {
        if (pointIndex == curve.points.length - 1) {
            point.options.className = 'control-point selected-point'
        } else {
            point.options.className = 'control-point'
        }
        map.addLayer(point)
        curvesCache[curveIndex].layers.push(point)
    })
}

function drawSplineColorMap(p: CurveCacheItem, curveIndex: number, cm: PreparedColorMap) {
    const spline = p.spline
    if (spline.data) {
        const { limits, colors, factors } = cm
        const lat = spline.data.lat
        const lon = spline.data.lon
        const speeds = spline.data.speed
        let current: [number, number][] = [[lat[0], lon[0]]]
        let prevColorIndex = -1
        let colorIndex = 0  // initial guess
        for (let i = 1; i < lat.length; i++) {
            const speedPrev = speeds[i - 1]
            const speed = speeds[i]
            const s = Math.min(speedPrev, speed)
            colorIndex = getColorIndex(s, limits, colorIndex)
            if (prevColorIndex === -1 || colorIndex == prevColorIndex) {
                current.push([lat[i], lon[i]])
            } else {
                flushCurve(current, colors[prevColorIndex], factors[prevColorIndex], curveIndex)
                current = [[lat[i - 1], lon[i - 1]]]
                current.push([lat[i], lon[i]])
            }
            prevColorIndex = colorIndex
        }
        flushCurve(current, colors[prevColorIndex], factors[prevColorIndex], curveIndex)
    }
}

function getColorIndex(value: number, limits: number[], guessIndex: number) {
    // hot code: implementation optimized for performance
    let n = limits.length
    let i = (guessIndex < n) ? guessIndex : (n - 1)
    let isSmaller = value < limits[i]
    let prevSmaller
    while (true) {
        if (!isSmaller) {
            i++
            if (i == n) {
                return n
            }
            isSmaller = value < limits[i]
        } else {
            if (i == 0) {
                return i
            }
            prevSmaller = value < limits[i - 1]
            if (!prevSmaller) {
                return i
            } else {
                isSmaller = prevSmaller
                i--
            }
        }
    }
}

function flushCurve(coordinates: [number, number][], color: string, factor: number, index: number) {
    const options = {
        color: color,
        weight: 4 * factor,
        lineCap: 'butt' as const,
        bubblingMouseEvents: false,
    }
    const line = L.polyline(coordinates, options)
    map.addLayer(line)
    line.on("click", () => {
        selectedCurveIndex.value = index
    })
    curvesCache[index].layers.push(line)
}

function drawControlLine(currentPolyline: Curve, index: number) {
    const cl = 'control-line selected-line'
    const points = currentPolyline.controlPoints
    const closed = currentPolyline.closed
    const latlng = (p: GlobePoint): [number, number] => [p.lat, p.lon]
    if (points.length > 1) {
        const coordinates = points.map(latlng)
        const line = L.polyline(coordinates, {
            className: cl,
            bubblingMouseEvents: false,
        })
        line.on("click", (e) => lineClick(e, index))
        map.addLayer(line)
        curvesCache[index].layers.push(line)
    }
    if (points.length > 2 && closed) {
        const coordinates = [latlng(points[points.length - 1]), latlng(points[0])]
        const line = L.polyline(coordinates, {
            className: cl + ' thin-line',
            bubblingMouseEvents: false,
        })
        map.addLayer(line)
        curvesCache[index].layers.push(line)
    }
}

function lineClick(e: L.LeafletMouseEvent, index: number) {
    addIntermediatePoint(index, e.latlng)
    requestCurveUpdate()
}

function addIntermediatePoint(polyIndex: number, latlng: L.LatLng) {
    const poly = curves.value[polyIndex]
    const insertIndex = findNearestIndexOnLine(poly.controlPoints, latlng.lat, latlng.lng)
    insertPoint(latlng.lat, latlng.lng, insertIndex + 1)
}

function moveableMarker(map: L.Map, marker: L.CircleMarker, index: number) {
    function trackCursor(e: L.LeafletMouseEvent) {
        marker.setLatLng(e.latlng)
        if (!selectedCurve.value) return
        selectedCurve.value.controlPoints[index] = {lat: e.latlng.lat, lon: e.latlng.lng}
        updateSingle(selectedCurveIndex.value)
        requestCurveUpdate()
    }
    let dragStartLatLng: L.LatLng | undefined = undefined

    function dragEnd() {
        map.dragging.enable()
        map.off("mousemove", trackCursor)
        if (marker.getLatLng() == dragStartLatLng) {
            // marker was not moved -> delete
            dragStartLatLng = undefined
            const n = deletePoint(index)
            if (n > 0) {
                requestCurveUpdate()
            }
        }
    }

    marker.on("mousedown", () => {
        dragStartLatLng = marker.getLatLng()
        map.dragging.disable()
        map.on("mousemove", trackCursor)
    })
    marker.on("mouseup", dragEnd)

    return marker
}

function deletePoint(index: number) {
    if (!selectedCurve.value) return 0
    const points = selectedCurve.value.controlPoints
    points.splice(index, 1)
    updateCache(selectedCurveIndex.value)
    const n = points.length
    if (n == 0) {
        deletePolyline(selectedCurveIndex.value)
    } else {
        updateSingle(selectedCurveIndex.value)
    }
    return n
}

function updateCache(curveIndex: number) {
    // re-compute points of given curve
    const f = (pt: GlobePoint, i: number) => newPoint(pt.lat, pt.lon, i)
    curvesCache[curveIndex].points = curves.value[curveIndex].controlPoints.map(f)
}

function requestCurveUpdate() {
    // request update of selected curve by incrementing requestedId
    if (isCurveSelected.value) {
        curvesCache[selectedCurveIndex.value].spline.requestedId++
    }
}

async function updateCurves() {
    // if update is currently running -> abort
    if (updating) {
        return
    }
    // check if any curve needs update
    updating = true
    let indicesUdated = []
    for (const [index, c] of curvesCache.entries()) {
        if (c.spline.id < c.spline.requestedId) {
            // needs update
            await updateSpline(curves.value[index], c)
            indicesUdated.push(index)
        }
    }
    for (let index of indicesUdated) {
        updateSingle(index)
    }
    updating = false
}

async function updateSpline(p: Curve, c: CurveCacheItem) {
    // load spline data via API
    if (p.controlPoints.length >= 2) {
        c.spline.data = await loadSpline(p)
    } else {
        c.spline.data = null
    }
    c.spline.id = c.spline.requestedId
}

async function loadSpline(p: Curve): Promise<null | SplineData> {
    const coordinates = p.controlPoints
    const data = {
        control: {
            lat: coordinates.map((c: GlobePoint) => c.lat),
            lon: coordinates.map((c: GlobePoint) => c.lon),
        },
        desired_degree: 3,
        closed: p.closed,
        max_distance: 30,
    }
    const url = "http://localhost:8000/curve"
    const options = {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    }
    const res = await fetch(url, options)
    if (res.status == 200) {
        return await res.json()
    } else {
        console.error(`response code: ${res.status}`)
        return null
    }
}

onMounted(() => {
    createMap()
    initializeMap()
    initCache()
    setInterval(updateCurves, 50)
})

</script>

<style>
.map-element {
    flex: 1;
}

.control-point {
    fill: rgb(76, 0, 255);
    fill-opacity: 0.3;
    stroke: rgb(76, 0, 255);
    stroke-width: 2px;
}

.selected-point {
    fill: rgb(255, 119, 0);
    fill-opacity: 0.3;
    stroke: rgb(255, 119, 0);
    stroke-width: 4px;
}

.control-line {
    stroke: rgba(76, 0, 255, 0.5);
    stroke-width: 5px;
}

.selected-line {
    stroke: rgb(76, 0, 255, 0.5);
    stroke-width: 10px;
}
.thin-line {
    stroke-width: 5px;
}

.curve {
    stroke: black;
    stroke-width: 5px;
}


/* Grey map
.leaflet-tile-pane {
    -webkit-filter: grayscale(100%);
    filter: grayscale(100%);
}
*/
</style>
