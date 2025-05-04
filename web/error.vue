<template>
    <div class="blankslate">
        <Logo class="mb-3"/>
        <h1 class="title">MapLineDraw</h1>
        <h2>Error {{ props.error?.statusCode }}</h2>
        <p class="text-muted">{{ props.error?.statusMessage }}</p>
        <NuxtLink to="/" class="btn btn-primary">Go back home</NuxtLink>
    </div>
</template>

<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps({
    error: Object as () => NuxtError
})
</script>

<style>
.blankslate {
    margin: 4rem;
    text-align: center;
}
.title {
    font-weight: 700;
    margin-bottom: 2rem;
}
html, body {
    background-color: #fcfcfc;
}
</style>
