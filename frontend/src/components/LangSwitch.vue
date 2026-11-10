<template>
  <div class="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 p-1" role="group" aria-label="Til">
    <button
      v-for="l in LOCALES"
      :key="l"
      type="button"
      class="rounded-full px-2.5 py-1 text-[11px] font-semibold tracking-wider transition"
      :class="locale === l ? 'bg-accent text-ink' : 'text-white/55 hover:text-white'"
      :aria-pressed="locale === l"
      @click="setLocale(l)"
    >
      {{ l.toUpperCase() }}
    </button>
  </div>
</template>

<script setup>
import { useI18n } from '../i18n/index.js'

const { locale, setLocale, LOCALES } = useI18n()
</script>
