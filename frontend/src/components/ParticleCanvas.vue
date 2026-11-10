<template>
  <canvas ref="canvasEl" class="pcanvas" aria-hidden="true"></canvas>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { createParticleEngine } from '../effects/particles.js'

const props = defineProps({
  effects: { type: Array, default: () => [] },
  palette: { type: Array, default: () => ['#ffffff'] },
  /* true bo'lsa RAF loop to'xtaydi — konvert animatsiyasi paytida
     canvas hisoblashlari asosiy oqimni band qilmasligi uchun */
  paused: { type: Boolean, default: false },
})

const canvasEl = ref(null)
let engine = null
let ro = null
let io = null
let reduceMotion = false
let mediaQuery = null
const visible = ref(true)

function syncRun() {
  if (!engine) return
  if (props.paused || !visible.value || document.hidden || reduceMotion) engine.stop()
  else engine.start()
}

function onVisibility() {
  syncRun()
}

function onMotionChange(e) {
  reduceMotion = e.matches
  syncRun()
}

onMounted(() => {
  mediaQuery = typeof matchMedia === 'function' ? matchMedia('(prefers-reduced-motion: reduce)') : null
  reduceMotion = !!(mediaQuery && mediaQuery.matches)
  if (mediaQuery) {
    if (mediaQuery.addEventListener) mediaQuery.addEventListener('change', onMotionChange)
    else if (mediaQuery.addListener) mediaQuery.addListener(onMotionChange)
  }

  engine = createParticleEngine(canvasEl.value)
  engine.setPalette(props.palette)
  engine.setEffects(props.effects)

  // Kichik containerlarda (preview) ham to'g'ri o'lcham uchun
  ro = new ResizeObserver(() => engine && engine.resize())
  ro.observe(canvasEl.value)

  // Ekrandan tashqaridagi (skroll qilingan) preview hisoblamasin
  if (typeof IntersectionObserver === 'function') {
    io = new IntersectionObserver(
      (entries) => {
        const entry = entries[0]
        if (!entry) return
        visible.value = entry.isIntersecting
        syncRun()
      },
      { rootMargin: '120px' },
    )
    io.observe(canvasEl.value)
  }

  document.addEventListener('visibilitychange', onVisibility)
  syncRun()
})

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', onVisibility)
  if (mediaQuery) {
    if (mediaQuery.removeEventListener) mediaQuery.removeEventListener('change', onMotionChange)
    else if (mediaQuery.removeListener) mediaQuery.removeListener(onMotionChange)
  }
  if (io) io.disconnect()
  if (ro) ro.disconnect()
  if (engine) engine.stop()
  engine = null
})

watch(
  () => props.effects,
  (v) => engine && engine.setEffects(v || []),
)
watch(
  () => props.palette,
  (v) => engine && engine.setPalette(v || ['#ffffff']),
)
watch(() => props.paused, syncRun)
watch(visible, syncRun)
</script>
