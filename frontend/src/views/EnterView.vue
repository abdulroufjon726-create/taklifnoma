<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="grain"></div>
  </div>

  <main class="relative grid min-h-[100dvh] place-items-center px-4 py-10">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <RouterLink to="/" class="mb-6 flex items-center justify-center gap-3">
        <AppIcon name="ph:envelope-simple" size="2rem" class="text-accent" />
        <span class="grad-text font-display text-3xl font-semibold">Taklifnoma</span>
      </RouterLink>

      <div class="mb-4 flex justify-center">
        <LangSwitch />
      </div>

      <!-- Kod kiritish kartasi -->
      <section class="glass card modal-in p-7 sm:p-9" :class="{ shake: shaking }">
        <div class="text-center">
          <div class="mx-auto mb-4 grid size-16 place-items-center rounded-2xl bg-white/5 text-accent ring-1 ring-white/10">
            <AppIcon name="ph:lock-key" size="1.8rem" />
          </div>
          <h1 class="font-display text-2xl font-semibold text-white sm:text-3xl">{{ t('enter.title') }}</h1>
          <p class="mt-2 text-sm leading-relaxed text-white/55">
            {{ t('enter.leadA') }}<b class="text-white/80">{{ t('enter.leadStrong') }}</b>{{ t('enter.leadB') }}
          </p>
        </div>

        <form class="mt-7 space-y-4" @submit.prevent="submit">
          <div>
            <span class="lbl">{{ t('enter.codeLbl') }}</span>
            <input
              ref="inputEl"
              v-model="code"
              class="field text-center font-semibold tracking-[0.42em] uppercase placeholder:tracking-[0.3em] placeholder:normal-case sm:text-2xl"
              type="text"
              inputmode="text"
              autocomplete="off"
              autocapitalize="characters"
              spellcheck="false"
              maxlength="9"
              placeholder="XXXX-XXXX"
              :aria-invalid="!!error"
              @input="onInput"
            />
            <p v-if="error" class="err-text flex items-center justify-center gap-1.5" role="alert">
              <AppIcon name="ph:warning-circle" /> {{ error }}
            </p>
            <p v-else class="mt-2 text-center text-xs text-white/40">
              {{ t('enter.caseNote') }}
            </p>
          </div>

          <button class="btn btn-primary w-full" type="submit" :disabled="raw.length !== 8 || loading">
            <template v-if="loading">
              <span class="size-4 animate-spin rounded-full border-2 border-black/30 border-t-black"></span>
              {{ t('enter.checking') }}
            </template>
            <template v-else>{{ t('enter.submit') }}</template>
          </button>
        </form>

        <div class="mt-6 flex flex-wrap items-center justify-center gap-4 text-xs text-white/45">
          <span class="inline-flex items-center gap-1.5"><AppIcon name="ph:lock-key" /> {{ t('enter.badge1') }}</span>
          <span class="h-3 w-px bg-white/15"></span>
          <span class="inline-flex items-center gap-1.5"><AppIcon name="ph:users-three" /> {{ t('enter.badge2') }}</span>
          <span class="h-3 w-px bg-white/15"></span>
          <span class="inline-flex items-center gap-1.5"><AppIcon name="ph:lightning" /> {{ t('enter.badge3') }}</span>
        </div>
      </section>

      <p class="mt-6 text-center text-sm text-white/55">
        {{ t('enter.footQ') }}
        <RouterLink to="/" class="ml-1 font-semibold text-accent transition hover:text-gold">{{ t('enter.start') }}</RouterLink>
      </p>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import LangSwitch from '../components/LangSwitch.vue'
import { useRouter } from 'vue-router'
import { fetchInvitation } from '../api.js'
import { useI18n } from '../i18n/index.js'

const { t } = useI18n()

const router = useRouter()

const code = ref('')
const error = ref('')
const loading = ref(false)
const shaking = ref(false)
const inputEl = ref(null)
let shakeTimer = null

function shake() {
  // :key bilan qayta mount qilish input fokusini yo'qotardi — endi faqat
  // klass almashtirib animatsiyani qayta ishga tushiramiz.
  shaking.value = false
  clearTimeout(shakeTimer)
  requestAnimationFrame(() => {
    shaking.value = true
    shakeTimer = setTimeout(() => (shaking.value = false), 500)
  })
}

const raw = ref('')

function onInput() {
  const clean = inputEl.value.value.replace(/[^a-z0-9]/gi, '').toUpperCase().slice(0, 8)
  raw.value = clean
  code.value = clean.length > 4 ? `${clean.slice(0, 4)}-${clean.slice(4)}` : clean
  if (error.value) error.value = ''
  // Kursorni oxirida saqlash
  nextTick(() => {
    const el = inputEl.value
    if (el && document.activeElement === el) {
      const pos = code.value.length
      el.setSelectionRange(pos, pos)
    }
  })
}

async function submit() {
  if (raw.value.length !== 8 || loading.value) return
  loading.value = true
  error.value = ''
  try {
    await fetchInvitation(raw.value)
    router.push({ name: 'invitation', params: { code: raw.value } })
  } catch (e) {
    if (e.status === 404) {
      error.value = t('enter.err404')
    } else if (e.status === 429) {
      error.value = t('enter.err429')
    } else {
      error.value = t('enter.errNet')
    }
    shake()
    loading.value = false
    nextTick(() => inputEl.value && inputEl.value.focus())
  }
  // muvaffaqiyat bo'lsa loading o'zi ketmaydi — sahifa almashadi
}

onMounted(() => {
  document.title = 'Taklifnoma ✦ ' + t('enter.title')
  inputEl.value && inputEl.value.focus()
})

onBeforeUnmount(() => clearTimeout(shakeTimer))
</script>
