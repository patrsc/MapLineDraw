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
                            <button @click.stop="toggleClosed(index)">
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
        <MapView
            ref="mapViewRef"
            :color-map="selectedColorMap"
            v-model:map-settings="project.settings.map"
            v-model:curves="project.curves"
            v-model:selected-curve-index="selectedCurveIndex"
            v-model:draw-mode="drawMode"
            @select-curve="setProperties"
        />
    </div>
</template>

<script setup lang="ts">

import type { Project } from "~/types"
import { colorMaps } from "~/utils/themes"

const selectedCurveIndex = ref(-1)
const isCurveSelected = computed(() => selectedCurveIndex.value != -1)
const selectedColorMap = computed(() => {
    return project.value.colorMaps[project.value.settings.selectedColorMapIndex]
})

let drawMode = ref(false)

const mapViewRef = useTemplateRef("mapViewRef")

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

const project = ref<Project>({
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

const properties = ref<string[]>([])

function unselect() {
    selectPolyline(-1)
}

function selectPolyline(index: number) {
    selectedCurveIndex.value = index
}

function deleteSelectedPolyline() {
    mapViewRef.value?.deleteSelectedPolyline()
}

function setProperties(p: string[]) {
    properties.value = p
}

function handleKeyboardEvent(e: KeyboardEvent) {
    if (e.key == 'd') {
        toggleDrawMode()
    }
}

function toggleDrawMode() {
    drawMode.value = !drawMode.value
}

function toggleClosed(index: number) {
    mapViewRef.value?.toggleClosed(index)
}

function listItemClass(index: number) {
    if (index == selectedCurveIndex.value) {
        return ["list-item", "selected-item"]
    } else {
        return ["list-item"]
    }
}

function setColormap(e: Event) {
    const target = e.target as HTMLSelectElement
    project.value.settings.selectedColorMapIndex = parseInt(target.value)
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
    }
}

// Main
onMounted(() => {
    loadLocalStorage()
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

</style>
