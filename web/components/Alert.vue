<template>
    <div :class="classes" :style="props.styles">
        <div>
            <Ico :name="icon" class="me-2" />
        </div>
        <div class="flex-grow-1 pre-wrap">
            <slot></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
const props = defineProps({
    type: {type: String, default: "danger"},
    styles: {type: String, default: ""}
})
const icon = computed(() => {
    switch (props.type) {
        case "danger": case "warning":
            return "fa6-solid:triangle-exclamation"
        case "success":
            return "fa6-solid:circle-check"
        default:
            return "fa6-solid:circle-info"
    }
})
const classes = computed(() => ["alert", `alert-${props.type}`, "mt-3", "d-flex", "flex-row"])
</script>
