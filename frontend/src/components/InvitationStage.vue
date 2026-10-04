<template>
  <div class="stage" :style="themeStyle">
    <!-- Fon -->
    <div class="amb amb-orbs"></div>
    <div
      v-for="a in ambientIds"
      :key="a"
      class="amb"
      :class="`amb-${a}`"
    ></div>

    <!-- Harakatli effektlar -->
    <ParticleCanvas :effects="canvasEffects" :palette="theme.palette" />

    <!-- Kontent -->
    <div class="stage-content" :class="cardClass">
      <p class="st-salute">
        <AnimatedText :text="data.to_name" :anim="data.text_anim" :delay="120" />
      </p>

      <h1 class="st-names">
        <AnimatedText :text="fullName" :anim="data.text_anim" :delay="320" />
      </h1>

      <div class="st-divider">❦</div>

      <p class="st-from">
        <AnimatedText :text="`— ${data.from_name} —`" :anim="data.text_anim" :delay="520" />
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
        />
      </div>

      <div class="st-when">
        <p class="st-date">
          <AnimatedText :text="dateLabel" :anim="data.text_anim" :delay="1000" />
        </p>
        <p v-if="data.place" class="st-place"><AppIcon name="ph:map-pin" /> {{ data.place }}</p>
      </div>

      <Countdown :target="data.event_at" @finish="celebrate" />

      <p class="st-foot">Kod · {{ pretty }}</p>
    </div>

    <!-- Tug'ilgan kun / event boshlanganda qo'shimcha zarba -->
    <template v-if="burst">
      <ParticleCanvas :effects="['confetti', 'fireworks']" :palette="theme.palette" />
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import ParticleCanvas from './ParticleCanvas.vue'
import AppIcon from './AppIcon.vue'
import Countdown from './Countdown.vue'
import AnimatedText from './AnimatedText.vue'
import { formatDateUz, themeById, prettyCode } from '../data/catalog.js'

const props = defineProps({
  data: { type: Object, required: true },
})

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
const canvasEffects = computed(() => props.data.particle_effects || [])
const texts = computed(() => (props.data.texts || []).slice(0, 6))

const fullName = computed(() =>
  [props.data.first_name, props.data.last_name].filter(Boolean).join(' ') || 'Taklifnoma',
)

const dateLabel = computed(() => formatDateUz(props.data.event_at))
const pretty = computed(() => prettyCode(props.data.code))

const cardClass = computed(() => `enter-${props.data.card_anim || 'scaleIn'}`)

function celebrate() {
  burst.value = true
  setTimeout(() => {
    burst.value = false
  }, 14000)
}
</script>
