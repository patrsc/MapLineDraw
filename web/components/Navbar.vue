<template>
    <nav class="navbar navbar-expand-lg bg-dark" data-bs-theme="dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">
                <Ico name="fa6-regular:map" class="me-1"/>
                MapLineDraw
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            </ul>
            <div v-if="publicProject" class="d-flex gap-2">
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
                <button class="btn btn-light" type="button" @click="emit('button-click', 'publish')">
                    <Ico name="fa6-solid:arrow-up-from-bracket" class="me-2"/>Publish
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
const publicProject = ref(false)
</script>

<style scoped>
</style>
