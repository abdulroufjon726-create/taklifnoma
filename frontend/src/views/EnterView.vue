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

      <!-- Kod kiritish kartasi -->
      <section class="glass card modal-in p-7 sm:p-9" :class="{ shake: shakeKey % 2 === 1 }" :key="shakeKey">
        <div class="text-center">
          <div class="mx-auto mb-4 grid size-16 place-items-center rounded-2xl bg-white/5 text-accent ring-1 ring-white/10">
            <AppIcon name="ph:lock-key" size="1.8rem" />
          </div>
          <h1 class="font-display text-2xl font-semibold text-white sm:text-3xl">Taklifnomani oching</h1>
          <p class="mt-2 text-sm leading-relaxed text-white/55">
            Sizga berilgan <b class="text-white/80">8 belgili kodni</b> kiriting. Kodni faqat siz bilgan odamlar ko'ra
            oladi.
          </p>
        </div>

        <form class="mt-7 space-y-4" @submit.prevent="submit">
          <div>
            <span class="lbl">Taklifnoma kodi</span>
            <input
              ref="inputEl"
              v-model="code"
              class="field text-center font-semibold tracking-[0.42em] uppercase placeholder:tracking-[0.3em] placeholder:normal-case sm:text-2xl"
              type="text"
              inputmode="latin"
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
              Koddagi harflar katta-kichikligi ahamiyatsiz
            </p>
          </div>

          <button class="btn btn-primary w-full" type="submit" :disabled="raw.length !== 8 || loading">
            <template v-if="loading">
              <span class="size-4 animate-spin rounded-full border-2 border-black/30 border-t-black"></span>
              Tekshirilmoqda...
            </template>
            <template v-else>Taklifnomani ochish →</template>
          </button>
        </form>

        <div class="mt-6 flex flex-wrap items-center justify-center gap-4 text-xs text-white/45">
          <span class="inline-flex items-center gap-1.5"><AppIcon name="ph:lock-key" /> Maxfiy</span>
          <span class="h-3 w-px bg-white/15"></span>
          <span class="inline-flex items-center gap-1.5"><AppIcon name="ph:users-three" /> Cheksiz ko'ruvchi</span>
          <span class="h-3 w-px bg-white/15"></span>
          <span class="inline-flex items-center gap-1.5"><AppIcon name="ph:lightning" /> Aniq taymer</span>
        </div>
      </section>

      <p class="mt-6 text-center text-sm text-white/55">
        Taklifnoma yasashmoqchimisiz?
        <RouterLink to="/" class="ml-1 font-semibold text-accent transition hover:text-gold">Boshlash →</RouterLink>
      </p>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import { useRouter } from 'vue-router'
import { fetchInvitation } from '../api.js'

const router = useRouter()

const code = ref('')
const error = ref('')
const loading = ref(false)
const shakeKey = ref(0)
const inputEl = ref(null)

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
      error.value = 'Bunday kodli taklifnoma topilmadi. Kodni tekshirib qayta kiriting.'
    } else if (e.status === 429) {
      error.value = "Juda ko'p urinish bo'ldi. Bir ozdan so'ng qayta urinib ko'ring."
    } else {
      error.value = e.message || "Serverga ulanib bo'lmadi."
    }
    shakeKey.value += 1
    loading.value = false
    nextTick(() => inputEl.value && inputEl.value.focus())
  }
  // muvaffaqiyat bo'lsa loading o'zi ketmaydi — sahifa almashadi
}

onMounted(() => inputEl.value && inputEl.value.focus())
</script>
