// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: '2024-11-01',
    devtools: { enabled: true },
    ssr: true,
    typescript: {
        typeCheck: true,
        strict: true,
    },
    css: [
        'bootstrap/dist/css/bootstrap.min.css',
        '~/assets/main.scss',
    ],
    modules: ['@nuxt/icon'],
    features: {
        inlineStyles: false,
    },
    icon: {
        localApiEndpoint: '/_api/_nuxt_icon'
    }
})
