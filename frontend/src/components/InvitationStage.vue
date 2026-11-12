<template>
  <div class="stage" :class="{ 'stage-hold': paused }" :style="themeStyle">
    <!-- Fon -->
    <div class="amb amb-orbs"></div>
    <div
      v-for="a in ambientIds"
      :key="a"
      class="amb"
      :class="`amb-${a}`"
    ></div>

    <!-- Harakatli effektlar (bitta canvas — burst ham shu yerda) -->
    <ParticleCanvas :effects="canvasEffects" :palette="theme.palette" :paused="paused" />

    <!-- Kontent -->
    <div class="stage-content" :class="cardClass">
      <p class="st-salute" :style="fontStyle('salute', 'var(--font-script)')">
        <AnimatedText :text="data.to_name" :anim="data.text_anim" :delay="120" :active="!paused" />
      </p>

      <h1 class="st-names" :style="fontStyle('names', 'var(--font-display)')">
        <AnimatedText :text="fullName" :anim="data.text_anim" :delay="320" :active="!paused" />
      </h1>

      <div class="st-divider">❦</div>

      <p class="st-from" :style="fontStyle('from', 'var(--font-body)')">
        <AnimatedText :text="`— ${data.from_name} —`" :anim="data.text_anim" :delay="520" :active="!paused" />
      </p>

      <div v-if="texts.length" class="st-texts">
        <AnimatedText
          v-for="(t, i) in texts"
          :key="`${i}-${t}`"
          class="st-text"
          tag="p"
          :text="t"
          :anim="data.text_anim"
          :delay="650 + i * 260"
          :active="!paused"
          :style="textFontStyle(i)"
        />
      </div>

      <div class="st-when">
        <p class="st-date">
          <AnimatedText :text="dateLabel" :anim="data.text_anim" :delay="1000" :active="!paused" />
        </p>
        <button
          v-if="hasPoint"
          type="button"
          class="st-place st-place-btn"
          @click="emit('place-route')"
        >
          <AppIcon name="ph:map-pin" /> {{ data.place || t('map.venue') }}
        </button>
        <p v-else-if="data.place" class="st-place"><AppIcon name="ph:map-pin" /> {{ data.place }}</p>
      </div>

      <Countdown :target="data.event_at" @finish="celebrate" />

      <p v-if="showCode" class="st-foot">{{ t('stage.codeFoot') }}{{ pretty }}</p>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, onBeforeUnmount } from 'vue'
import ParticleCanvas from './ParticleCanvas.vue'
import AppIcon from './AppIcon.vue'
import Countdown from './Countdown.vue'
import AnimatedText from './AnimatedText.vue'
import { themeById, prettyCode, fontStack } from '../data/catalog.js'
import { useI18n, formatDate } from '../i18n/index.js'

const { t } = useI18n()

const props = defineProps({
  data: { type: Object, required: true },
  /* Konvert pardazi ochilguncha taklifnoma animatsiyalari (CSS + canvas)
     pauzada turadi — keyin qayta mount qilmasdan davom etadi. */
  paused: { type: Boolean, default: false },
})

const emit = defineEmits(['place-route'])

const hasPoint = computed(
  () => typeof props.data.place_lat === 'number' && typeof props.data.place_lng === 'number',
)

const burst = ref(false)

const theme = computed(() => themeById(props.data.theme))

const themeStyle = computed(() => {
  const t = theme.value
  return {
    '--bg1': t.bg1,
    '--bg2': t.bg2,
    '--bg3': t.bg3,
    '--accent': t.accent,
    '--accent2': t.accent2,
    '--txt': t.txt,
    '--muted': t.muted,
  }
})

const ambientIds = computed(() => (props.data.ambient_effects || []).filter((a) => typeof a === 'string'))
const texts = computed(() => (props.data.texts || []).slice(0, 6))

/* Har bir matn uchun alohida shrift (fonts JSON) */
const chosenFonts = computed(() => props.data.fonts || {})

function fontStyle(key, fallback) {
  const stack = fontStack(chosenFonts.value[key])
  return { fontFamily: stack || fallback }
}

function textFontStyle(index) {
  const stack = fontStack((chosenFonts.value.texts || [])[index])
  return stack ? { fontFamily: stack } : {}
}

/* Bitta canvas: asosiy effektlar + bayram boshlanganda qo'shimcha zarba.
   Ilgari ikkinchi canvas ochilardi — ikki RAF loop va ikki marta to'liq
   clearRect. Endi hammasi bitta loopda, ko'rinishi bir xil. */
const canvasEffects = computed(() => {
  const base = (props.data.particle_effects || []).filter((e) => typeof e === 'string')
  if (!burst.value) return base
  return [...new Set([...base, 'confetti', 'fireworks'])]
})

const fullName = computed(
  () =>
    [props.data.first_name, props.data.last_name].filter(Boolean).join(' ') || t('stage.fallbackName'),
)

const dateLabel = computed(() => formatDate(props.data.event_at))
const pretty = computed(() => prettyCode(props.data.code))
// Builder'dagi jonli ko'rinishda "PREV-IEW" kabi soxta kod chiqmasin
const showCode = computed(() => !!props.data.code && props.data.code !== 'PREVIEW')

const cardClass = computed(() => `enter-${props.data.card_anim || 'scaleIn'}`)

let burstTimer = null

function celebrate() {
  // Konvert pardazi ochilmagan bo'lsa — keyin ko'rinmaydigan zarba bermaymiz
  if (props.paused) return
  burst.value = true
  clearTimeout(burstTimer)
  burstTimer = setTimeout(() => {
    burst.value = false
    burstTimer = null
  }, 14000)
}

onBeforeUnmount(() => {
  clearTimeout(burstTimer)
  burstTimer = null
})
</script>
