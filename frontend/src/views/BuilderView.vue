<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="grain"></div>
  </div>

  <!-- Header -->
  <header class="sticky top-0 z-40 border-b border-white/[0.06] bg-ink/70 backdrop-blur-xl">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
      <RouterLink to="/" class="flex items-center gap-2.5">
        <AppIcon name="ph:envelope-simple" size="1.7rem" class="text-accent" />
        <span class="grad-text font-display text-2xl font-semibold">Taklifnoma</span>
      </RouterLink>
      <nav class="flex items-center gap-2 sm:gap-3">
        <RouterLink
          v-if="lastCode"
          :to="`/i/${lastCode}`"
          class="hidden items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3.5 py-2 text-xs text-white/70 transition hover:border-accent/50 hover:text-white sm:inline-flex"
        >
          Oxirgi: <b class="font-semibold tracking-widest text-gold">{{ prettyCode(lastCode) }}</b> →
        </RouterLink>
        <RouterLink to="/enter" class="btn btn-ghost !px-4 !py-2 text-sm">
          <AppIcon name="ph:lock-key" />
          Kodni kiriting
        </RouterLink>
      </nav>
    </div>
  </header>

  <main class="mx-auto max-w-7xl px-4 pt-10 pb-24 sm:px-6">
    <!-- Sarlavha -->
    <div class="mx-auto mb-9 max-w-2xl text-center">
      <p class="mb-3 text-xs font-semibold tracking-[0.35em] text-accent uppercase">Onlayn taklifnoma yasovchi</p>
      <h1 class="font-display text-4xl leading-tight font-semibold sm:text-5xl">
        O'z taklifnomangizni <span class="grad-text">yarating</span>
      </h1>
      <p class="mt-3 leading-relaxed text-white/55">
        Ma'lumotlarni kiriting, effekt va animatsiyalarni tanlang — natijani darhol jonli ko'ring. Tayyor bo'lgach,
        <b class="text-white/80">maxfiy kod</b> olasiz.
      </p>
    </div>

    <div class="grid items-start gap-8 lg:grid-cols-2">
      <!-- ============================ FORM ============================ -->
      <section class="order-2 space-y-6 lg:order-1">
        <!-- 1. Ma'lumotlar -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">1</span> Tadbir ma'lumotlari</h2>
          <div class="mt-5 space-y-4">
            <div>
              <span class="lbl">Bayram / tadbir turi — bosganingizda tayyor dizayn qo'llanadi</span>
              <ChoiceChips :options="HOLIDAYS" :model-value="form.category" @update:model-value="onCategory" />
              <p class="mt-2 flex items-center gap-1.5 text-xs text-white/45">
                <AppIcon name="ph:calendar-blank" />
                {{ currentHoliday ? currentHoliday.hint : 'O‘z uslubingizni tanlang' }}
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
                <span class="lbl">Ism *</span>
                <input
                  v-model="form.first_name"
                  class="field"
                  :class="{ err: showErrors && !form.first_name.trim() }"
                  type="text"
                  maxlength="80"
                  placeholder="Masalan: Aziz"
                />
                <span v-if="showErrors && !form.first_name.trim()" class="err-text">Ismni kiriting *</span>
              </label>
              <label class="block">
                <span class="lbl">Familiya</span>
                <input v-model="form.last_name" class="field" type="text" maxlength="80" placeholder="Masalan: Karimov" />
              </label>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="lbl">Kimga — qabul qiluvchi</span>
                <input
                  v-model="form.to_name"
                  class="field"
                  type="text"
                  maxlength="120"
                  placeholder="Barcha do'stlarimizga"
                />
              </label>
              <label class="block">
                <span class="lbl">Kimdan — yuboruvchi</span>
                <input
                  v-model="form.from_name"
                  class="field"
                  type="text"
                  maxlength="120"
                  placeholder="Aziz va Malika oilasidan"
                />
              </label>
            </div>

            <label class="block">
              <span class="lbl">Joy / manzil</span>
              <input
                v-model="form.place"
                class="field"
                type="text"
                maxlength="200"
                placeholder="Toshkent, Markaziy to'yxona"
              />
            </label>
          </div>
        </div>

        <!-- 2. Qachon -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">2</span> Qachon?</h2>
          <div class="mt-5 space-y-4">
            <div class="grid gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="lbl">Sana *</span>
                <input
                  v-model="form.date"
                  class="field"
                  :class="{ err: showErrors && !form.date }"
                  type="date"
                  :min="todayStr"
                />
                <span v-if="showErrors && !form.date" class="err-text">Sanani tanlang *</span>
              </label>
              <label class="block">
                <span class="lbl">Vaqt *</span>
                <input
                  v-model="form.time"
                  class="field"
                  :class="{ err: showErrors && !form.time }"
                  type="time"
                />
                <span v-if="showErrors && !form.time" class="err-text">Vaqt kiriting *</span>
              </label>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs text-white/45">Tez to'ldirish:</span>
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
                Taymer <b class="text-gold">kun, soat, daqiqa va soniya</b> bo'yicha aniq hisoblanadi — mehmonlar
                tadbirgacha qolgan vaqtni soniyagacha ko'radi.
              </span>
            </p>
          </div>
        </div>

        <!-- 3. So'zlar -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">3</span> Taklifnoma so'zlari</h2>
          <div class="mt-5">
            <TextComposer v-model="form.texts" :max="MAX_TEXTS" :defaults="categoryDefaults" />
          </div>
        </div>

        <!-- 4. Dizayn -->
        <div class="glass card">
          <h2 class="section-title"><span class="num">4</span> Dizayn temasi</h2>
          <div class="mt-5">
            <ChoiceChips :options="THEMES" v-model="form.theme">
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
          <h2 class="section-title"><span class="num">5</span> Effekt va animatsiyalar</h2>

          <div class="mt-5 space-y-5">
            <div>
              <span class="lbl">
                Fon effektlari — bir nechtasini tanlang
                <b class="ml-1 text-accent">({{ form.ambient_effects.length }} ta)</b>
              </span>
              <ChoiceChips :options="AMBIENT_EFFECTS" v-model="form.ambient_effects" multiple />
            </div>

            <div>
              <span class="lbl">
                Harakatli effektlar — cheklanmagan
                <b class="ml-1 text-accent">({{ form.particle_effects.length }} ta)</b>
              </span>
              <ChoiceChips :options="PARTICLE_EFFECTS" v-model="form.particle_effects" multiple />
            </div>

            <div class="grid gap-5 sm:grid-cols-2">
              <div>
                <span class="lbl">Matn animatsiyasi — bitta</span>
                <ChoiceChips :options="TEXT_ANIMS" v-model="form.text_anim" />
              </div>
              <div>
                <span class="lbl">Karta ochilish animatsiyasi — bitta</span>
                <ChoiceChips :options="CARD_ANIMS" v-model="form.card_anim" />
              </div>
            </div>

            <p class="flex items-start gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-xs leading-relaxed text-white/55">
              <AppIcon name="ph:sparkle" class="mt-0.5" />
              <span><b class="text-white/80">Standart animatsiyalar</b> doim yoqilgan: yumshoq suzish, taymer nuri, yulduzcha titrashi va effektli fon. Effektlarni xohlagancha ko'paytiring — cheklov yo'q.</span>
            </p>
          </div>
        </div>

        <!-- Yaratish -->
        <div class="glass card text-center">
          <button class="btn btn-primary w-full px-8 text-lg sm:w-auto" type="button" :disabled="loading" @click="submit">
            <template v-if="loading">
              <span class="size-4 animate-spin rounded-full border-2 border-black/30 border-t-black"></span>
              Yaratilmoqda...
            </template>
            <template v-else><AppIcon name="ph:sparkle" /> Taklifnomani yasash</template>
          </button>
          <p v-if="submitError" class="err-text flex items-center justify-center gap-1.5" role="alert">
            <AppIcon name="ph:warning-circle" /> {{ submitError }}
          </p>
          <p class="mt-3 text-xs text-white/45">
            Yasagach, sizga <b class="text-white/70">maxfiy 8 belgili kod</b> va havola beriladi — uni faqat
            xohlagan odamingizga yuborasiz.
          </p>
        </div>
      </section>

      <!-- ============================ PREVIEW ============================ -->
      <aside class="order-1 self-start lg:sticky lg:top-24 lg:order-2">
        <div class="glass card p-4">
          <div class="mb-3 flex items-center justify-between gap-3">
            <span class="lbl !mb-0">● Jonli ko'rinish</span>
            <button class="chip !py-1.5 !text-xs" type="button" @click="showFullscreen = true">
              <AppIcon name="ph:arrows-out" /> To'liq ekran
            </button>
          </div>
          <div class="relative aspect-[3/4] w-full overflow-hidden rounded-2xl ring-1 ring-white/10 lg:aspect-[4/3]">
            <InvitationStage :data="draft" />
          </div>
          <p class="mt-3 text-center text-xs text-white/45">
            Har bir o'zgarish shu yerda darhol aks etadi — taymer ham jonli ishlaydi.
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
      ✕ Yopish
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
      <h2 class="font-display text-3xl font-semibold">Taklifnomangiz tayyor!</h2>
      <p class="mt-2 text-sm text-white/55">Bu kodni faqat xohlagan odamlaringizga yuboring.</p>

      <!-- KOD -->
      <div class="mt-5 rounded-2xl border border-gold/30 bg-gold/[0.07] px-4 py-5">
        <span class="lbl !mb-1">Taklifnoma kodi</span>
        <p class="grad-text text-3xl font-bold tracking-[0.3em] select-all sm:text-4xl">
          {{ prettyCode(result.code) }}
        </p>
      </div>

      <!-- Havola -->
      <div class="mt-4 flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] p-2 pl-4">
        <span class="min-w-0 flex-1 truncate text-left text-xs text-white/60">{{ resultLink }}</span>
        <button class="chip !py-1.5 !text-xs shrink-0" type="button" @click="copyLink">
          {{ flash === 'link' ? '✓ Nusxalandi' : 'Linkni nusxalash' }}
        </button>
      </div>

      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <RouterLink :to="`/i/${result.code}`" class="btn btn-primary">Taklifnomani ochish →</RouterLink>
        <button class="btn btn-ghost" type="button" @click="copyCode">
          {{ flash === 'code' ? '✓ Kod nusxalandi' : 'Kodni nusxalash' }}
        </button>
        <button class="btn btn-ghost sm:col-span-2" type="button" @click="resetAll">+ Yangi taklifnoma yasash</button>
      </div>

      <div class="mt-5 flex items-center justify-center gap-3 text-xs text-white/45">
        <img
          v-if="qrOk"
          :src="qrUrl"
          alt="QR kod"
          width="84"
          height="84"
          class="rounded-lg bg-white p-1"
          @error="qrOk = false"
        />
        <p class="flex items-start gap-2 max-w-[24ch] text-left leading-relaxed">
          <AppIcon name="ph:lock-key" class="mt-0.5" />
          <span>Hech kim noto'g'ri koddan sizning taklifnomangizni ko'ra olmaydi. Bir kodni istalgan son odam ko'ra oladi.</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import ChoiceChips from '../components/ChoiceChips.vue'
import AppIcon from '../components/AppIcon.vue'
import TextComposer from '../components/TextComposer.vue'
import InvitationStage from '../components/InvitationStage.vue'
import { createInvitation, shareUrl, copyText } from '../api.js'
import {
  HOLIDAYS,
  holidayById,
  nextOccurrence,
  DEFAULT_TEXTS,
  THEMES,
  AMBIENT_EFFECTS,
  PARTICLE_EFFECTS,
  TEXT_ANIMS,
  CARD_ANIMS,
  MAX_TEXTS,
  prettyCode,
} from '../data/catalog.js'

const today = new Date()
const ymd = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

const form = reactive({
  category: 'toy',
  event_type: 'toy',
  first_name: '',
  last_name: '',
  to_name: "Barcha do'stlarimizga",
  from_name: 'Bizdan',
  place: '',
  date: '',
  time: '18:00',
  theme: 'gold',
  ambient_effects: ['aurora', 'bokeh'],
  particle_effects: ['confetti', 'hearts'],
  text_anim: 'fadeUp',
  card_anim: 'scaleIn',
  texts: ['Hurmatli mehmonlar!', 'Keling, birga nishonlaymiz!'],
})

const todayStr = ymd(today)
const quickDates = [
  { label: 'Bugun', days: 0 },
  { label: 'Ertaga', days: 1 },
  { label: '+1 hafta', days: 7 },
  { label: '+1 oy', days: 30 },
]

/* ---- Bayram preseti ------------------------------------------------- */
const presetNote = ref('')
const currentHoliday = computed(() => holidayById(form.category))

/* Tanlangan bayramning tayyor matnlari + umumiy matnlar */
const categoryDefaults = computed(() => {
  const own = holidayById(form.category)?.preset?.texts || []
  return [...own, ...DEFAULT_TEXTS.filter((t) => !own.includes(t))]
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
    form.to_name = p.to_name
    form.from_name = p.from_name
  }
  if (!textsDirty.value) form.texts = [...p.texts]

  let dateFilled = false
  if (h.date && (!form.date || dateAuto)) {
    form.date = ymd(nextOccurrence(h.date.month, h.date.day))
    dateAuto = true
    dateFilled = true
  }
  applyingPreset = false

  presetNote.value =
    `«${h.label}» uchun tayyor dizayn qo'llandi: tema, effektlar, animatsiyalar va matnlar. ` +
    (dateFilled ? 'Sana avtomatik to‘ldirildi. ' : '') +
    'Xohlagancha o‘zgartiring.'
  clearTimeout(noteTimer)
  noteTimer = setTimeout(() => (presetNote.value = ''), 5000)
}

const showErrors = ref(false)
const loading = ref(false)
const submitError = ref('')
const result = ref(null)
const flash = ref('')
const showFullscreen = ref(false)
const qrOk = ref(true)
const lastCode = ref('')
let flashTimer = null

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

/* Preview uchun hozirgi forma holati */
const draft = computed(() => ({
  code: 'PREVIEW',
  category: form.category,
  event_type: form.event_type,
  first_name: form.first_name.trim() || 'Ism',
  last_name: form.last_name.trim(),
  to_name: form.to_name.trim() || 'Kimga',
  from_name: form.from_name.trim() || 'Kimdan',
  place: form.place.trim(),
  event_at: isoFromDate(form.date, form.time) || new Date(Date.now() + 3 * 86400000 + 3600000).toISOString(),
  theme: form.theme,
  ambient_effects: form.ambient_effects,
  particle_effects: form.particle_effects,
  text_anim: form.text_anim,
  card_anim: form.card_anim,
  texts: form.texts,
}))

const resultLink = computed(() => (result.value ? shareUrl(result.value.code) : ''))

const qrUrl = computed(() =>
  result.value
    ? `https://api.qrserver.com/v1/create-qr-code/?size=160x160&bgcolor=ffffff&color=0a0912&data=${encodeURIComponent(
        shareUrl(result.value.code),
      )}`
    : '',
)

async function submit() {
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
      to_name: form.to_name.trim() || "Barcha do'stlarimizga",
      from_name: form.from_name.trim() || 'Bizdan',
      event_at: isoFromDate(form.date, form.time),
      place: form.place.trim(),
      theme: form.theme,
      ambient_effects: form.ambient_effects,
      particle_effects: form.particle_effects,
      text_anim: form.text_anim,
      card_anim: form.card_anim,
      texts: form.texts.slice(0, MAX_TEXTS),
    }
    const data = await createInvitation(payload)
    result.value = data
    lastCode.value = data.code
    try {
      localStorage.setItem('taklifnoma:last', data.code)
    } catch {
      /* ignore */
    }
    showFullscreen.value = false
  } catch (e) {
    if (e.status === 429) {
      submitError.value = "Juda ko'p so'rov yuborildi — birozdan so'ng qayta urinib ko'ring."
    } else {
      submitError.value = e.message || "Serverda xatolik yuz berdi. Qayta urinib ko'ring."
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

function closeResult() {
  result.value = null
}

function resetAll() {
  result.value = null
  showErrors.value = false
  submitError.value = ''
  form.first_name = ''
  form.last_name = ''
  form.place = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function onKey(e) {
  if (e.key === 'Escape') {
    if (result.value) closeResult()
    else if (showFullscreen.value) showFullscreen.value = false
  }
}

onMounted(() => {
  document.title = 'Taklifnoma ✦ Onlayn taklifnoma yasovchi'
  try {
    lastCode.value = localStorage.getItem('taklifnoma:last') || ''
  } catch {
    lastCode.value = ''
  }
  window.addEventListener('keydown', onKey)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  clearTimeout(flashTimer)
  clearTimeout(noteTimer)
})
</script>
