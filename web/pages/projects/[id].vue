<template>
    <template v-if="status == 'success' && project">
        <ClientOnly fallbackTag="main">
            <Map :public="true" :publicProjectData="project"/>
            <template #fallback>
                <div class="fallback">
                    <Navbar :public="true"/>
                    <article>
                        <h1>MapLineDraw</h1>
                        <p>Sketch corridors of railway lines or roads on an interactive map.<br>
                        Free and open source.
                        <a href="https://github.com/patrsc/MapLineDraw" target="_blank">View on GitHub</a>
                        </p>
                        <h2>{{ project.info.name || 'Project' }}</h2>
                        <span v-if="project.info.author">by {{ project.info.author }}</span>
                        <p>{{ project.info.description || 'No description.' }}</p>
                    </article>
                    <footer>
                        <p>Copyright &copy; 2025 MapLineDraw.com</p>
                    </footer>
                </div>
            </template>
        </ClientOnly>
    </template>
</template>

<script setup lang="ts">
const route = useRoute()
const id = computed(() => route.params.id)
import type { Project } from "~/types"

import { getApiUrl } from "~/utils/api"

const apiUrl = getApiUrl()

const { data: project, status, error } = await useFetch<Project | null>(() => `${apiUrl}/projects/${id.value}`)

const errorData = computed(() => {
    if (error.value) {
        let errorData = error.value.data
        if (errorData.detail?.error == "NotFoundError") {
            return { error: true, code: 404, message: `Page not found: /projects/${id.value}` }
        } else if (errorData.detail?.error == "BadRequestError") {
            return { error: true, code: 400, message: errorData.detail?.message || "Unknown error" }
        }
        return { error: true, code: 500, message: "Unexpected error" }
    }
    return { error: false, code: 200, message: "Success"}
})

if (errorData.value.error) {
    throw createError({
        statusCode: errorData.value.code,
        statusMessage: errorData.value.message,
    })
}

</script>

<style scoped>
.fallback {
    visibility: hidden;
}
</style>
