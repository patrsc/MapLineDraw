<template>
    <div class="modal fade" ref="modalElement" :id="props.id" tabindex="-1"
        :aria-labelledby="labelId" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
            <div class="modal-header">
                <h1 class="modal-title fs-5" :id="labelId">
                    <slot name="title"></slot>
                </h1>
                <button type="button" class="btn-close"
                    data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <slot></slot>
            </div>
            <div v-if="!nofooter" class="modal-footer">
                <button type="button" class="btn btn-secondary"
                    data-bs-dismiss="modal">{{ cancelText ?? 'Cancel' }}</button>
                <slot name="footer"></slot>
            </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    id: string,
    nofooter?: boolean,
    cancelText?: string,
}
const open = defineModel<boolean>()
const emits = defineEmits(['hide', 'shown'])
const props = defineProps<Props>()
const labelId = computed(() => props.id + "Label")

import type { Modal } from 'bootstrap'

const { $bs } = useNuxtApp()

const element = useTemplateRef('modalElement')
const modal = ref(undefined as undefined | Modal)

function initModal() {
    if (!modal.value && element.value) {
        modal.value = new $bs.Modal(element.value as Element)
        element.value.addEventListener('hide.bs.modal', event => {
            emits('hide')
            open.value = false
        })
        element.value.addEventListener('shown.bs.modal', event => {
            emits('shown')
        })
    }
}

watch(element, initModal, { immediate: true })
watch(open, (to, from) => {
    if (modal.value) {
        if (to && !from) {
            modal.value.show()
        }
        if (!to && from) {
            modal.value.hide()
        }
    }
})

</script>
