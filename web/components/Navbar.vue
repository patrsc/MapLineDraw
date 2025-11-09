<template>
    <nav class="navbar navbar-expand-lg bg-dark" data-bs-theme="dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="#" @click="emit('button-click', 'toggle-sidebar')">
                <Ico name="fa6-regular:map" class="me-1"/>
                MapLineDraw
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item">
                    <a class="nav-link active" aria-current="page" href="#">Project</a>
                </li>
                <li class="nav-item">
                    <NuxtLink to="about" class="nav-link" aria-current="page">About</NuxtLink>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="https://github.com/patrsc/MapLineDraw" target="_blank">GitHub <Ico name="fa7-solid:external-link" class="small small-fix"/></a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="https://medium.com/@patrsc/introducing-maplinedraw-draw-smooth-curves-on-real-maps-free-and-open-source-e1e6a6f9d39e" target="_blank">Article <Ico name="fa7-solid:external-link" class="small small-fix"/></a>
                </li>
            </ul>
            <div v-if="props.public" class="d-flex gap-2">
                <button class="btn btn-primary" type="button" @click="emit('button-click', 'open-public')">
                    <Ico name="fa6-regular:folder" class="me-2"/>Open this project
                </button>
                <button class="btn btn-success" type="button" @click="emit('button-click', 'save')">
                    <Ico name="fa6-solid:download" class="me-2"/>Save
                </button>
                <button class="btn btn-light" type="button" @click="emit('button-click', 'copy-link')">
                    <Ico name="fa6-solid:link" class="me-2"/>Copy link
                </button>
                <button class="btn btn-danger" type="button" @click="emit('button-click', 'close-public')">
                    <Ico name="fa6-solid:arrow-right-from-bracket" class="me-2"/>Back to your project
                </button>
            </div>
            <div v-else class="d-flex gap-2">
                <button class="btn btn-primary" type="button" @click="emit('button-click', 'open')">
                    <Ico name="fa6-regular:folder" class="me-2"/>Open
                </button>
                <button class="btn btn-success" type="button" @click="emit('button-click', 'save')">
                    <Ico name="fa6-solid:download" class="me-2"/>Save
                </button>
                <button class="btn btn-light" type="button" @click="emit('button-click', 'share')">
                    <Ico name="fa6-solid:share-from-square" class="me-2"/>Share
                </button>
                <button class="btn btn-danger" type="button" @click="emit('button-click', 'reset')">
                    <Ico name="fa6-solid:trash" class="me-2"/>Reset
                </button>
            </div>
            </div>
        </div>
    </nav>
</template>

<script setup lang="ts">
const emit = defineEmits(["button-click"])
interface Props {
    public?: boolean
}
const props = defineProps<Props>()
</script>

<style scoped>
</style>
