<template>
    <ClientOnly fallbackTag="main">
        <Map />
        <template #fallback>
            <div class="fallback">
                <article>
                    <h1>MapLineDraw</h1>
                    <p>Sketch corridors of railway lines or roads on an interactive map.<br>
                    Free and open source.
                    <a href="https://github.com/patrsc/MapLineDraw" target="_blank">View on GitHub</a>
                    </p>
                </article>
                <footer>
                    <p>Copyright &copy; 2025 MapLineDraw.com</p>
                </footer>
            </div>
        </template>
    </ClientOnly>
</template>

<style scoped>
.fallback {
    visibility: hidden;
}
</style>
