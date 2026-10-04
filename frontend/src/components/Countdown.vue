<template>
  <div class="cd-wrap">
    <div v-if="!finished" class="cd-grid" role="timer" aria-live="off">
      <div v-for="u in units" :key="u.key" class="cd-box">
        <span class="cd-num" :key="u.key + '-' + u.value">{{ pad(u.value) }}</span>
        <span class="cd-lbl">{{ u.label }}</span>
      </div>
    </div>
    <p v-else class="cd-done">Bayram muborak bo'lsin! ✦</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  target: { type: [String, Number, Date], required: true },
})
const emit = defineEmits(['finish', 'tick'])

const now = ref(Date.now())
const finishedOnce = ref(false)
let timer = null

const targetMs = computed(() => {
  const t = props.target instanceof Date ? props.target.getTime() : new Date(props.target).getTime()
  return Number.isNaN(t) ? 0 : t
})

const diff = computed(() => Math.max(0, targetMs.value - now.value))
const finished = computed(() => targetMs.value > 0 && diff.value <= 0)

const units = computed(() => {
  const d = diff.value
  return [
    { key: 'd', label: 'Kun', value: Math.floor(d / 86400000) },
    { key: 'h', label: 'Soat', value: Math.floor(d / 3600000) % 24 },
    { key: 'm', label: 'Daqiqa', value: Math.floor(d / 60000) % 60 },
    { key: 's', label: 'Soniya', value: Math.floor(d / 1000) % 60 },
  ]
})

const pad = (n) => String(n).padStart(2, '0')

function tick() {
  now.value = Date.now()
  emit('tick', diff.value)
  if (finished.value && !finishedOnce.value) {
    finishedOnce.value = true
    emit('finish')
  }
}

onMounted(() => {
  tick()
  timer = setInterval(tick, 250)
})
onBeforeUnmount(() => clearInterval(timer))
watch(() => props.target, tick)
</script>
