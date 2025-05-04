<template>
    <ClientOnly fallbackTag="main">
        <Map />
        <template #fallback>
            <article class="fallback">
                <h1>MapLineDraw</h1>
                <p>Sketch corridors of railway lines or roads on an interactive map.<br>
                Free and open source.
                <a href="https://github.com/patrsc/MapLineDraw" target="_blank">View on GitHub</a>
                </p>
            </article>
            <footer>
                <p>Copyright &copy; 2025 MapLineDraw.com</p>
            </footer>
        </template>
    </ClientOnly>
</template>

<style scoped>
.fallback {
    visibility: hidden;
}
</style>
