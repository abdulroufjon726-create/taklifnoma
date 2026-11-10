/* ==========================================================================
   Yengil i18n — vue-i18n'siz. Reaktiv locale + t() kalit bo'yicha tarjima.
   localStorage'da saqlanadi, til o'zgarganda darhol yangilanadi.
   ========================================================================== */
import { ref, computed } from 'vue'
import { dict, LOCALES } from './dict.js'

const STORAGE_KEY = 'taklifnoma:lang'

function detectLocale() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && dict[saved]) return saved
  } catch {
    /* ignore */
  }
  const nav = (navigator.language || 'uz').slice(0, 2).toLowerCase()
  if (dict[nav]) return nav
  if (nav === 'ru' || nav === 'en') return nav
  return 'uz'
}

export const locale = ref(detectLocale())

export function setLocale(l) {
  if (!dict[l]) return
  locale.value = l
  try {
    localStorage.setItem(STORAGE_KEY, l)
  } catch {
    /* ignore */
  }
}

/** Kalit bo'yicha tarjima. Topilmasa — uz'ga tushadi, oxirida kalitning o'zi. */
export function t(key) {
  const parts = String(key).split('.')
  let cur = dict[locale.value] || dict.uz
  for (const p of parts) {
    cur = cur && typeof cur === 'object' ? cur[p] : undefined
    if (cur === undefined) break
  }
  if (cur !== undefined) return cur
  let fallback = dict.uz
  for (const p of parts) {
    fallback = fallback && typeof fallback === 'object' ? fallback[p] : undefined
    if (fallback === undefined) break
  }
  return fallback !== undefined ? fallback : key
}

/** Params bilan interpolatsiya: t('tc.ph') emas — t('x', { n: 2 }) */
export function tf(key, params) {
  let s = t(key)
  if (typeof s !== 'string') return s
  for (const [k, v] of Object.entries(params || {})) {
    s = s.split(`{${k}}`).join(String(v))
  }
  return s
}

/** Sanani joriy tilga qarab formatlash */
export function formatDate(value) {
  const d = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const months = t('months')
  const weekdays = t('weekdays')
  const year = d.getFullYear()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const time = `${hh}:${mm}`
  if (locale.value === 'en') {
    return `${weekdays[d.getDay()]}, ${months[d.getMonth()]} ${d.getDate()}, ${year} · ${time}`
  }
  if (locale.value === 'ru') {
    return `${d.getDate()} ${months[d.getMonth()]} ${year} г., ${weekdays[d.getDay()]} · ${time}`
  }
  return `${d.getDate()}-${months[d.getMonth()]} ${year}-y, ${weekdays[d.getDay()]} · ${time}`
}

/** Reaktiv tarjima (template uchun qulay) */
export function useI18n() {
  const tR = (...args) => t(...args)
  const localeLabel = computed(
    () => ({ uz: 'UZ', ru: 'RU', en: 'EN' })[locale.value] || 'UZ',
  )
  return { locale, setLocale, t: tR, tf, localeLabel, LOCALES }
}
