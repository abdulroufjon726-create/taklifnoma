<template>
  <canvas ref="canvasEl" class="pcanvas" aria-hidden="true"></canvas>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { createParticleEngine } from '../effects/particles.js'

const props = defineProps({
  effects: { type: Array, default: () => [] },
  palette: { type: Array, default: () => ['#ffffff'] },
})

const canvasEl = ref(null)
let engine = null
let ro = null

onMounted(() => {
  engine = createParticleEngine(canvasEl.value)
  engine.setPalette(props.palette)
  engine.setEffects(props.effects)
  engine.start()
  // Kichik containerlarda (preview) ham to'g'ri o'lcham uchun
  ro = new ResizeObserver(() => engine && engine.resize())
  ro.observe(canvasEl.value)
  document.addEventListener('visibilitychange', onVis)
})

function onVis() {
  if (!engine) return
  if (document.hidden) engine.stop()
  else engine.start()
}

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', onVis)
  if (ro) ro.disconnect()
  if (engine) engine.stop()
  engine = null
})

watch(
  () => props.effects,
  (v) => engine && engine.setEffects(v || []),
  { deep: true },
)
watch(
  () => props.palette,
  (v) => engine && engine.setPalette(v || ['#ffffff']),
  { deep: true },
)
</script>
