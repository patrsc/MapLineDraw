<template>
  <Icon :name="props.name" :class="className" />
</template>

<script setup lang="ts">
const props = defineProps({
  name: {type: String, default: ""},
  class: {type: String, default: ""},
})
const className = computed(() => {
  return props.class + " vertical-fix"
})
</script>

<style scoped>
.vertical-fix {
  vertical-align: -.125em;
}
.small-fix {
  vertical-align: -.05em;
}
</style>
