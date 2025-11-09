<template>
    <ClientOnly fallbackTag="main">
        <Map />
        <template #fallback>
            <div class="fallback">
                <Navbar :public="false"/>
                <article>
                    <h1>MapLineDraw</h1>
                    <p>Sketch corridors of railway lines or roads on an interactive map. Draw smooth spline curves on real maps.
                    <NuxtLink to="about">Learn more</NuxtLink>
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
