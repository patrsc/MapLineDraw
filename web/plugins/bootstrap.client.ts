import * as bootstrap from 'bootstrap';

export default defineNuxtPlugin(() => {
    return {
        provide: {
            bs: bootstrap,
        }
    }
})
