<template>
  <div class="cd-wrap">
    <div v-if="!finished" class="cd-grid" role="timer" aria-live="off">
      <div v-for="u in units" :key="u.key" class="cd-box">
        <span class="cd-num" :key="u.key + '-' + u.value">{{ pad(u.value) }}</span>
        <span class="cd-lbl">{{ u.label }}</span>
      </div>
    </div>
    <p v-else class="cd-done">{{ t('cd.done') }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useI18n } from '../i18n/index.js'

const { t } = useI18n()

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
    { key: 'd', label: t('cd.d'), value: Math.floor(d / 86400000) },
    { key: 'h', label: t('cd.h'), value: Math.floor(d / 3600000) % 24 },
    { key: 'm', label: t('cd.m'), value: Math.floor(d / 60000) % 60 },
    { key: 's', label: t('cd.s'), value: Math.floor(d / 1000) % 60 },
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

/*
 * 250ms interval o'rniga soniyaga tekislangan setTimeout: sekund har doim
 * aniq o'zgaradi, ortiqcha 4x render bo'lmaydi. Tab yashiringanda to'xtaydi.
 */
function schedule() {
  clearTimeout(timer)
  if (document.hidden) return
  const delay = 1000 - (Date.now() % 1000) + 8
  timer = setTimeout(() => {
    tick()
    schedule()
  }, delay)
}

function onVisibility() {
  if (document.hidden) {
    clearTimeout(timer)
    timer = null
  } else {
    tick()
    schedule()
  }
}

onMounted(() => {
  tick()
  schedule()
  document.addEventListener('visibilitychange', onVisibility)
})

onBeforeUnmount(() => {
  clearTimeout(timer)
  timer = null
  document.removeEventListener('visibilitychange', onVisibility)
})

watch(
  () => props.target,
  () => {
    finishedOnce.value = false
    tick()
    schedule()
  },
)
</script>
