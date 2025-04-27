<template>
    <div class="map-app"
        @keyup.esc="unselect"
        @keyup.delete="deleteSelectedPolyline"
        @keyup="handleKeyboardEvent"
    >
        <Navbar />
        <div class="map-main">
        <div class="sidebar" @click="unselect">
            <div class="sidebar-text">
                <p class="text-muted small mt-2 mb-2 help-text">
                    <template v-if="!drawMode">
                        <span v-if="isCurveSelected">
                            Move points by dragging. Delete point by clicking.
                            Add intermediate points by clicking on control line.
                        </span>
                        <span v-else>
                            Sketch corridors of railway lines or roads on an interactive map.<br>
                            Free and open source.
                            <a href="https://github.com/patrsc/MapLineDraw" target="_blank"
                            >View on GitHub</a>
                        </span>
                    </template>
                    <span v-else>
                        Click on different map positions to draw curve by adding points.<br>
                        Press <kbd>d</kbd> to finish or click Finish.
                    </span>
                </p>
                <div class="d-flex align-items-center justify-content-between">
                    <h5 class="mt-2">Curves</h5>
                    <button class="btn btn-sm btn-primary"
                    @click.stop="toggleDrawMode"
                    >{{ btnDrawText }}</button>
                </div>
            </div>
            <div class="polyline-list">
                <div v-if="project.curves.length == 0" class="no-lines-placeholder">
                    No curves yet.
                </div>
                <template v-for="(c, index) in project.curves">
                    <div :class="listItemClass(index)" @click.stop="selectPolyline(index)">
                        <div>{{ `${c.name} (${c.controlPoints.length} points)` }}</div>
                        <div v-if="index == selectedCurveIndex" class="d-flex gap-1">
                            <button class="btn btn-light btn-sm"
                                @click.stop="toggleClosed(index)"
                            >
                                {{ (c.closed) ? "Open" : "Close" }}
                            </button>
                            <button class="btn btn-danger btn-sm"
                                @click.stop="deleteSelectedPolyline"
                            ><Ico name="fa6-solid:trash"/></button>
                        </div>
                    </div>
                </template>
            </div>
            <div class="sidebar-text">
                <div class="curve-props" v-if="isCurveSelected" @click.stop="noUnselect">
                    <h5 style="width: 100%">Curve properties</h5>
                    <input type="text" v-model="project.curves[selectedCurveIndex].name"
                        class="form-control mb-1" @keyup.stop placeholder="Curve name">
                    <div v-for="text in properties" class="px-1 small">{{ text }}</div>
                </div>
                <h5 class="mt-3">Legend</h5>
                <select class="form-select"
                    @change="setColormap" @click.stop
                    :value="project.settings.selectedColorMapIndex"
                >
                    <option v-for="(c, index) in project.colorMaps" :value="index">
                        {{ c.name }}
                    </option>
                </select>
                <div class="legend mt-2">
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
        return "Finish"
    } else {
        if (!isCurveSelected.value) {
            return "Draw new"
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

function noUnselect() {
    // nothing to do
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
    console.log(e)
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
.map-app {
    display: flex;
    height: 100vh;
    flex-direction: column;
}
.map-main {
    display: flex;
    flex: 1;
    overflow-y: auto;
}

.sidebar {
    width: 300px;
    background-color: #f4f4f4;
    padding: 0px 0.25rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
}

.sidebar-text {
    padding: 0.5rem 0.5rem;
}
.polyline-list {
    flex-grow: 1;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: rgba(1, 1, 1, 0.2) transparent;
    padding: 0rem 0.5rem;
}
.list-item {
    padding: 0.5rem 0.75rem;
    border-radius: 0.5rem;
    margin-bottom: 0.25rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 47px;
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

.help-text {
    height: 63px;
}

</style>
