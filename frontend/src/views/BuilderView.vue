<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="grain"></div>
  </div>

  <!-- Header -->
  <header class="sticky top-0 z-40 rounded-b-2xl border-b border-white/[0.06] bg-ink/70 backdrop-blur-xl">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
      <RouterLink to="/" class="flex items-center gap-2.5">
        <AppIcon name="ph:envelope-simple" size="1.7rem" class="text-accent" />
        <span class="grad-text font-display text-2xl font-semibold">Taklifnoma</span>
      </RouterLink>
      <nav class="flex min-w-0 items-center gap-2 sm:gap-3">
        <RouterLink
          v-if="lastCode"
          :to="`/i/${lastCode}`"
          class="hidden items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3.5 py-2 text-xs text-white/70 transition hover:border-accent/50 hover:text-white sm:inline-flex"
        >
          {{ t('nav.last') }} <b class="font-semibold tracking-widest text-gold">{{ prettyCode(lastCode) }}</b> →
        </RouterLink>
        <RouterLink to="/enter" class="btn btn-ghost !px-3 !py-2 text-sm !hidden sm:!inline-flex sm:!px-4">
          <AppIcon name="ph:lock-key" />
          <span class="hidden sm:inline">{{ t('nav.enterCode') }}</span>
        </RouterLink>
        <RouterLink to="/envelopes" class="btn btn-ghost !px-3 !py-2 text-sm sm:!px-4">
          <AppIcon name="ph:envelope-simple" />
          <span class="hidden sm:inline">{{ t('nav.envelopes') }}</span>
        </RouterLink>
        <LangSwitch />
      </nav>
    </div>
  </header>

  <main class="mx-auto max-w-7xl px-4 pt-10 pb-24 sm:px-6">
    <!-- Sarlavha -->
    <div class="mx-auto mb-9 max-w-2xl text-center">
      <p class="mb-3 text-xs font-semibold tracking-[0.35em] text-accent uppercase">{{ t('builder.kicker') }}</p>
      <h1 class="font-display text-4xl leading-tight font-semibold sm:text-5xl">
        {{ t('builder.titleA') }} <span class="grad-text">{{ t('builder.titleB') }}</span>
      </h1>
      <p class="mt-3 leading-relaxed text-white/55">
        {{ t('builder.leadA') }}
        <b class="text-white/80">{{ t('builder.leadStrong') }}</b>{{ t('builder.leadB') }}
      </p>
    </div>

    <div class="grid items-start gap-8 lg:grid-cols-2">
      <!-- ============================ FORM ============================ -->
      <section class="order-2 min-w-0 space-y-6 lg:order-1">
        <!-- Mening taklifnomalarim -->
        <div v-if="mine.length || editError" class="glass card">
          <div class="flex items-center justify-between gap-3">
            <h2 class="section-title"><span class="num">↺</span> {{ t('builder.mineTitle') }}</h2>
            <RouterLink to="/envelopes" class="text-xs text-white/45 transition hover:text-gold">
              {{ t('nav.envelopes') }} →
            </RouterLink>
          </div>
          <p v-if="editError" class="mt-3 rounded-xl border border-amber-300/30 bg-amber-300/10 px-4 py-2.5 text-xs leading-relaxed text-amber-200">
            {{ editError }}
          </p>
          <div class="mt-4 space-y-2">
            <div
              v-for="e in mine.slice(0, 5)"
              :key="e.code"
              class="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2"
            >
              <span class="min-w-0 flex-1 truncate text-sm text-white/75">
                {{ e.payload?.first_name || e.code }}
                <b class="ml-1 tracking-widest text-gold">{{ prettyCode(e.code) }}</b>
              </span>
              <RouterLink :to="`/create?edit=${e.code}`" class="chip !py-1 !text-xs">{{ t('builder.edit') }}</RouterLink>
              <RouterLink :to="`/i/${e.code}`" class="chip !py-1 !text-xs">{{ t('builder.open') }}</RouterLink>
            </div>
          </div>
        </div>

        <!-- 1. Ma'lumotlar -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">1</span> {{ t('builder.sec1') }}</h2>
          <div class="mt-5 space-y-4">
            <div>
              <span class="lbl">{{ t('builder.catLabel') }}</span>
              <ChoiceChips :options="holidayOptions" :model-value="form.category" @update:model-value="onCategory" />
              <p class="mt-2 flex items-center gap-1.5 text-xs text-white/45">
                <AppIcon name="ph:calendar-blank" />
                {{ currentHoliday ? t('holidayHint.' + form.category) : t('builder.hintDefault') }}
              </p>
              <p
                v-if="presetNote"
                class="slide-down mt-3 rounded-xl border border-accent/25 bg-accent/[0.08] px-4 py-2.5 text-xs leading-relaxed text-white/75"
              >
                <AppIcon name="ph:sparkle" />
                {{ presetNote }}
              </p>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="lbl">{{ t('builder.fName') }}</span>
                <input
                  v-model="form.first_name"
                  class="field"
                  :class="{ err: showErrors && !form.first_name.trim() }"
                  type="text"
                  maxlength="80"
                  placeholder="Masalan: Aziz"
                />
                <span v-if="showErrors && !form.first_name.trim()" class="err-text">{{ t('builder.fNameErr') }}</span>
              </label>
              <label class="block">
                <span class="lbl">{{ t('builder.fLast') }}</span>
                <input v-model="form.last_name" class="field" type="text" maxlength="80" :placeholder="t('builder.fLastPh')" />
              </label>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="lbl">{{ t('builder.fTo') }}</span>
                <input
                  v-model="form.to_name"
                  class="field"
                  type="text"
                  maxlength="120"
                  :placeholder="t('builder.fToPh')"
                />
              </label>
              <label class="block">
                <span class="lbl">{{ t('builder.fFrom') }}</span>
                <input
                  v-model="form.from_name"
                  class="field"
                  type="text"
                  maxlength="120"
                  :placeholder="t('builder.fFromPh')"
                />
              </label>
            </div>

            <label class="block">
              <span class="lbl">{{ t('builder.fPlace') }}</span>
              <input
                v-model="form.place"
                class="field"
                type="text"
                maxlength="200"
                :placeholder="t('builder.fPlacePh')"
              />
            </label>

            <div ref="mapSlot" class="map-slot">
              <PlaceMap
                v-if="mapReady"
                :place="form.place"
                :lat="form.place_lat"
                :lng="form.place_lng"
                @update:place="form.place = $event"
                @update:lat="form.place_lat = $event"
                @update:lng="form.place_lng = $event"
              />
              <div v-else class="map-skeleton" aria-hidden="true"></div>
            </div>
          </div>
        </div>

        <!-- 2. Qachon -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">2</span> {{ t('builder.sec2') }}</h2>
          <div class="mt-5 space-y-4">
            <div class="grid gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="lbl">{{ t('builder.fDate') }}</span>
                <input
                  v-model="form.date"
                  class="field"
                  :class="{ err: showErrors && !form.date }"
                  type="date"
                  :min="todayStr"
                />
                <span v-if="showErrors && !form.date" class="err-text">{{ t('builder.fDateErr') }}</span>
              </label>
              <label class="block">
                <span class="lbl">{{ t('builder.fTime') }}</span>
                <input
                  v-model="form.time"
                  class="field"
                  :class="{ err: showErrors && !form.time }"
                  type="time"
                />
                <span v-if="showErrors && !form.time" class="err-text">{{ t('builder.fTimeErr') }}</span>
              </label>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs text-white/45">{{ t('builder.quickLbl') }}</span>
              <button
                v-for="q in quickDates"
                :key="q.label"
                type="button"
                class="chip !py-1.5 !text-xs"
                @click="applyQuick(q.days)"
              >
                {{ q.label }}
              </button>
            </div>

            <p class="flex items-start gap-2 rounded-xl border border-accent/20 bg-accent/[0.07] px-4 py-3 text-sm text-white/70">
              <AppIcon name="ph:hourglass" class="mt-0.5" />
              <span>
                {{ t('builder.timerA') }}<b class="text-gold">{{ t('builder.timerB') }}</b>{{ t('builder.timerC') }}
              </span>
            </p>
          </div>
        </div>

        <!-- 3. So'zlar -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">3</span> {{ t('builder.sec3') }}</h2>
          <div class="mt-5">
            <TextComposer v-model="form.texts" :max="MAX_TEXTS" :defaults="categoryDefaults" />
          </div>
        </div>

        <!-- 4. Dizayn -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">4</span> {{ t('builder.sec4') }}</h2>
          <div class="mt-5">
            <ChoiceChips :options="themeOptions" v-model="form.theme">
              <template #item="{ o }">
                <span
                  class="size-4 rounded-full ring-1 ring-white/30"
                  :style="{
                    background: `linear-gradient(135deg, ${o.swatch[0]} 0%, ${o.swatch[1]} 55%, ${o.swatch[2]} 100%)`,
                  }"
                ></span>
                {{ o.label || o.name }}
              </template>
            </ChoiceChips>
          </div>
        </div>

        <!-- 5. Effekt va animatsiyalar -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">5</span> {{ t('builder.sec5') }}</h2>

          <div class="mt-5 space-y-5">
            <div>
              <span class="lbl">
                {{ t('builder.ambientLbl') }}
                <b class="ml-1 text-accent">{{ tf('builder.count', { n: form.ambient_effects.length }) }}</b>
              </span>
              <ChoiceChips :options="ambientOptions" v-model="form.ambient_effects" multiple />
            </div>

            <div>
              <span class="lbl">
                {{ t('builder.particleLbl') }}
                <b class="ml-1 text-accent">{{ tf('builder.count', { n: form.particle_effects.length }) }}</b>
              </span>
              <ChoiceChips :options="particleOptions" v-model="form.particle_effects" multiple />
            </div>

            <div class="grid gap-5 sm:grid-cols-2">
              <div>
                <span class="lbl">{{ t('builder.textAnimLbl') }}</span>
                <ChoiceChips :options="textAnimOptions" v-model="form.text_anim" />
              </div>
              <div>
                <span class="lbl">{{ t('builder.cardAnimLbl') }}</span>
                <ChoiceChips :options="cardAnimOptions" v-model="form.card_anim" />
              </div>
            </div>

            <p class="flex items-start gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-xs leading-relaxed text-white/55">
              <AppIcon name="ph:sparkle" class="mt-0.5" />
              <span><b class="text-white/80">{{ t('builder.stdA') }}</b>{{ t('builder.stdB') }}</span>
            </p>
          </div>
        </div>

        <!-- 6. Shriftlar -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">6</span> {{ t('builder.sec6') }}</h2>
          <div class="mt-5 grid gap-4 sm:grid-cols-3">
            <label v-for="r in fontRoles" :key="r.key" class="block">
              <span class="lbl">{{ t(r.label) }}</span>
              <select v-model="form.fonts[r.key]" class="field" :style="{ fontFamily: fontStack(form.fonts[r.key]) }">
                <option v-for="f in FONTS" :key="f.id" :value="f.id">{{ f.label }}</option>
              </select>
            </label>
          </div>
          <div v-if="form.texts.length" class="mt-5 space-y-2">
            <span class="lbl">{{ t('builder.textFonts') }}</span>
            <div v-for="(txt, i) in form.texts" :key="`f-${i}`" class="flex items-center gap-2">
              <span class="min-w-0 flex-1 truncate text-xs text-white/50">«{{ txt }}»</span>
              <select
                v-model="form.fonts.texts[i]"
                class="field !w-auto shrink-0 !py-1.5 !text-xs"
                :style="{ fontFamily: fontStack(form.fonts.texts[i]) }"
              >
                <option v-for="f in FONTS" :key="f.id" :value="f.id">{{ f.label }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Yaratish -->
        <div class="glass card text-center">
          <p v-if="editing" class="mb-3 inline-flex items-center gap-2 rounded-full border border-accent/40 bg-accent/10 px-4 py-1.5 text-xs text-white/80">
            {{ t('builder.editingNow') }} · <b class="tracking-widest text-gold">{{ prettyCode(editing.code) }}</b>
          </p>
          <button class="btn btn-primary w-full px-8 text-lg sm:w-auto" type="button" :disabled="loading" @click="submit">
            <template v-if="loading">
              <span class="size-4 animate-spin rounded-full border-2 border-black/30 border-t-black"></span>
              {{ t('builder.submitting') }}
            </template>
            <template v-else><AppIcon name="ph:sparkle" /> {{ editing ? t('builder.saveBtn') : t('builder.submit') }}</template>
          </button>
          <button v-if="editing" class="btn btn-ghost mt-3 w-full sm:ml-3 sm:mt-0 sm:w-auto" type="button" @click="cancelEdit">
            {{ t('builder.cancelEdit') }}
          </button>
          <p v-if="submitError" class="err-text flex items-center justify-center gap-1.5" role="alert">
            <AppIcon name="ph:warning-circle" /> {{ submitError }}
          </p>
          <p class="mt-3 text-xs text-white/45">
            {{ t('builder.footA') }} <b class="text-white/70">{{ t('builder.footStrong') }}</b>{{ t('builder.footB') }}
          </p>
        </div>
      </section>

      <!-- ============================ PREVIEW ============================ -->
      <aside class="order-1 min-w-0 self-start lg:sticky lg:top-24 lg:order-2">
        <div class="glass card p-4">
          <div class="mb-3 flex items-center justify-between gap-3">
            <span class="lbl !mb-0">{{ t('builder.live') }}</span>
            <button class="chip !py-1.5 !text-xs" type="button" @click="showFullscreen = true">
              <AppIcon name="ph:arrows-out" /> {{ t('builder.fullscreen') }}
            </button>
          </div>
          <div class="relative aspect-[3/4] w-full overflow-hidden rounded-2xl ring-1 ring-white/10 lg:aspect-[4/3]">
            <InvitationStage :data="draft" :paused="previewPaused" />
          </div>
          <p class="mt-3 text-center text-xs text-white/45">
            {{ t('builder.prevNote') }}
          </p>
        </div>
      </aside>
    </div>
  </main>

  <!-- To'liq ekran ko'rinish -->
  <div v-if="showFullscreen" class="fixed inset-0 z-50 bg-black">
    <InvitationStage :data="draft" />
    <button
      class="glass absolute top-4 right-4 z-20 rounded-full px-4 py-2 text-sm font-medium transition hover:text-white"
      type="button"
      @click="showFullscreen = false"
    >
      {{ t('builder.close') }}
    </button>
  </div>

  <!-- Natija: kod + havola -->
  <div
    v-if="result"
    class="fixed inset-0 z-50 grid place-items-center overflow-y-auto bg-black/80 p-4 backdrop-blur-sm"
    @click.self="closeResult"
  >
    <div class="glass card modal-in relative w-full max-w-lg p-6 text-center sm:p-8">
      <button
        class="absolute top-4 right-4 grid size-9 place-items-center rounded-full bg-white/5 text-white/60 transition hover:bg-white/10 hover:text-white"
        type="button"
        aria-label="Yopish"
        @click="closeResult"
      >
        ✕
      </button>

      <div class="mx-auto mb-3 grid size-14 place-items-center rounded-2xl bg-white/5 text-accent ring-1 ring-white/10">
        <AppIcon name="ph:confetti" size="1.7rem" />
      </div>
      <h2 class="font-display text-3xl font-semibold">{{ result.updated ? t('builder.updatedTitle') : t('builder.resTitle') }}</h2>
      <p class="mt-2 text-sm text-white/55">{{ result.updated ? t('builder.updatedSub') : t('builder.resSub') }}</p>

      <!-- KOD -->
      <div class="mt-5 rounded-2xl border border-gold/30 bg-gold/[0.07] px-4 py-5">
        <span class="lbl !mb-1">{{ t('builder.codeLbl') }}</span>
        <p class="grad-text text-3xl font-bold tracking-[0.3em] select-all sm:text-4xl">
          {{ prettyCode(result.code) }}
        </p>
      </div>

      <!-- Havola -->
      <div class="mt-4 flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] p-2 pl-4">
        <span class="min-w-0 flex-1 truncate text-left text-xs text-white/60">{{ resultLink }}</span>
        <button class="chip !py-1.5 !text-xs shrink-0" type="button" @click="copyLink">
          {{ flash === 'link' ? t('builder.linkCopied') : t('builder.copyLink') }}
        </button>
      </div>

      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <RouterLink :to="`/i/${result.code}`" class="btn btn-primary">{{ t('builder.open') }}</RouterLink>
        <button class="btn btn-ghost" type="button" @click="copyCode">
          {{ flash === 'code' ? t('builder.codeCopied') : t('builder.copyCode') }}
        </button>
        <button class="btn btn-ghost sm:col-span-2" type="button" @click="resetAll">{{ t('builder.newOne') }}</button>
      </div>

      <div class="mt-5 flex items-center justify-center gap-3 text-xs text-white/45">
        <div v-if="qrData" class="text-center">
          <img
            :src="qrData"
            alt="QR kod"
            width="96"
            height="96"
            class="rounded-lg bg-white p-1"
          />
          <p class="mt-1.5 text-[10px] text-white/40">{{ t('builder.qrCap') }}</p>
          <button class="chip !py-1 !px-2.5 !text-[10px] mt-1.5" type="button" @click="downloadQr">
            {{ flash === 'qr' ? t('builder.qrDlDone') : t('builder.qrDl') }}
          </button>
        </div>
        <p class="flex items-start gap-2 max-w-[24ch] text-left leading-relaxed">
          <AppIcon name="ph:lock-key" class="mt-0.5" />
          <span>{{ t('builder.qrNote') }}</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, shallowRef, computed, defineAsyncComponent, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ChoiceChips from '../components/ChoiceChips.vue'
import AppIcon from '../components/AppIcon.vue'
import TextComposer from '../components/TextComposer.vue'
import InvitationStage from '../components/InvitationStage.vue'
import LangSwitch from '../components/LangSwitch.vue'
import {
  createInvitation,
  updateInvitation,
  fetchMyInvitations,
  shareUrl,
  copyText,
  warmUp,
} from '../api.js'
import { auth, loadMe, signOutLocal } from '../auth.js'
/* Leaflet (150 KB) va plitkalar xarita maydoni ko'rinishga yaqinlashganda
   yuklanadi — create/edit sahifasi darhol ochiladi. */
const PlaceMap = defineAsyncComponent(() => import('../components/PlaceMap.vue'))
import { getMine, saveMine } from '../data/mine.js'
import { useI18n, tf } from '../i18n/index.js'
import {
  HOLIDAYS,
  holidayById,
  nextOccurrence,
  THEMES,
  AMBIENT_EFFECTS,
  PARTICLE_EFFECTS,
  TEXT_ANIMS,
  CARD_ANIMS,
  MAX_TEXTS,
  prettyCode,
  FONTS,
  fontStack,
} from '../data/catalog.js'

const { t, locale } = useI18n()

/* Katalog yorliqlari — joriy tilga reaktiv */
const withLabels = (list, ns) =>
  computed(() => list.map((o) => ({ ...o, label: t(`${ns}.${o.id}`) })))
const holidayOptions = withLabels(HOLIDAYS, 'holiday')
const themeOptions = withLabels(THEMES, 'theme')
const ambientOptions = withLabels(AMBIENT_EFFECTS, 'ambient')
const particleOptions = withLabels(PARTICLE_EFFECTS, 'particle')
const textAnimOptions = withLabels(TEXT_ANIMS, 'textAnim')
const cardAnimOptions = withLabels(CARD_ANIMS, 'cardAnim')

const today = new Date()
const ymd = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

/* Sana tanlanmagan paytda ham barqaror (o'zgarmaydigan) fallback vaqt —
   aks holda har renderda countdown qayta ishga tushardi. */
const FALLBACK_EVENT_AT = new Date(Date.now() + 3 * 86400000 + 3600000).toISOString()

const form = reactive({
  category: 'toy',
  event_type: 'toy',
  first_name: '',
  last_name: '',
  to_name: t('presetTo.toy'),
  from_name: t('presetFrom.toy'),
  place: '',
  place_lat: null,
  place_lng: null,
  date: '',
  time: '18:00',
  theme: 'gold',
  ambient_effects: ['aurora', 'bokeh'],
  particle_effects: ['confetti', 'hearts'],
  text_anim: 'fadeUp',
  card_anim: 'scaleIn',
  texts: (t('presetTexts.toy') || []).slice(0, 2),
  fonts: emptyFonts(),
})

function emptyFonts() {
  return { salute: 'vibes', names: 'cormorant', from: 'montserrat', texts: [] }
}

const fontRoles = [
  { key: 'salute', label: 'builder.fontSalute' },
  { key: 'names', label: 'builder.fontNames' },
  { key: 'from', label: 'builder.fontFrom' },
]

const todayStr = ymd(today)
const quickDates = computed(() => [
  { label: t('builder.quickToday'), days: 0 },
  { label: t('builder.quickTomorrow'), days: 1 },
  { label: t('builder.quickWeek'), days: 7 },
  { label: t('builder.quickMonth'), days: 30 },
])

/* ---- Bayram preseti ------------------------------------------------- */
const presetNote = ref('')
const currentHoliday = computed(() => holidayById(form.category))

/* Tanlangan bayramning tayyor matnlari + umumiy matnlar (joriy til) */
const categoryDefaults = computed(() => {
  const own = t(`presetTexts.${form.category}`) || []
  const common = t('defaultTexts') || []
  return [...own, ...common.filter((x) => !own.includes(x))]
})

let applyingPreset = false
let noteTimer = null
let dateAuto = false // sana preset tomonidan avtomatik to'ldirilganmi
const textsDirty = ref(false) // foydalanuvchi matnlarni o'zi o'zgartirdimi
const contactDirty = ref(false) // kimga/kimdan maydonlarini o'zgartirdimi

watch(
  () => form.date,
  () => {
    if (!applyingPreset) dateAuto = false // foydalanuvchi sana o'zgartirdi
  },
  { flush: 'sync' },
)

watch(
  () => form.texts,
  () => {
    if (!applyingPreset) textsDirty.value = true
  },
  { flush: 'sync' },
)
watch(
  () => [form.to_name, form.from_name],
  () => {
    if (!applyingPreset) contactDirty.value = true
  },
  { flush: 'sync' },
)

function onCategory(id) {
  const h = holidayById(id)
  if (!h || id === form.category) return
  const p = h.preset
  applyingPreset = true

  form.category = h.id
  form.event_type = h.event_type
  form.theme = p.theme
  form.ambient_effects = [...p.ambient_effects]
  form.particle_effects = [...p.particle_effects]
  form.text_anim = p.text_anim
  form.card_anim = p.card_anim
  if (!contactDirty.value) {
    form.to_name = t(`presetTo.${id}`) || p.to_name
    form.from_name = t(`presetFrom.${id}`) || p.from_name
  }
  if (!textsDirty.value) {
    form.texts = [...(t(`presetTexts.${id}`) || p.texts)]
  }

  let dateFilled = false
  if (h.date && (!form.date || dateAuto)) {
    form.date = ymd(nextOccurrence(h.date.month, h.date.day))
    dateAuto = true
    dateFilled = true
  }
  applyingPreset = false

  presetNote.value =
    tf('builder.presetApplied', { name: t(`holiday.${id}`) }) +
    (dateFilled ? t('builder.presetDate') : '') +
    t('builder.presetFree')
  clearTimeout(noteTimer)
  noteTimer = setTimeout(() => (presetNote.value = ''), 5000)
}

const showErrors = ref(false)
const loading = ref(false)
const submitError = ref('')
const result = ref(null)
const flash = ref('')
const showFullscreen = ref(false)
const mapReady = ref(false)
const mapSlot = ref(null)
let mapIO = null
let mapTimer = null

function showMap() {
  if (mapReady.value) return
  mapReady.value = true
  if (mapIO) {
    mapIO.disconnect()
    mapIO = null
  }
  clearTimeout(mapTimer)
  mapTimer = null
}
const qrData = ref('') // mahalliy QR — aynan shu taklifnoma havolasidan
const lastCode = ref('')
let flashTimer = null

/* Modal/to'liq ekran ochilganda orqadagi preview animatsiyalari to'xtaydi —
   ikki joyda bir xil canvas ishlamaydi, telefon ham qizimaydi. */
const previewPaused = computed(() => showFullscreen.value || !!result.value)

function applyQuick(days) {
  const d = new Date()
  d.setDate(d.getDate() + days)
  form.date = ymd(d)
}

function isoFromDate(dateStr, timeStr) {
  if (!dateStr || !timeStr) return null
  const d = new Date(`${dateStr}T${timeStr}`)
  return Number.isNaN(d.getTime()) ? null : d.toISOString()
}

/* Preview uchun hozirgi forma holati. Har bir tugma bosishida butun sahna
   qayta render bo'lmasligi uchun 180ms debounce qilamiz — yozayotganda
   animatsiyalar qayta-qayta boshlanmaydi va telefon qotmaydi. */
function buildDraft() {
  return {
    code: 'PREVIEW',
    category: form.category,
    event_type: form.event_type,
    first_name: form.first_name.trim() || t('builder.defName'),
    last_name: form.last_name.trim(),
    to_name: form.to_name.trim() || t('builder.defTo'),
    from_name: form.from_name.trim() || t('builder.defFrom'),
    place: form.place.trim(),
    place_lat: form.place_lat,
    place_lng: form.place_lng,
    event_at: isoFromDate(form.date, form.time) || FALLBACK_EVENT_AT,
    theme: form.theme,
    ambient_effects: form.ambient_effects,
    particle_effects: form.particle_effects,
    text_anim: form.text_anim,
    card_anim: form.card_anim,
    texts: form.texts,
    fonts: { ...form.fonts, texts: [...form.fonts.texts] },
  }
}

const draft = shallowRef(buildDraft())
let draftTimer = null
watch(
  form,
  () => {
    clearTimeout(draftTimer)
    draftTimer = setTimeout(() => {
      // Bir xil holat qayta render qilmasin; 260ms — yozishda qotishsiz
      const next = buildDraft()
      if (JSON.stringify(next) !== JSON.stringify(draft.value)) draft.value = next
    }, 260)
  },
  { deep: true },
)

/* Matnlar soni o'zgarsa — shriftlar ro'yxati ham mos bo'lsin */
watch(
  () => form.texts.length,
  (n) => {
    const arr = form.fonts.texts
    while (arr.length < n) arr.push('')
    if (arr.length > n) arr.length = n
  },
  { flush: 'sync' },
)

const resultLink = computed(() => (result.value ? shareUrl(result.value.code) : ''))

/* ---- Tahrirlash ------------------------------------------------------- */
const route = useRoute()
const router = useRouter()
const editing = ref(null) // { code, editKey }
const mine = ref([])
const editError = ref('')

/* Serverdan kelgan taklifnomani forma uchun "yozuv"ga aylantiramiz */
function toEntry(inv) {
  const d = new Date(inv.event_at)
  const pad = (n) => String(n).padStart(2, '0')
  const valid = !Number.isNaN(d.getTime())
  return {
    code: inv.code,
    editKey: localEditEntry(inv.code)?.editKey || '',
    payload: {
      ...inv,
      date: valid ? `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` : '',
      time: valid ? `${pad(d.getHours())}:${pad(d.getMinutes())}` : '18:00',
    },
  }
}

async function loadMine() {
  try {
    mine.value = (await fetchMyInvitations()).map(toEntry)
  } catch (e) {
    if (e && e.status === 401) {
      signOutLocal()
      router.replace({ path: '/login', query: { next: route.fullPath, expired: '1' } })
    }
    /* boshqa xatolarda forma baribir ishlaydi */
  }
}

function applyMineEntry(entry) {
  const p = entry.payload || {}
  applyingPreset = true
  form.category = p.category || 'toy'
  form.event_type = p.event_type || 'toy'
  form.first_name = p.first_name || ''
  form.last_name = p.last_name || ''
  form.to_name = p.to_name || ''
  form.from_name = p.from_name || ''
  form.place = p.place || ''
  form.place_lat = typeof p.place_lat === 'number' ? p.place_lat : null
  form.place_lng = typeof p.place_lng === 'number' ? p.place_lng : null
  form.date = p.date || ''
  form.time = p.time || '18:00'
  form.theme = p.theme || 'gold'
  form.ambient_effects = [...(p.ambient_effects || [])]
  form.particle_effects = [...(p.particle_effects || [])]
  form.text_anim = p.text_anim || 'fadeUp'
  form.card_anim = p.card_anim || 'scaleIn'
  form.texts = [...(p.texts || [])]
  form.fonts = { ...emptyFonts(), ...(p.fonts || {}), texts: [...((p.fonts && p.fonts.texts) || [])] }
  applyingPreset = false
  textsDirty.value = true
  contactDirty.value = true
}

/* Faqat egasi (server ro'yxati) yoki shu qurilmada saqlangan kalit.
   Begona hisobning kaliti bilan ochilmaydi (umumiy brauzer). */
function localEditEntry(code) {
  const entry = getMine(code)
  if (!entry || !entry.editKey) return null
  const uid = auth.user?.id ?? null
  if (entry.ownerId && entry.ownerId !== uid) return null
  return entry
}

function loadForEdit(code) {
  const clean = String(code || '').replace(/[^a-z0-9]/gi, '').toUpperCase()
  if (!clean) return
  const owned = mine.value.find((e) => e.code === clean)
  const entry = owned || localEditEntry(clean)
  if (!entry) {
    editing.value = null
    editError.value = t('builder.editNoKey')
    return
  }
  applyMineEntry(entry)
  editing.value = { code: entry.code, editKey: entry.editKey || '' }
  editError.value = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelEdit() {
  editing.value = null
  editError.value = ''
  if (route.query.edit) router.replace({ path: '/create' })
}

/* Reaktiv yorliqlar uchun til o'zgarishini kuzatish */
watch(locale, () => {
  document.title = 'Taklifnoma ✦ ' + t('builder.kicker')
  draft.value = buildDraft()
})

/* QR shu taklifnomaning aniq havolasidan mahalliy yaratiladi —
   boshqa taklifnomaga qarab ketishi mumkin emas, tashqi server yo'q */
async function makeQr(code) {
  qrData.value = ''
  if (!code) return
  try {
    // QR kutubxonasi faqat kerak bo'lganda yuklanadi (boshlang'ich bundle yengil)
    const mod = await import('qrcode')
    const QRCode = mod.default || mod
    qrData.value = await QRCode.toDataURL(shareUrl(code), {
      width: 320,
      margin: 1,
      color: { dark: '#0a0912', light: '#ffffff' },
      errorCorrectionLevel: 'M',
    })
  } catch {
    qrData.value = ''
  }
}

async function submit() {
  if (loading.value) return
  submitError.value = ''
  showErrors.value = true
  if (!form.first_name.trim() || !form.date || !form.time) {
    return
  }
  loading.value = true
  try {
    const payload = {
      category: form.category,
      event_type: form.event_type,
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      to_name: form.to_name.trim() || t('presetTo.toy'),
      from_name: form.from_name.trim() || t('presetFrom.toy'),
      event_at: isoFromDate(form.date, form.time),
      place: form.place.trim(),
      place_lat: form.place_lat,
      place_lng: form.place_lng,
      theme: form.theme,
      ambient_effects: form.ambient_effects,
      particle_effects: form.particle_effects,
      text_anim: form.text_anim,
      card_anim: form.card_anim,
      texts: form.texts.slice(0, MAX_TEXTS),
      fonts: {
        salute: form.fonts.salute,
        names: form.fonts.names,
        from: form.fonts.from,
        texts: form.texts.slice(0, MAX_TEXTS).map((_, i) => form.fonts.texts[i] || ''),
      },
    }

    let data
    if (editing.value) {
      data = await updateInvitation(editing.value.code, editing.value.editKey, payload)
      data.updated = true
    } else {
      data = await createInvitation(payload)
      data.updated = false
    }

    result.value = data
    lastCode.value = data.code
    makeQr(data.code)

    // Keyingi tahrirlash uchun kalit va forma shu qurilmada saqlanadi
    saveMine({
      code: data.code,
      editKey: editing.value ? editing.value.editKey : data.edit_key,
      ownerId: auth.user?.id ?? null,
      payload: { ...payload, date: form.date, time: form.time },
      updated_at: Date.now(),
    })
    await loadMine()

    try {
      localStorage.setItem('taklifnoma:last', data.code)
    } catch {
      /* ignore */
    }
    showFullscreen.value = false
  } catch (e) {
    if (e.status === 401) {
      // Sessiya tugagan — qayta kirishga yuboramiz
      signOutLocal()
      router.replace({ path: '/login', query: { next: '/create', expired: '1' } })
      return
    }
    if (e.status === 429) {
      submitError.value = t('builder.err429')
    } else {
      submitError.value = e.message || t('builder.errGeneric')
    }
  } finally {
    loading.value = false
  }
}

function flashMsg(kind) {
  flash.value = kind
  clearTimeout(flashTimer)
  flashTimer = setTimeout(() => (flash.value = ''), 2200)
}

async function copyCode() {
  if (!result.value) return
  const ok = await copyText(prettyCode(result.value.code).replace('-', ''))
  if (ok) flashMsg('code')
}

async function copyLink() {
  if (!result.value) return
  const ok = await copyText(shareUrl(result.value.code))
  if (ok) flashMsg('link')
}

/* QR'ni PNG fayl sifatida yuklab olish — lokal data-URL'dan, code nom bilan */
function downloadQr() {
  if (!qrData.value || !result.value) return
  const a = document.createElement('a')
  a.href = qrData.value
  a.download = `taklifnoma-${prettyCode(result.value.code)}.png`
  document.body.appendChild(a)
  a.click()
  a.remove()
  flashMsg('qr')
}

function closeResult() {
  result.value = null
  qrData.value = ''
}

function resetAll() {
  result.value = null
  qrData.value = ''
  showErrors.value = false
  submitError.value = ''
  editing.value = null
  editError.value = ''
  if (route.query.edit) router.replace({ path: '/create' })
  form.first_name = ''
  form.last_name = ''
  form.place = ''
  form.place_lat = null
  form.place_lng = null
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function onKey(e) {
  if (e.key === 'Escape') {
    if (result.value) closeResult()
    else if (showFullscreen.value) showFullscreen.value = false
  }
}

onMounted(async () => {
  document.title = 'Taklifnoma ✦ ' + t('builder.kicker')
  // Taklifnoma yaratish uchun hisob kerak
  if (!auth.token) {
    router.replace({ path: '/login', query: { next: route.fullPath } })
    return
  }
  // Render bepul tarifi uxlab qolishi mumkin — forma to'ldirilayotganda
  // backendni oldindan uyg'otamiz, submit kutmaydi.
  warmUp()
  try {
    lastCode.value = localStorage.getItem('taklifnoma:last') || ''
  } catch {
    lastCode.value = ''
  }
  // Profil va ro'yxat parallel — edit ma'lumoti tezroq to'ldiriladi
  await Promise.all([loadMe(), loadMine()])
  if (route.query.edit) loadForEdit(route.query.edit)
  // Xarita faqat ko'rinish maydoniga yaqinlashganda mount bo'ladi
  if (typeof IntersectionObserver === 'function' && mapSlot.value) {
    mapIO = new IntersectionObserver(
      (entries) => {
        if (!entries.some((e) => e.isIntersecting)) return
        showMap()
      },
      { rootMargin: '300px' },
    )
    mapIO.observe(mapSlot.value)
    // Har holatda xarita chiqishi kerak: IO ishlamasa 6 soniyada yuklaymiz
    mapTimer = setTimeout(showMap, 6000)
  } else {
    showMap()
  }
  window.addEventListener('keydown', onKey)
})

watch(
  () => route.query.edit,
  (code) => {
    if (code) loadForEdit(code)
  },
)

onBeforeUnmount(() => {
  if (mapIO) mapIO.disconnect()
  clearTimeout(mapTimer)
  window.removeEventListener('keydown', onKey)
  clearTimeout(flashTimer)
  clearTimeout(noteTimer)
  clearTimeout(draftTimer)
})
</script>

<style scoped>
.map-skeleton {
  height: 258px;
  border-radius: 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(100deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.04));
  background-size: 220% 100%;
  animation: mapShimmer 1.4s linear infinite;
}
@keyframes mapShimmer {
  to {
    background-position: -120% 0;
  }
}
@media (prefers-reduced-motion: reduce) {
  .map-skeleton {
    animation: none;
  }
}
</style>
