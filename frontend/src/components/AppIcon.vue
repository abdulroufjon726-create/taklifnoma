<template>
  <svg
    v-if="icon"
    class="icn"
    :viewBox="viewBox"
    :style="{ width: size, height: size }"
    fill="currentColor"
    aria-hidden="true"
    v-html="icon.b"
  ></svg>
</template>

<script setup>
import { computed } from 'vue'
import icons from '../data/icons.json'

const props = defineProps({
  // Iconify nomi: 'ph:cake', 'mdi:sheep', ...
  name: { type: String, required: true },
  // CSS uzunlik — em (matn ichida) yoki px/rem
  size: { type: [String, Number], default: '1.15em' },
})

const icon = computed(() => icons[props.name] || null)
const viewBox = computed(() => (icon.value ? `0 0 ${icon.value.w} ${icon.value.h}` : '0 0 24 24'))
</script>
