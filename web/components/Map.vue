<template>
    <div class="map-app"
        @keyup.esc="unselect"
        @keyup.delete="deleteSelectedPolyline"
        @keyup="handleKeyboardEvent"
    >
        <Navbar @button-click="handleNavbarButtonClick"/>
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
                <template v-if="projectEditMode">
                    <div class="d-flex align-items-center justify-content-between">
                        <h5 class="mt-2">Project</h5>
                        <button type="button" class="btn btn-sm btn-success"
                        @click="toggleProjectEditMode">Done</button>
                    </div>
                    <form submit.prevent>
                        <input type="text" v-model="project.info.name"
                            class="form-control mb-1" @keyup.stop placeholder="Name">
                        <input type="text" v-model="project.info.author"
                            class="form-control mb-1" @keyup.stop placeholder="Author">
                        <textarea type="text" v-model="project.info.description" rows="3"
                            class="form-control mb-1" @keyup.stop placeholder="Description">
                        </textarea>
                    </form>
                </template>
                <template v-else>
                    <div class="d-flex align-items-baseline justify-content-between">
                        <div class="mt-2 mb-2">
                            <h5 style="display: inline;">{{ projectNameDisplay }}</h5>
                            <span class="author text-muted small">{{ authorDisplay }}</span>
                        </div>
                        <a href="#" class="small" @click="toggleProjectEditMode">Edit</a>
                    </div>
                    <p v-if="descriptionDisplay" class="description text-muted small">
                        {{ descriptionDisplay }}
                    </p>
                </template>
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
                        <div class="curve-name">{{ `${c.name} (${c.controlPoints.length} points)` }}</div>
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
    <Modal id="confirmOpenModal" v-model="openProjectModalOpen">
        Opening a file will delete the current project's content.
        <Alert type="danger">All unsaved changes in this project will be lost.</Alert>
        <template v-slot:title>
            Open file
        </template>
        <template v-slot:footer>
            <button type="button" class="btn btn-danger"
            @click="doOpenFile">Delete and open project</button>
        </template>
    </Modal>
    <Modal id="confirmResetModal" v-model="resetProjectModalOpen">
        This will delete the project's content and reset it to a blank project.
        Are you sure?
        <Alert type="danger">All unsaved changes in this project will be lost.</Alert>
        <template v-slot:title>
            Reset project
        </template>
        <template v-slot:footer>
            <button type="button" class="btn btn-danger"
            @click="doReset">Delete project content</button>
        </template>
    </Modal>
</template>

<script setup lang="ts">

import type { Project } from "~/types"
import { getColorMaps } from "~/utils/themes"

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

function getDefaultProject() {
    return {
        info: {
            name: "",
            description: "",
            author: "",
        },
        curves: [],
        colorMaps: getColorMaps(),
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
    }
}

const project = ref<Project>(getDefaultProject())

let saveIdRequest = 0
let saveId = 0
let openProjectModalOpen = ref(false)
let resetProjectModalOpen = ref(false)

watch(project, requestSave, {deep: true})

const properties = ref<string[]>([])

const projectEditMode = ref<boolean>(false)

const projectNameDisplay = computed(() => {
    if (project.value.info.name) {
        return project.value.info.name
    } else {
        return "Project"
    }
})

const authorDisplay = computed(() => {
    if (project.value.info.author) {
        return " by " + project.value.info.author
    } else {
        return ""
    }
})

const descriptionDisplay = computed(() => {
    if (project.value.info.description) {
        return project.value.info.description
    } else {
        return "No description."
    }
})

function toggleProjectEditMode() {
    projectEditMode.value = !projectEditMode.value
}

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

function handleNavbarButtonClick(button: "open" | "save" | "publish" | "reset") {
    const functions = {
        "open": openProjectFile,
        "save": saveProjectFile,
        "publish": publishProject,
        "reset": resetProject,
    }
    functions[button]()
}

async function saveProjectFile() {
    const hash = await hashProject()
    const pretty = JSON.stringify(project.value, null, 4)
    const filename = projectNameDisplay.value + ".json"
    downloadFile(filename, pretty)
    localStorage.setItem("saved-project-hash", hash)
}

async function hashProject(): Promise<string> {
    return await sha256(encodeUtf8(JSON.stringify(project.value)))
}

function encodeUtf8(s: string): Uint8Array {
    const encoder = new TextEncoder() // UTF-8
    return encoder.encode(s)
}

async function sha256(uint8Array: Uint8Array): Promise<string> {
    const hashBuffer = await crypto.subtle.digest('SHA-256', uint8Array);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

async function hasUnsavedChanges() {
    if (isEmpytProject()) {
        return false
    }
    const h = await hashProject()
    const hSaved = localStorage.getItem("saved-project-hash")
    if (h == hSaved) {
        return false
    }
    return true
}

function isEmpytProject() {
    const p: any = { ...project.value }
    const defaultProject: any = getDefaultProject()
    const excludeKeys = ["settings"]
    for (const key of excludeKeys) {
        delete p[key]
        delete defaultProject[key]
    }
    if (JSON.stringify(p) == JSON.stringify(defaultProject)) {
        return true
    }
    return false
}

async function openProjectFile() {
    if (await hasUnsavedChanges()) {
        openProjectModalOpen.value = true
    } else {
        await loadProject()
    }
}

function doOpenFile() {
    openProjectModalOpen.value = false
    loadProject()
}

async function loadProject() {
    const file = await openJsonFileDialog()
    if (!file) {
        return
    }
    try {
        const content = await readFileAsString(file)
        const p = JSON.parse(content)
        project.value = p
    } catch (error) {
        alert("Could not load the file.")
    }
}

function readFileAsString(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = () => {
      resolve(reader.result as string)
    }

    reader.onerror = () => {
      reject('Error reading file')
    }

    reader.readAsText(file, 'utf-8')
  })
}

async function openJsonFileDialog() {
    return await openFileDialog(".json")
}

function openFileDialog(filetypes: string): Promise<File | null> {
    return new Promise((resolve) => {
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = filetypes
        input.style.display = 'none'

        input.addEventListener('change', () => {
            const file = input.files ? input.files[0] : null
            document.body.removeChild(input)
            resolve(file)
        })

        input.addEventListener('cancel', () => {
            document.body.removeChild(input)
            resolve(null)
        })

        document.body.appendChild(input)
        input.click()
    })
}

function publishProject() {
    console.log('publish project')
}

function resetProject() {
    resetProjectModalOpen.value = true
}

function doReset() {
    resetProjectModalOpen.value = false
    project.value = getDefaultProject()
}

function downloadFile(filename: string, content: string) {
    const uint8Array = encodeUtf8(content)
    const blob = new Blob([uint8Array], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
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
    background-color: #0d6efd;
}
.selected-item:hover {
    background-color: #0d6efd;
}

.no-lines-placeholder {
    padding: 0rem 0rem;
    font-size: .875em;
    color: var(--bs-secondary-color) !important;
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

.curve-name {
    overflow: hidden;
    text-wrap: nowrap;
    text-overflow: ellipsis;
}

.description {
    max-height: 4rem;
    overflow-y: scroll;
    scrollbar-width: thin;
    scrollbar-color: rgba(1, 1, 1, 0.2) transparent;
}

</style>
