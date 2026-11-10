<template>
  <component :is="tag" :class="rootClass" :style="{ animationDelay: cssDelay }">
    <!-- Harf-bahf sakratish -->
    <template v-if="mode === 'letters'">
      <span
        v-for="(ch, i) in chars"
        :key="i"
        class="ltr"
        :style="{ animationDelay: delay / 1000 + i * 0.035 + 's' }"
        >{{ ch === ' ' ? '\u00A0' : ch }}</span
      >
    </template>
    <!-- Chop etiluvchi (typewriter) -->
    <template v-else-if="mode === 'type'">{{ typed }}<span v-if="!typeDone" class="caret"></span></template>
    <!-- Oddiy animatsiya -->
    <template v-else>{{ text }}</template>
  </component>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  text: { type: String, default: '' },
  anim: { type: String, default: 'fadeUp' },
  delay: { type: Number, default: 0 },
  tag: { type: String, default: 'span' },
  /* Konvert pardazi ochilmaguncha typewriter ham kutishi kerak — aks holda
     matn parda ortida yozilib bo'lib, ko'rinadigan paytda effekt yo'qoladi. */
  active: { type: Boolean, default: true },
})

const typed = ref('')
const typeDone = ref(true)
let typeTimer = null
let startTimer = null

const mode = computed(() => {
  if (props.anim === 'bounce') return 'letters'
  if (props.anim === 'typewriter') return 'type'
  return 'class'
})

const chars = computed(() => [...props.text])
const cssDelay = computed(() => (mode.value === 'type' ? '0s' : `${props.delay}ms`))
const rootClass = computed(() => (mode.value === 'class' ? `tx-${props.anim}` : ''))

function startTypewriter() {
  stopTypewriter()
  typed.value = ''
  typeDone.value = false
  startTimer = setTimeout(() => {
    let i = 0
    typeTimer = setInterval(() => {
      i += 1
      typed.value = props.text.slice(0, i)
      if (i >= props.text.length) {
        clearInterval(typeTimer)
        typeTimer = null
        typeDone.value = true
      }
    }, 42)
  }, props.delay)
}

function stopTypewriter() {
  if (typeTimer) clearInterval(typeTimer)
  if (startTimer) clearTimeout(startTimer)
  typeTimer = null
  startTimer = null
}

onMounted(() => {
  if (props.active && mode.value === 'type') startTypewriter()
})

onBeforeUnmount(stopTypewriter)

watch(
  () => [props.text, props.anim],
  () => {
    if (props.active && mode.value === 'type') startTypewriter()
    else {
      stopTypewriter()
      typed.value = ''
      typeDone.value = true
    }
  },
)

watch(
  () => props.active,
  (on) => {
    if (mode.value !== 'type') return
    if (on) startTypewriter()
    else stopTypewriter()
  },
)
</script>
