<template>
  <div class="space-y-4">
    <!-- Tanlangan matnlar -->
    <div v-if="modelValue.length" class="flex flex-wrap gap-2">
      <span
        v-for="(t, i) in modelValue"
        :key="`${i}-${t}`"
        class="inline-flex items-center gap-2 rounded-full border border-accent/40 bg-accent/10 px-3 py-1.5 text-sm text-white slide-down"
      >
        <span class="max-w-[46ch] truncate">{{ t }}</span>
        <button
          type="button"
          class="grid size-5 place-items-center rounded-full bg-white/10 text-xs text-white/70 transition hover:bg-red-400/30 hover:text-white"
          :aria-label="`O'chirish: ${t}`"
          @click="remove(i)"
        >
          ✕
        </button>
      </span>
    </div>
    <p v-else class="text-sm text-white/45">
      Hozircha matn yo'q — quyidagi tayyor matnlarni tanlang yoki o'zingiz yozing.
    </p>

    <!-- Qo'shish -->
    <form class="flex gap-2" @submit.prevent="add">
      <input
        v-model="draft"
        class="field"
        type="text"
        maxlength="160"
        :placeholder="`O'zingiz yozing... (${modelValue.length}/${max})`"
        :disabled="modelValue.length >= max"
      />
      <button class="btn btn-ghost shrink-0" type="submit" :disabled="!draft.trim() || modelValue.length >= max">
        + Qo'shish
      </button>
    </form>

    <!-- Tayyor (default) matnlar -->
    <div>
      <span class="lbl">Tayyor matnlar — bosing, qo'shiladi</span>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="t in availableDefaults"
          :key="t"
          type="button"
          class="chip"
          :disabled="modelValue.length >= max"
          @click="addDefault(t)"
        >
          + {{ t }}
        </button>
        <span v-if="!availableDefaults.length" class="inline-flex items-center gap-1.5 text-sm text-white/40">
          <AppIcon name="ph:sparkle" /> Barcha tayyor matnlar tanlandi
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppIcon from './AppIcon.vue'
import { DEFAULT_TEXTS, MAX_TEXTS } from '../data/catalog.js'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  max: { type: Number, default: MAX_TEXTS },
  // Bayram bo'yicha tayyor matnlar — berilsa, umumiy ro'yxat o'rniga shu ishlatiladi
  defaults: { type: Array, default: null },
})
const emit = defineEmits(['update:modelValue'])

const draft = ref('')

const defaultPool = computed(() =>
  Array.isArray(props.defaults) && props.defaults.length ? props.defaults : DEFAULT_TEXTS,
)

const availableDefaults = computed(() => defaultPool.value.filter((t) => !props.modelValue.includes(t)))

function add() {
  const v = draft.value.trim()
  if (!v || props.modelValue.length >= props.max) return
  emit('update:modelValue', [...props.modelValue, v])
  draft.value = ''
}

function addDefault(t) {
  if (props.modelValue.length >= props.max) return
  emit('update:modelValue', [...props.modelValue, t])
}

function remove(i) {
  const next = [...props.modelValue]
  next.splice(i, 1)
  emit('update:modelValue', next)
}
</script>
