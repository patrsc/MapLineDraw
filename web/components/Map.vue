<template>
    <div class="map-app">
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
                <button class="btn-draw" @click="toggleDrawMode">{{ btnDrawText }}</button>
                <h2 class="mt-3">Curves</h2>
            </div>
            <div id="polyline-list" class="polyline-list"></div>
            <div class="sidebar-text">
                <div id="curve-props" class="curve-props"></div>
                <h2 class="mt-3">Legend</h2>
                <select id="colormap-select"></select>
                <div id="legend"></div>
            </div>
        </div>
        <div id="map" ref="map-element"></div>
    </div>
</template>

<script setup>

import L from "leaflet"
import 'leaflet/dist/leaflet.css'

import { getColor, colorMaps } from "~/utils/themes"

let map
const selectedCurveIndex = ref(-1)
const selectedCurve = computed(() => {
    return (selectedCurveIndex.value == -1) ? null : project.value.curves[selectedCurveIndex.value]
})
const isCurveSelected = computed(() => selectedCurveIndex.value != -1)
let updating = false
let drawMode = false

const mapElement = useTemplateRef('map-element')

const btnDrawText = ref("")

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

    document.addEventListener('keyup', handleKeyboardEvent)
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
    saveLocalStorage()
}

function handleKeyboardEvent(e) {
    const key = e.key
    if (key == 'Escape') {
        unselect()
    } else if (key == 'Delete' || key == 'Backspace') {
        deleteSelectedPolyline()
    } else if (key == 'd') {
        toggleDrawMode(e)
    }
}

function toggleDrawMode(e) {
    e.stopPropagation()
    drawMode = !drawMode
    updateDrawMode()
}

function updateDrawMode() {
    if (drawMode) {
        btnDrawText.value = "Finish drawing"
        setLeafletCursor("crosshair")
    } else {
        setLeafletCursor("grab")
        if (!isCurveSelected.value) {
            btnDrawText.value = "Draw new curve"
        } else {
            btnDrawText.value = "Add points"
        }
    }
}

function setLeafletCursor(cursor) {
    for (const e of document.getElementsByClassName('leaflet-container')) {
        e.style.setProperty("cursor", cursor, "important")
    }
}

function addControlPoint(e) {
    if (!drawMode) {
        unselect()
        return
    }
    if (!isCurveSelected.value) {
        selectedCurveIndex.value = project.value.curves.length
        project.value.curves.push(newCurve("Curve"))
    }
    insertPoint(e.latlng, -1)
    requestCurveUpdate()
}

function newCurve(name) {
    return {
        name: name,
        points: [],
        closed: false,
        spline: {requestedId: 0, id: 0, data: null}
    }
}

function newPoint(lat, lng) {
    const point = L.circleMarker([lat, lng], {
        className: 'control-point',
        radius: 15,
        bubblingMouseEvents: false,
    })
    moveableMarker(map, point)
    return point
}

function insertPoint(latlng, insertIndex) {
    const { lat, lng } = latlng
    const point = newPoint(lat, lng)
    const currentPolyline = selectedCurve.value
    if (insertIndex == -1) {
        currentPolyline.points.push(point)
    } else {
        currentPolyline.points.splice(insertIndex + 1, 0, point)
    }
    update()
}

function updateSidebar() {
    updateCurveList()
    updateProperties()
}

function updateCurveList() {
    const list = document.getElementById('polyline-list')
    list.innerHTML = ''
    project.value.curves.forEach((p, index) => {
        const li = document.createElement('div')
        li.className = 'list-item'
        const t = document.createElement('div')
        t.textContent = `${p.name} (${p.points.length} points)`
        li.appendChild(t)
        li.addEventListener('click', (e) => {
            e.stopPropagation()
            selectPolyline(index)
        })
        if (index == selectedCurveIndex.value) {
            li.className += ' selected-item'
            const right = document.createElement("div")
            const btnClose = document.createElement('button')
            btnClose.innerText = (p.closed) ? "Open" : "Close"
            btnClose.addEventListener('click', (e) => {
                e.stopPropagation()
                p.closed = !p.closed
                requestCurveUpdate()
                update()
            })
            right.appendChild(btnClose)
            const btn = document.createElement('button')
            btn.innerText = "Delete"
            btn.addEventListener('click', (e) => {
                e.stopPropagation()
                deleteSelectedPolyline()
            })
            right.appendChild(btn)
            li.appendChild(right)
        }
        list.appendChild(li)
    })
    if (project.value.curves.length == 0) {
        const text = document.createElement("div")
        text.textContent = 'No curves yet.'
        text.className = "no-lines-placeholder"
        list.appendChild(text)
    }
}

function updateProperties() {
    const e = document.getElementById("curve-props")
    e.innerHTML = ""
    if (isCurveSelected.value) {
        const h = document.createElement("h2")
        h.innerText = "Properties"
        h.style = "width: 100%"
        e.appendChild(h)
        const p = project.value.curves[selectedCurveIndex.value]
        const nPoints = p.points.length
        const data = p.spline.data
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
        for (const text of texts) {
            const t = document.createElement("div")
            t.innerText = text
            e.appendChild(t)
        }
    }
}

function deletePolyline(index) {
    project.value.curves = project.value.curves.filter((p, i) => i !== index);
    unselect()
}

function deleteSelectedPolyline() {
    if (isCurveSelected.value) {
        deletePolyline(selectedCurveIndex.value)
    }
}

function unselect() {
    selectedCurveIndex.value = -1
    drawMode = false
    update()
}

function selectPolyline(index) {
    selectedCurveIndex.value = index
    update()
}

function update() {
    updateSidebar()
    updatePolylines()
    updateDrawMode()
    saveLocalStorage()
}

function updatePolylines() {
    deleteItems()
    drawItems()
}

function deleteItems() {
    map.eachLayer(layer => {
        if (layer instanceof L.Polyline || layer instanceof L.CircleMarker) {
            map.removeLayer(layer)
        }
    })
}

function getSelectedColorMap() {
    return project.value.colorMaps[project.value.settings.selectedColorMapIndex]
}

function drawItems() {
    const colorMap = getSelectedColorMap()
    project.value.curves.forEach((p, polyIndex) => {
        // drawSpline(p, polyIndex)
        drawSplineColorMap(p, polyIndex, colorMap)
        if (polyIndex == selectedCurveIndex.value) {
            drawControlLine(p, polyIndex)
            drawPoints(p)
        }
    })
}

function drawPoints(p) {
    p.points.forEach((point, pointIndex) => {
        if (pointIndex == p.points.length - 1) {
            point.options.className = 'control-point selected-point'
        } else {
            point.options.className = 'control-point'
        }
        map.addLayer(point)
    })
}

function drawSpline(p, index) {
    const spline = p.spline
    if (spline.data) {
        const coordinates = spline.data.lat.map((lat, i) => {
            return { lat: lat, lng: spline.data.lon[i] }
        })
        const options = {
            className: 'curve',
            bubblingMouseEvents: false,
        }
        const line = L.polyline(coordinates, options)
        map.addLayer(line)
        line.on("click", () => selectPolyline(index))
    }
}

function drawSplineColorMap(p, index, colorMap) {
    const spline = p.spline
    if (spline.data) {
        const coordinates = spline.data.lat.map((lat, i) => {
            return { lat: lat, lng: spline.data.lon[i] }
        })
        const speeds = spline.data.speed
        let current = [coordinates[0]]
        let prevColor = null
        let prevFactor = null
        for (let i = 1; i < speeds.length; i++) {
            const speedPrev = speeds[i - 1]
            const speed = speeds[i]
            const s = Math.min(speedPrev, speed)
            const [ color, factor ] = getColor(s, colorMap.items)
            if (prevColor === null || color == prevColor) {
                current.push(coordinates[i])
            } else {
                flushCurve(current, prevColor, prevFactor, index)
                current = [coordinates[i - 1]]
                current.push(coordinates[i])
            }
            prevColor = color
            prevFactor = factor
        }
        flushCurve(current, prevColor, prevFactor, index)
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
}

function drawControlLine(currentPolyline, index) {
    const cl = 'control-line selected-line'
    const points = currentPolyline.points
    const closed = currentPolyline.closed
    if (points.length > 1) {
        const coordinates = points.map(p => p.getLatLng())
        const line = L.polyline(coordinates, {
            className: cl,
            bubblingMouseEvents: false,
        })
        line.on("click", (e) => lineClick(e, index))
        map.addLayer(line)
    }
    if (points.length > 2 && closed) {
        const coordinates = [points[points.length - 1].getLatLng(), points[0].getLatLng()]
        const line = L.polyline(coordinates, {
            className: cl + ' thin-line',
            bubblingMouseEvents: false,
        })
        map.addLayer(line)
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
    const p = latLngToXY(latlng)
    for (let i = 0; i < poly.points.length - 1; i++) {
        const p1 = latLngToXY(poly.points[i].getLatLng())
        const p2 = latLngToXY(poly.points[i + 1].getLatLng())
        const d = pointSegmentDistance(p1, p2, p)
        if (d < minDistance) {
            minDistance = d
            insertIndex = i
        }
    }
    insertPoint(latlng, insertIndex)
}

function moveableMarker(map, marker) {
    function trackCursor(evt) {
        marker.setLatLng(evt.latlng)
        update()
        requestCurveUpdate()
    }
    let dragStartLatLng

    function dragEnd() {
        map.dragging.enable()
        map.off("mousemove", trackCursor)
        if (marker.getLatLng() == dragStartLatLng) {
            // marker was not moved -> delete
            dragStartLatLng = undefined
            deletePoint(marker)
            requestCurveUpdate()
        }
    }

    marker.on("mousedown", () => {
        dragStartLatLng = marker.getLatLng()
        map.dragging.disable()
        map.on("mousemove", trackCursor)
    })
    map.on("mouseup", dragEnd)
    map.on("mouseout", dragEnd)

    return marker
}

function deletePoint(point) {
    for (const [ polyIndex, poly ] of toRaw(project.value).curves.entries()) {
        for (const [ index, currentPoint ] of poly.points.entries()) {
            if (currentPoint === point) {
                poly.points.splice(index, 1)
                if (poly.points.length == 0) {
                    deletePolyline(polyIndex)
                } else {
                    update()
                }
                return
            }
        }
    }
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

function latLngToXY(p) {
    // TODO
    return { x: p.lng, y: p.lat }
}

function requestCurveUpdate() {
    // request update of selected curve by incrementing requestedId
    if (isCurveSelected.value) {
        project.value.curves[selectedCurveIndex.value].spline.requestedId++
    }
}

async function updateCurves() {
    // if update is currently running -> abort
    if (updating) {
        return
    }
    // check if any curve needs update
    updating = true
    let anyUpdated = false
    for (const p of project.value.curves) {
        if (p.spline.id < p.spline.requestedId) {
            // needs update
            await updateSpline(p)
            anyUpdated = true
        }
    }
    if (anyUpdated) {
        update()
    }
    updating = false
}

async function updateSpline(p) {
    // load spline data via API
    if (p.points.length >= 2) {
        p.spline.data = await loadSpline(p)
    } else {
        p.spline.data = null
    }
    p.spline.id = p.spline.requestedId
}

async function loadSpline(p) {
    const coordinates = p.points.map((p) => p.getLatLng())
    const data = {
        control: {
            lat: coordinates.map((c) => c.lat),
            lon: coordinates.map((c) => c.lng),
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

function updateLegend() {
    const e = document.getElementById('legend')
    e.innerHTML = ""
    const colorMap = getSelectedColorMap()
    for (const { color, label } of colorMap.items) {
        e.appendChild(legendItem(color, label))
    }
}

function legendItem(color, text) {
    let e = document.createElement('div')
    e.className = 'legend-item'
    let c = document.createElement('div')
    c.className = 'legend-color'
    c.style = `background-color: ${color}`
    let t = document.createElement('div')
    t.textContent = text
    e.appendChild(c)
    e.appendChild(t)
    return e
}

function initColorMapSelect() {
    let e = document.getElementById("colormap-select")
    e.addEventListener("change", setColormap)
}

function setColormap(e) {
    project.value.settings.selectedColorMapIndex = parseInt(e.target.value)
    update()
    updateLegend()
}

function updateColormapSelect() {
    let e = document.getElementById("colormap-select")
    for (const [index, colorMap] of project.value.colorMaps.entries()) {
        let option = document.createElement("option")
        option.textContent = colorMap.name
        option.value = index
        e.appendChild(option)
    }
    e.value = project.value.settings.selectedColorMapIndex
}

function saveLocalStorage() {
    // save project to local storage
    const p = projectToJson(project.value)
    localStorage.setItem("project", JSON.stringify(p))
}

function loadLocalStorage() {
    // load project from local storage (if any was saved before)
    const s = localStorage.getItem("project")
    if (s != null) {
        const p = JSON.parse(s)
        project.value = projectFromJson(p)
    }
}

function projectToJson(project) {
    const curves = project.curves.map((c) => {
        return {
            name: c.name,
            closed: c.closed,
            controlPoints: c.points.map((p) => {
                const latlng = p.getLatLng()
                return {lat: latlng.lat, lon: latlng.lng}
            })
        }
    })
    return {
        info: project.info,
        curves: curves,
        settings: project.settings,
        colorMaps: project.colorMaps,
    }
}

function projectFromJson(p) {
    const curves = p.curves.map((c) => {
        return {
            name: c.name,
            closed: c.closed,
            points: c.controlPoints.map((pt) => newPoint(pt.lat, pt.lon)),
            spline: {requestedId: 1, id: 0, data: null}
        }
    })
    return {
        info: p.info,
        curves: curves,
        settings: p.settings,
        colorMaps: p.colorMaps,
    }
}

// Main
onMounted(() => {
    createMap()
    loadLocalStorage()
    initializeMap()
    updateSidebar()
    updateLegend()
    initColorMapSelect()
    updateColormapSelect()
    updateDrawMode()
    setInterval(updateCurves, 50)
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

#legend {
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
