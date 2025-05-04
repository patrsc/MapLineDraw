<template>
    <NuxtPage />
</template>

<script setup lang="ts">
useHead({
    title: 'MapLineDraw',
    meta: [
      { name: 'description', content: 'Sketch corridors of railway lines or roads on an interactive map.' },
      { property: 'og:title', content: 'MapLineDraw'},
      { property: 'og:description', content: 'Sketch corridors of railway lines or roads on an interactive map.'},
      { property: 'og:url', content: 'https://maplinedraw.com/'},
    ],
    link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg', sizes: 'any' },
        { rel: 'canonical', href: 'https://maplinedraw.com/'}
    ],
})
</script>
