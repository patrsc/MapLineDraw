<template>
    <div class="map-app"
        @keyup.esc="unselect"
        @keyup.delete="deleteSelectedPolyline"
        @keyup="handleKeyboardEvent"
    >
        <div class="sidebar" @click="unselect">
            <div class="sidebar-text">
                <h2>MapLineDraw</h2>
                <h4>Draw</h4>
                <p>Click on different map positions to draw.
                    Press <code>Esc</code> to finish. You can draw multiple curves.
                </p>
                <h4>Select</h4>
                <p>Click on a curve to select it.</p>
                <h4>Edit curve</h4>
                <p>Move points by dragging. Delete point by clicking.
                    Add intermediate points by clicking on control line.
                </p>
                <button class="btn-draw" @click.stop="toggleDrawMode">{{ btnDrawText }}</button>
                <h2 class="mt-3">Curves</h2>
            </div>
            <div class="polyline-list">
                <div v-if="project.curves.length == 0" class="no-lines-placeholder">
                    No curves yet.
                </div>
                <template v-for="(c, index) in project.curves">
                    <div :class="listItemClass(index)" @click.stop="selectPolyline(index)">
                        <div>{{ `${c.name} (${c.controlPoints.length} points)` }}</div>
                        <div v-if="index == selectedCurveIndex">
                            <button @click.stop="toggleClosed(c)">
                                {{ (c.closed) ? "Open" : "Close" }}
                            </button>
                            <button @click.stop="deleteSelectedPolyline">Delete</button>
                        </div>
                    </div>
                </template>
            </div>
            <div class="sidebar-text">
                <div class="curve-props" v-if="isCurveSelected">
                    <h2 style="width: 100%">Properties</h2>
                    <div v-for="text in properties">{{ text }}</div>
                </div>
                <h2 class="mt-3">Legend</h2>
                <select @change="setColormap" @click.stop :value="project.settings.selectedColorMapIndex">
                    <option v-for="(c, index) in project.colorMaps" :value="index">
                        {{ c.name }}
                    </option>
                </select>
                <div class="legend">
                    <div v-for="item in selectedColorMap.items" class="legend-item">
                        <div class="legend-color" :style="`background-color: ${item.color}`"></div>
                        <div>{{ item.label }}</div>
                    </div>
                </div>
            </div>
        </div>
        <div id="map" ref="map-element"></div>
    </div>
</template>

<script setup>

import L from "leaflet"
import 'leaflet/dist/leaflet.css'

import { colorMaps } from "~/utils/themes"

let map
const selectedCurveIndex = ref(-1)
const selectedCurve = computed(() => {
    return (selectedCurveIndex.value == -1) ? null : project.value.curves[selectedCurveIndex.value]
})
const isCurveSelected = computed(() => selectedCurveIndex.value != -1)
const selectedColorMap = computed(() => getSelectedColorMap())

let updating = false
let drawMode = ref(false)

const mapElement = useTemplateRef('map-element')

const btnDrawText = computed(() => {
    if (drawMode.value) {
        return "Finish drawing"
    } else {
        if (!isCurveSelected.value) {
            return "Draw new curve"
        } else {
            return "Add points"
        }
    }
})

watch(drawMode, (newMode) => {
    if (newMode) {
        setLeafletCursor("crosshair")
    } else {
        setLeafletCursor("grab")
    }
})

const project = ref({
    info: {
        name: "Project",
        description: "",
        author: "",
    },
    curves: [],
    colorMaps: colorMaps,
    settings: {
        selectedColorMapIndex: 0,
        map: {
            center: {
                lat: 51.505,
                lon: -0.09,
            },
            zoom: 13,
            background: "osm",
        },
    }
})

let saveIdRequest = 0
let saveId = 0

watch(project, requestSave, {deep: true})

let curvesCache = [] // {points, spline, layers}
let numUpdates = ref(0)

const properties = computed(() => {
    const p = selectedCurve.value
    const nPoints = p.controlPoints.length
    const data = curvesCache[selectedCurveIndex.value].spline.data
    numUpdates.value // read only to update when curvesCache updated
    let texts = [`Points: ${nPoints}`]
    if (data) {
        const distance = data.distance[data.distance.length - 1]
        const maxCurvature = Math.max(...data.curvature.map(Math.abs))
        let minRadius = 1/maxCurvature
        if (minRadius >= 1e6) {
            minRadius = "∞"
        } else {
            minRadius = minRadius.toFixed(0)
        }
        const minSpeed = Math.min(...data.speed)
        texts.push(`Length: ${(distance/1000).toFixed(1)} km`)
        texts.push(`Radius: ${minRadius} m`)
        texts.push(`Speed: ${(minSpeed).toFixed(0)} km/h`)
    }
    return texts
})

function createMap() {
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

function getMapView() {
    const m = project.value.settings.map
    return [[m.center.lat, m.center.lon], m.zoom]
}

function updateMapView() {
    const z = map.getZoom()
    const c = map.getCenter()
    project.value.settings.map.center.lat = c.lat
    project.value.settings.map.center.lon = c.lng
    project.value.settings.map.zoom = z
}

function handleKeyboardEvent(e) {
    if (e.key == 'd') {
        toggleDrawMode()
    }
}

function toggleDrawMode() {
    drawMode.value = !drawMode.value
}

function setLeafletCursor(cursor) {
    mapElement.value.style.setProperty("cursor", cursor, "important")
}

function addControlPoint(e) {
    if (!drawMode.value) {
        unselect()
        return
    }
    if (!isCurveSelected.value) {
        selectedCurveIndex.value = project.value.curves.length
        project.value.curves.push(newCurve("Curve"))
        curvesCache.push({points: [], spline: {requestedId: 0, id: 0, data: null}, layers: []})
    }
    const latlng = e.latlng
    insertPoint(latlng.lat, latlng.lng, selectedCurve.value.controlPoints.length)
    requestCurveUpdate()
}

function newCurve(name) {
    return {
        name: name,
        controlPoints: [],
        closed: false,
    }
}

function newPoint(lat, lon, index) {
    const point = L.circleMarker([lat, lon], {
        className: 'control-point',
        radius: 15,
        bubblingMouseEvents: false,
    })
    moveableMarker(map, point, index)
    return point
}

function insertPoint(lat, lon, index) {
    // insert point at given index
    const point = { lat: lat, lon: lon }
    const currentPolyline = selectedCurve.value
    currentPolyline.controlPoints.splice(index, 0, point)
    updateCache(selectedCurveIndex.value)
    updateSingle(selectedCurveIndex.value)
}

function toggleClosed(c) {
    c.closed = !c.closed
    requestCurveUpdate()
    updateSingle(selectedCurveIndex.value)
}

function listItemClass(index) {
    if (index == selectedCurveIndex.value) {
        return ["list-item", "selected-item"]
    } else {
        return ["list-item"]
    }
}

function deletePolyline(index) {
    deleteItems(index)
    project.value.curves = project.value.curves.filter((p, i) => i !== index);
    curvesCache = curvesCache.filter((p, i) => i !== index);
    selectedCurveIndex.value = -1
    unselect()
}

function deleteSelectedPolyline() {
    if (isCurveSelected.value) {
        deletePolyline(selectedCurveIndex.value)
    }
}

function unselect() {
    const oldIndex = selectedCurveIndex.value
    selectedCurveIndex.value = -1
    drawMode.value = false
    if (oldIndex != -1) {
        updateSingle(oldIndex)
    }
}

function selectPolyline(index) {
    const oldIndex = selectedCurveIndex.value
    selectedCurveIndex.value = index
    updateSingle(selectedCurveIndex.value)
    if (oldIndex != -1) {
        updateSingle(oldIndex)
    }
}

function getSelectedColorMap() {
    return project.value.colorMaps[project.value.settings.selectedColorMapIndex]
}

function getPreparedColorMap() {
    const colorMap = getSelectedColorMap()
    const colorItemsReverse = colorMap.items.slice().reverse();
    const colors = colorItemsReverse.map((c) => c.color)
    const limits = colorItemsReverse.map((c) => c.limit).slice(0, -1)
    const factors = colorMap.items.map((c, i) => Math.pow(1.15, i)).reverse()
    return { colors, limits, factors }
}

function update() {
    const { colors, limits, factors } = getPreparedColorMap()
    for (let i = 0; i < project.value.curves.length; i++) {
        updateCurve(i, colors, limits, factors)
    }
}

function updateSingle(index) {
    const { colors, limits, factors } = getPreparedColorMap()
    updateCurve(index, colors, limits, factors)
}

function updateCurve(index, colors, limits, factors) {
    deleteItems(index)
    drawItems(index, colors, limits, factors)
    numUpdates.value++
}

function deleteItems(index) {
    for (let layer of curvesCache[index].layers) {
        map.removeLayer(layer)
    }
    curvesCache[index].layers = []
}

function drawItems(polyIndex, colors, limits, factors) {
    const p = project.value.curves[polyIndex]
    const cc = curvesCache[polyIndex]
    drawSplineColorMap(cc, polyIndex, colors, limits, factors)
    if (polyIndex == selectedCurveIndex.value) {
        drawControlLine(p, polyIndex)
        drawPoints(cc, polyIndex)
    }
}

function drawPoints(curve, curveIndex) {
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

function drawSplineColorMap(p, curveIndex, colors, limits, factors) {
    const spline = p.spline
    if (spline.data) {
        const lat = spline.data.lat
        const lon = spline.data.lon
        const speeds = spline.data.speed
        let current = [[lat[0], lon[0]]]
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

function getColorIndex(value, limits, guessIndex) {
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

function flushCurve(coordinates, color, factor, index) {
    const options = {
        color: color,
        weight: 4 * factor,
        lineCap: 'butt',
        bubblingMouseEvents: false,
    }
    const line = L.polyline(coordinates, options)
    map.addLayer(line)
    line.on("click", () => selectPolyline(index))
    curvesCache[index].layers.push(line)
}

function drawControlLine(currentPolyline, index) {
    const cl = 'control-line selected-line'
    const points = currentPolyline.controlPoints
    const closed = currentPolyline.closed
    if (points.length > 1) {
        const coordinates = points.map(p => [p.lat, p.lon])
        const line = L.polyline(coordinates, {
            className: cl,
            bubblingMouseEvents: false,
        })
        line.on("click", (e) => lineClick(e, index))
        map.addLayer(line)
        curvesCache[index].layers.push(line)
    }
    if (points.length > 2 && closed) {
        const latlng = (p) => [p.lat, p.lon]
        const coordinates = [latlng(points[points.length - 1]), latlng(points[0])]
        const line = L.polyline(coordinates, {
            className: cl + ' thin-line',
            bubblingMouseEvents: false,
        })
        map.addLayer(line)
        curvesCache[index].layers.push(line)
    }
}

function lineClick(e, index) {
    addIntermediatePoint(index, e.latlng)
    requestCurveUpdate()
}

function addIntermediatePoint(polyIndex, latlng) {
    const poly = project.value.curves[polyIndex]
    // Find point in polyline after which point should be inserted
    let insertIndex = 0
    let minDistance = Infinity
    const p = latLonToXY({ lat: latlng.lat, lon: latlng.lng })
    for (let i = 0; i < poly.controlPoints.length - 1; i++) {
        const p1 = latLonToXY(poly.controlPoints[i])
        const p2 = latLonToXY(poly.controlPoints[i + 1])
        const d = pointSegmentDistance(p1, p2, p)
        if (d < minDistance) {
            minDistance = d
            insertIndex = i
        }
    }
    insertPoint(latlng.lat, latlng.lng, insertIndex + 1)
}

function moveableMarker(map, marker, index) {
    function trackCursor(e) {
        marker.setLatLng(e.latlng)
        selectedCurve.value.controlPoints[index] = {lat: e.latlng.lat, lon: e.latlng.lng}
        updateSingle(selectedCurveIndex.value)
        requestCurveUpdate()
    }
    let dragStartLatLng

    function dragEnd() {
        map.dragging.enable()
        map.off("mousemove", trackCursor)
        if (marker.getLatLng() == dragStartLatLng) {
            // marker was not moved -> delete
            dragStartLatLng = undefined
            deletePoint(index)
            requestCurveUpdate()
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

function deletePoint(index) {
    const points = selectedCurve.value.controlPoints
    points.splice(index, 1)
    updateCache(selectedCurveIndex.value)
    if (points.length == 0) {
        deletePolyline(selectedCurveIndex.value)
    } else {
        updateSingle(selectedCurveIndex.value)
    }
}

function updateCache(curveIndex) {
    // re-compute points of given curve
    const f = (pt, i) => newPoint(pt.lat, pt.lon, i)
    curvesCache[curveIndex].points = project.value.curves[curveIndex].controlPoints.map(f)
}

/**
 * Calculates the minimum normal distance from a point to a line segment
 * and the normalized position of the closest point on the line segment.
 *
 * @param {Object} p1 - The first endpoint of the line segment ({x, y}).
 * @param {Object} p2 - The second endpoint of the line segment ({x, y}).
 * @param {Object} p - The point to measure distance from ({x, y}).
 * @returns {Object} An object containing:
 *   - distance {number}: The shortest distance from point p to the line segment.
 *   - t {number}: The normalized position along the line segment where
 *                 the perpendicular projection occurs (0 at p1, 1 at p2).
 *                 Values outside [0,1] indicate projections beyond the segment.
 */
function pointLineDistance(p1, p2, p) {
    // Vector from p1 to p2
    let dx = p2.x - p1.x;
    let dy = p2.y - p1.y;
    
    // Vector from p1 to p
    let px = p.x - p1.x;
    let py = p.y - p1.y;
    
    // Compute the projection scalar (normalized position on the line)
    let dotProduct = px * dx + py * dy;
    let lenSq = dx * dx + dy * dy;
    let t = dotProduct / lenSq;

    // Compute the closest point on the infinite line
    let closestX = p1.x + t * dx;
    let closestY = p1.y + t * dy;

    // Compute the minimum distance
    let distX = p.x - closestX;
    let distY = p.y - closestY;
    let distance = Math.sqrt(distX * distX + distY * distY);

    return { distance, t };
}

function pointSegmentDistance(p1, p2, p) {
    const { distance, t } = pointLineDistance(p1, p2, p)
    if (t < 0) {
        // distance to p1
        return pointDistance(p1, p)
    } else if (t > 1) {
        // distance to p2
        return pointDistance(p2, p)
    }
    return distance
}

function pointDistance(p1, p2) {
    let dx = p2.x - p1.x;
    let dy = p2.y - p1.y;
    return Math.sqrt(dx * dx + dy * dy)
}

function latLonToXY(p) {
    // this approximation (although wrong) is sufficient for finding the closest point
    return { x: p.lon, y: p.lat }
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
            await updateSpline(project.value.curves[index], c)
            indicesUdated.push(index)
        }
    }
    for (let index of indicesUdated) {
        updateSingle(index)
    }
    updating = false
}

async function updateSpline(p, c) {
    // load spline data via API
    if (p.controlPoints.length >= 2) {
        c.spline.data = await loadSpline(p)
    } else {
        c.spline.data = null
    }
    c.spline.id = c.spline.requestedId
}

async function loadSpline(p) {
    const coordinates = p.controlPoints
    const data = {
        control: {
            lat: coordinates.map((c) => c.lat),
            lon: coordinates.map((c) => c.lon),
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

function setColormap(e) {
    project.value.settings.selectedColorMapIndex = parseInt(e.target.value)
    update()
}

function requestSave() {
    saveIdRequest++;
}

function saveLocalStorage() {
    // save project to local storage
    if (saveIdRequest == saveId) {
        return
    }
    localStorage.setItem("project", JSON.stringify(project.value))
    saveId = saveIdRequest
}

function loadLocalStorage() {
    // load project from local storage (if any was saved before)
    const s = localStorage.getItem("project")
    if (s != null) {
        project.value = JSON.parse(s)
        curvesCache = project.value.curves.map((c) => {
            return {
                points: c.controlPoints.map((pt, i) => newPoint(pt.lat, pt.lon, i)),
                spline: {requestedId: 1, id: 0, data: null},
                layers: [],
            }
        })
    }
}

// Main
onMounted(() => {
    createMap()
    loadLocalStorage()
    initializeMap()
    setInterval(updateCurves, 50)
    setInterval(saveLocalStorage, 1000)
})

</script>

<style>
html, body {
    font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
        Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    margin: 0;
}

h2 {
    margin-bottom: 0.5rem;
    margin-top: 0;
}
h4 {
    margin-bottom: 0.5rem;
    margin-top: 1rem;
}
p {
    font-size: 90%;
    margin-top: 0;
    margin-bottom: 0.5rem;
}

.map-app {
    display: flex;
    height: 100vh;
    margin: 0;
}

.sidebar {
    width: 300px;
    background-color: #f4f4f4;
    padding: 0px 10px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
}

.mt-3 {
    margin-top: 1rem;
}

#map {
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

.sidebar-text {
    padding: 0.5rem 0.5rem;
}
.polyline-list {
    flex-grow: 1;
}
.list-item {
    padding: 0.5rem 0.75rem;
    border-radius: 0.5rem;
    margin-bottom: 0.25rem;
    display: flex;
    justify-content: space-between;
    height: 22px;
}
.list-item:hover {
    background-color: #e3e3e3;
    cursor: pointer;
}

.selected-item {
    color: white;
    background-color: rgb(76, 0, 255);
}
.selected-item:hover {
    background-color: rgb(76, 0, 255);
}

.no-lines-placeholder {
    padding: 0rem 0.5rem;
}

.curve {
    stroke: black;
    stroke-width: 5px;
}

code {
    background-color: black;
    padding: 0.2rem;
    border-radius: 0.4rem;
    color: white;
}

.curve-props {
    display: flex;
    flex-wrap: wrap;
}

.curve-props div {
    width: 50%;
}

.legend {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}

.legend-item {
    width: 25%;
    display: flex;
    height: 1.5rem;
}
.legend-color {
    width: 15px;
    height: 15px;
    margin-top: 2px;
    margin-right: 0.25rem;
}

.btn-draw {
    margin-top: 0.25rem;
    width: 100%;
    min-width: 100%;
    height: 40px;
    background-color: green;
    border: black solid 0px;
    color: white;
    border-radius: 0.5rem;
    font-size: 100%;
    cursor: pointer;
}

.btn-draw:hover {
    opacity: 0.9;
}

/* Grey map
.leaflet-tile-pane {
    -webkit-filter: grayscale(100%);
    filter: grayscale(100%);
}
*/

</style>
