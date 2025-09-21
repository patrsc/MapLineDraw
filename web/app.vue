<template>
    <NuxtPage />
</template>

<script setup lang="ts">
useHead({
    title: 'MapLineDraw',
    meta: [
      { name: 'description', content: 'Sketch corridors of railway lines or roads on an interactive map. Draw smooth spline curves on real maps.' },
      { property: 'og:title', content: 'MapLineDraw'},
      { property: 'og:description', content: 'Sketch corridors of railway lines or roads on an interactive map. Draw smooth spline curves on real maps.'},
      { property: 'og:url', content: 'https://maplinedraw.com/'},
      { property: 'og:type', content: 'website'},
    ],
    link: [
        { rel: 'icon', href: '/favicon.ico', sizes: '32x32' },
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg'},
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png'},
        { rel: 'canonical', href: 'https://maplinedraw.com/'}
    ],
})
</script>
