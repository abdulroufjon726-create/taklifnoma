<template>
  <!-- Yuklanmoqda -->
  <div v-if="status === 'loading'" class="fixed inset-0 grid h-[100dvh] place-items-center overflow-hidden bg-ink">
    <div class="page-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>
    <div class="relative flex flex-col items-center gap-5">
      <span class="spinner"></span>
      <p class="text-sm tracking-[0.3em] text-white/55 uppercase">{{ t('inv.loading') }}</p>
      <p v-if="slowLoading" class="max-w-[26ch] text-center text-xs leading-relaxed text-white/40 fade-in">
        {{ t('inv.waking') }}
      </p>
    </div>
  </div>

  <!-- Topilmadi -->
  <div v-else-if="status !== 'ok'" class="fixed inset-0 grid h-[100dvh] place-items-center overflow-hidden bg-ink px-4">
    <div class="page-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-3"></div>
      <div class="grain"></div>
    </div>
    <div class="glass card modal-in relative w-full max-w-md p-8 text-center">
      <div class="mx-auto mb-4 grid size-16 place-items-center rounded-2xl bg-white/5 text-accent ring-1 ring-white/10">
        <AppIcon name="ph:envelope-open" size="1.8rem" />
      </div>
      <h1 class="font-display text-3xl font-semibold">{{ t('inv.nfTitle') }}</h1>
      <p class="mt-3 text-sm leading-relaxed text-white/60">
        <b class="text-white/85">{{ pretty || t('inv.nfCode') }}</b>{{ t('inv.nfB') }}
      </p>
      <p v-if="status === 'error'" class="mt-2 text-xs text-red-300">{{ errorText }}</p>
      <div class="mt-6 flex flex-col gap-3">
        <RouterLink to="/enter" class="btn btn-primary w-full">{{ t('inv.enterNew') }}</RouterLink>
        <RouterLink to="/" class="btn btn-ghost w-full">{{ t('inv.create') }}</RouterLink>
      </div>
    </div>
  </div>

  <!-- Taklifnoma: to'liq ekran, skrollsiz -->
  <div v-else class="fixed inset-0 h-[100dvh] w-full overflow-hidden bg-black">
    <InvitationStage :data="invitation" :paused="!stageLive" @place-route="showRoute = true" />

    <!-- KONVERT: taklifnomadan oldin ochiladigan pardaz -->
    <div v-if="covered"
      class="absolute inset-0 z-30 flex flex-col items-center justify-center gap-7 overflow-hidden bg-ink px-5 text-center"
      :class="{ 'cover-out': openingAnim }"
      :style="{
        '--paper-scale': paperScale,
        '--paper-dx': paperDx + 'px',
        '--paper-dy': paperDy + 'px',
      }"
      role="button" tabindex="0" :aria-label="t('inv.coverBtn')"
      @click="openCover" @keydown.enter.prevent="openCover" @keydown.space.prevent="openCover">
      <div class="page-bg">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="grain"></div>
      </div>

      <div class="absolute top-4 left-4 z-10 sm:top-6 sm:left-6 cover-ui">
        <LangSwitch />
      </div>

      <!-- Konvert -->
      <span class="env-scene relative" :class="{ 'cursor-pointer': !openingAnim, 'scene-open': openingAnim }">
        <span class="env" :class="{ open: openingAnim }">
          <span class="env-back"></span>
          <span class="env-inner"></span>
          <span class="env-letter">
            <span class="env-letter-txt">
              <b class="env-letter-name">{{ invitation.first_name }}</b>
              <span v-if="paperDate" class="env-letter-date">{{ paperDate }}</span>
              <span class="env-letter-orn">❦</span>
            </span>
          </span>
          <span ref="paperEl" class="env-paper"></span>
          <span class="env-pocket"></span>
          <span class="env-flap"></span>
          <span class="env-seal">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 48 48">
              <path d="M0 0h48v48H0z" fill="none" />
              <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"
                d="M31.65 39.54c1.461 0 2.886-.203 4.227-.592A18.35 18.35 0 0 1 24.988 42.5C14.765 42.5 6.485 34.221 6.485 24s8.28-18.5 18.503-18.5c4.07 0 7.836 1.314 10.89 3.552a15.2 15.2 0 0 0-4.229-.592c-8.585 0-15.542 6.956-15.542 15.54s6.957 15.54 15.542 15.54" />
              <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"
                d="m35.832 18.003l1.756 3.557l3.927.57l-2.841 2.77l.67 3.91l-3.512-1.846l-3.512 1.846l.671-3.91l-2.841-2.77l3.927-.57z" />
            </svg>
          </span>
        </span>
      </span>
      <button class="btn btn-primary relative cover-ui" type="button" @click.stop="openCover">
        {{ t('inv.coverBtn') }}
      </button>
    </div>

    <!-- Til -->
    <div class="absolute top-4 left-4 z-20 sm:top-6 sm:left-6">
      <LangSwitch />
    </div>

    <!-- To'liq ekran (agar avtomatik kirmagan bo'lsa) -->
    <button v-if="!isFullscreen" type="button"
      class="glass absolute top-4 left-1/2 z-20 -translate-x-1/2 rounded-full px-4 py-2 text-sm font-medium text-white/85 transition hover:text-white sm:top-6"
      @click="goFullscreen">
      <AppIcon name="ph:arrows-out" /> {{ t('inv.fsBtn') }}
    </button>

    <!-- Ulashish -->
    <button type="button"
      class="glass absolute top-4 right-4 z-20 rounded-full px-4 py-2 text-sm font-medium text-white/85 transition hover:text-white sm:top-6 sm:right-6"
      @click="share">
      {{ copied ? t('inv.copied') : t('inv.share') }}
    </button>

    <!-- Boshqa taklifnomalarga o'tish -->
    <RouterLink to="/enter"
      class="glass absolute bottom-4 left-4 z-20 rounded-full px-4 py-2 text-xs tracking-widest text-white/60 uppercase transition hover:text-white sm:bottom-6 sm:left-6">
      {{ t('inv.codeBtn') }}
    </RouterLink>

    <p v-if="toast"
      class="fade-in fixed bottom-6 left-1/2 z-30 -translate-x-1/2 rounded-full bg-white/10 px-5 py-2.5 text-sm text-white backdrop-blur-md">
      {{ toast }}
    </p>

    <!-- Manzil: matn bosilganda xarita va yo'l -->
    <div
      v-if="showRoute && invitation && invitation.place_lat !== null && invitation.place_lng !== null"
      class="route-overlay"
      @click.self="showRoute = false"
    >
      <div class="route-panel">
        <RouteMap
          :lat="invitation.place_lat"
          :lng="invitation.place_lng"
          :label="invitation.place"
        />
        <button type="button" class="btn btn-ghost mt-2 w-full" @click="showRoute = false">
          {{ t('map.close') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import InvitationStage from '../components/InvitationStage.vue'
import RouteMap from '../components/RouteMap.vue'
import AppIcon from '../components/AppIcon.vue'
import LangSwitch from '../components/LangSwitch.vue'
import { fetchInvitation, getCachedInvitation, shareUrl, copyText } from '../api.js'
import { prettyCode } from '../data/catalog.js'
import { useI18n, formatDate } from '../i18n/index.js'

const { t, locale } = useI18n()

const route = useRoute()

const status = ref('loading') // loading | ok | missing | error
const invitation = ref(null)
const errorText = ref('')
const copied = ref(false)
const toast = ref('')
const showRoute = ref(false)
let toastTimer = null
const covered = ref(false) // konvert pardazi — bosilmaguncha taklifnoma yashirinadi
const openingAnim = ref(false) // konvert animatsiyasi ketmoqda
const slowLoading = ref(false) // backend uyg'onishi uzoqqa cho'zildi
const stageLive = ref(false) // taklifnoma animatsiyalari yoqilgan (pauza ochilgan)
const paperScale = ref(9) // tekis qog'oz ekranni to'ldirishi uchun masshtab
const paperDx = ref(0) // qog'oz markazini ekran markaziga surish
const paperDy = ref(0)
const paperEl = ref(null)
let openTimer = null
let liveTimer = null
let slowTimer = null

/* Konvert xoreografiyasi (CSS bilan biri-biriga mos bo'lishi shart):
   mum 0.00–0.60 · qopqoq 0.60–1.55 · qog'oz chiqishi 1.50–2.40
   · qog'oz kattalashishi 2.25–3.20 · pardaz so'nishi 3.15–3.65 */
const STAGE_LIVE_AT = 2850
const COVER_DONE_AT = 3700 // CSS coverOut 3.65s tugagachgina olib tashlaymiz

const pretty = computed(() => prettyCode(route.params.code))
// Konvert ichidagi qog'ozda yozilgan taklifnoma satri
const paperDate = computed(() => (invitation.value ? formatDate(invitation.value.event_at) : ''))

function updateTitle() {
  if (!invitation.value) return
  document.title = t('inv.docTitle')
    .replace('{name}', invitation.value.first_name)
    .replace('{code}', pretty.value)
}

function applyInvitation(data) {
  invitation.value = data
  status.value = 'ok'
  covered.value = true // har bir ochilishda avval konvert
  openingAnim.value = false
  stageLive.value = false
  clearTimeout(openTimer)
  clearTimeout(liveTimer)
  clearTimeout(slowTimer)
  slowLoading.value = false
  updateTitle()
}

async function load() {
  status.value = 'loading'
  invitation.value = null
  covered.value = false
  openingAnim.value = false
  stageLive.value = false
  clearTimeout(openTimer)
  clearTimeout(liveTimer)
  clearTimeout(slowTimer)
  slowLoading.value = false
  slowTimer = setTimeout(() => (slowLoading.value = true), 4500)

  // Kirish sahifasida tekshirilgan taklifnoma keshda bo'ladi — qayta
  // so'rovsiz, darhol konvert ochiladi (ko'rishlar soni ham ikki marta
  // oshmaydi).
  const cached = getCachedInvitation(route.params.code)
  if (cached) {
    applyInvitation(cached)
    return
  }

  try {
    applyInvitation(await fetchInvitation(route.params.code))
  } catch (e) {
    clearTimeout(slowTimer)
    slowLoading.value = false
    if (e.status === 404) status.value = 'missing'
    else {
      status.value = 'error'
      if (e.status === 429) errorText.value = t('inv.err429')
      else if (e.code === 'timeout' || e.code === 'network') errorText.value = t('inv.errTimeout')
      else errorText.value = e.message || t('inv.errNet')
    }
  }
}

/* Tekis qog'oz ekranni to'liq qoplashi uchun masshtab va siljishni
   o'lchaymiz: qog'oz markazi ekran markaziga tushiriladi, keyin
   o'sha markaz atrofida kattalashtiriladi. */
function measurePaper() {
  const el = paperEl.value
  if (!el) return
  const prev = el.style.transform
  el.style.transform = 'none' // o'lchov uchun transformni o'chiramiz
  const r = el.getBoundingClientRect()
  el.style.transform = prev
  if (r.width < 10 || r.height < 10) return
  const vw = window.innerWidth
  const vh = window.innerHeight
  const need = Math.max(vw / r.width, vh / r.height) * 1.08 // 8% zaxira
  paperScale.value = Math.min(Math.max(need, 3), 30)
  paperDx.value = Math.round(vw / 2 - (r.left + r.width / 2))
  paperDy.value = Math.round(vh / 2 - (r.top + r.height / 2))
}

/* Konvert DARHOL ochiladi: fullscreen yoki viewport o'zgarishini kutmaymiz
   (ilgari bosishdan keyin ~1s hech narsa ko'rinmasdi — "qotdi" taassuroti).
   Fullscreen alohida, bloklamaydigan chaqiruv sifatida ketadi. */
function openCover() {
  if (!covered.value || openingAnim.value) return
  measurePaper()
  startOpening()
  goFullscreen()
}

function startOpening() {
  openingAnim.value = true
  clearTimeout(openTimer)
  clearTimeout(liveTimer)
  // Qog'oz ekranni to'ldirib, yo'qolib borayotganda taklifnoma
  // konvert ichidan "chiqib kelayotgandek" animatsiya bilan jonlanadi
  liveTimer = setTimeout(() => {
    stageLive.value = true
  }, STAGE_LIVE_AT)
  openTimer = setTimeout(() => {
    covered.value = false
    openingAnim.value = false
  }, COVER_DONE_AT)
}

/* ---- To'liq ekran (F11 kabi) ---------------------------------------- */
const isFullscreen = ref(false)

function goFullscreen() {
  const el = document.documentElement
  if (!el.requestFullscreen || document.fullscreenElement) return
  try {
    const p = el.requestFullscreen({ navigationUI: 'hide' })
    if (p && typeof p.catch === 'function') p.catch(() => { })
  } catch {
    /* brauzer ruxsat bermaydi — tugma qoladi */
  }
}

function onFsChange() {
  isFullscreen.value = !!document.fullscreenElement
}

function showToast(msg) {
  toast.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toast.value = ''), 2400)
}

async function share() {
  const url = shareUrl(route.params.code)
  const data = invitation.value
  const title = data ? `${data.first_name} — ${t('inv.shareSuffix')}` : 'Taklifnoma'
  if (navigator.share) {
    try {
      await navigator.share({ title, url })
      return
    } catch {
      /* bekor qilindi — nusxalashga o'tamiz */
    }
  }
  const ok = await copyText(url)
  copied.value = ok
  showToast(ok ? t('inv.toastCopied') : url)
  setTimeout(() => (copied.value = false), 2400)
}

onMounted(() => {
  load()
  document.addEventListener('fullscreenchange', onFsChange)
})
onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', onFsChange)
  clearTimeout(slowTimer)
  // Sahifadan chiqsak to'liq ekrandan chiqamiz
  if (document.fullscreenElement && typeof document.exitFullscreen === 'function') {
    document.exitFullscreen().catch(() => { })
  }
  clearTimeout(toastTimer)
  clearTimeout(openTimer)
  clearTimeout(liveTimer)
})
watch(() => route.params.code, load)
watch(locale, updateTitle)
</script>
