export function getApiUrl(): string {
    let url = "https://maplinedraw.com/api"
    if (import.meta.dev) {
        url = "http://localhost:8000"
    }
    return url
}
