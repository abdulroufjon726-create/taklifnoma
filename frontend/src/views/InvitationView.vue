<template>
  <!-- Yuklanmoqda -->
  <div v-if="status === 'loading'" class="fixed inset-0 grid h-[100dvh] place-items-center overflow-hidden bg-ink">
    <div class="page-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>
    <div class="relative flex flex-col items-center gap-5">
      <span class="spinner"></span>
      <p class="text-sm tracking-[0.3em] text-white/55 uppercase">Taklifnoma yuklanmoqda...</p>
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
      <h1 class="font-display text-3xl font-semibold">Taklifnoma topilmadi</h1>
      <p class="mt-3 text-sm leading-relaxed text-white/60">
        <b class="text-white/85">{{ pretty || 'Kod' }}</b> bo'yicha taklifnoma mavjud emas. Kodni tekshiring yoki
        uni yasagan odamdan qayta so'rang.
      </p>
      <p v-if="status === 'error'" class="mt-2 text-xs text-red-300">{{ errorText }}</p>
      <div class="mt-6 flex flex-col gap-3">
        <RouterLink to="/enter" class="btn btn-primary w-full">Yangi kod kirish →</RouterLink>
        <RouterLink to="/" class="btn btn-ghost w-full">Taklifnoma yasash</RouterLink>
      </div>
    </div>
  </div>

  <!-- Taklifnoma: to'liq ekran, skrollsiz -->
  <div v-else class="fixed inset-0 h-[100dvh] w-full overflow-hidden bg-black">
    <InvitationStage :data="invitation" />

    <!-- Ulashish -->
    <button
      type="button"
      class="glass absolute top-4 right-4 z-20 rounded-full px-4 py-2 text-sm font-medium text-white/85 transition hover:text-white sm:top-6 sm:right-6"
      @click="share"
    >
      {{ copied ? '✓ Nusxalandi' : '↗ Ulashish' }}
    </button>

    <!-- Boshqa taklifnomalarga o'tish -->
    <RouterLink
      to="/enter"
      class="glass absolute bottom-4 left-4 z-20 rounded-full px-4 py-2 text-xs tracking-widest text-white/60 uppercase transition hover:text-white sm:bottom-6 sm:left-6"
    >
      Taklifnoma ✦ kod
    </RouterLink>

    <p
      v-if="toast"
      class="fade-in fixed bottom-6 left-1/2 z-30 -translate-x-1/2 rounded-full bg-white/10 px-5 py-2.5 text-sm text-white backdrop-blur-md"
    >
      {{ toast }}
    </p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import InvitationStage from '../components/InvitationStage.vue'
import AppIcon from '../components/AppIcon.vue'
import { fetchInvitation, shareUrl, copyText } from '../api.js'
import { prettyCode } from '../data/catalog.js'

const route = useRoute()

const status = ref('loading') // loading | ok | missing | error
const invitation = ref(null)
const errorText = ref('')
const copied = ref(false)
const toast = ref('')
let toastTimer = null

const pretty = computed(() => prettyCode(route.params.code))

async function load() {
  status.value = 'loading'
  invitation.value = null
  try {
    invitation.value = await fetchInvitation(route.params.code)
    status.value = 'ok'
    document.title = `${invitation.value.first_name} — taklifnoma ✦ ${pretty.value}`
  } catch (e) {
    if (e.status === 404) status.value = 'missing'
    else {
      status.value = 'error'
      errorText.value = e.message || 'Serverga ulanib bo\'lmadi.'
    }
  }
}

function showToast(msg) {
  toast.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toast.value = ''), 2400)
}

async function share() {
  const url = shareUrl(route.params.code)
  const data = invitation.value
  const title = data ? `${data.first_name} — taklifnoma` : 'Taklifnoma'
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
  showToast(ok ? 'Havola nusxalandi!' : url)
  setTimeout(() => (copied.value = false), 2400)
}

onMounted(load)
watch(() => route.params.code, load)
</script>
