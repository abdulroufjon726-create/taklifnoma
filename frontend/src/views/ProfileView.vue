<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="grain"></div>
  </div>

  <SiteHeader />

  <main class="profile">
    <div class="glass card prof-card">
      <div class="prof-top">
        <span class="prof-avatar">{{ initial }}</span>
        <div class="min-w-0">
          <p class="prof-kicker">{{ t('profile.title') }}</p>
          <h1 class="prof-name">{{ name }}</h1>
          <p class="prof-email">{{ auth.user?.email }}</p>
        </div>
      </div>

      <div class="prof-stats">
        <div class="stat">
          <b>{{ envelopeCount }}</b>
          <span>{{ t('profile.statEnvelopes') }}</span>
        </div>
        <div class="stat">
          <b>{{ totalViews }}</b>
          <span>{{ t('profile.statViews') }}</span>
        </div>
        <div class="stat">
          <b class="method">{{ methodLabel }}</b>
          <span>{{ t('profile.method') }}</span>
        </div>
      </div>

      <form v-if="auth.user && !auth.user.has_password" class="pw-form" @submit.prevent="savePassword">
        <p class="pw-title">{{ t('profile.setPwTitle') }}</p>
        <div class="pw-row">
          <input
            v-model="pw"
            class="field"
            type="password"
            minlength="8"
            autocomplete="new-password"
            :placeholder="t('profile.setPwPh')"
          />
          <button class="btn btn-primary" type="submit" :disabled="pwBusy || pw.length < 8">
            {{ t('profile.setPwBtn') }}
          </button>
        </div>
        <p v-if="pwMsg" class="pw-msg">{{ pwMsg }}</p>
      </form>

      <div class="prof-actions">
        <RouterLink to="/envelopes" class="btn btn-primary">
          <AppIcon name="ph:envelope-simple" />
          {{ t('profile.myEnvelopes') }}
        </RouterLink>
        <RouterLink to="/create" class="btn btn-ghost">
          <AppIcon name="ph:plus" />
          {{ t('profile.newBtn') }}
        </RouterLink>
        <button class="btn btn-ghost danger" @click="logout">
          <AppIcon name="ph:sign-out" />
          {{ t('profile.logout') }}
        </button>
      </div>

      <p v-if="!authConfig.google" class="prof-note">{{ t('profile.googleOff') }}</p>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchMyInvitations } from '../api.js'
import { auth, authConfig, loadAuthConfig, loadMe, setPassword, signOut } from '../auth.js'
import { useI18n } from '../i18n/index.js'
import AppIcon from '../components/AppIcon.vue'
import SiteHeader from '../components/SiteHeader.vue'

const { t } = useI18n()
const router = useRouter()

const items = ref([])
const pw = ref('')
const pwBusy = ref(false)
const pwMsg = ref('')

const name = computed(() => auth.user?.name || auth.user?.email || '')
const initial = computed(() => (name.value || '?').trim().charAt(0).toUpperCase())
const envelopeCount = computed(() => (items.value.length ? items.value.length : auth.user?.invitations || 0))
const totalViews = computed(() => items.value.reduce((sum, i) => sum + (i.views || 0), 0))
const methodLabel = computed(() =>
  auth.user?.has_password ? t('profile.methodEmail') : t('profile.methodGoogle'),
)

onMounted(async () => {
  document.title = 'Taklifnoma ✦ ' + t('profile.title')
  if (!auth.token) {
    router.replace({ path: '/login', query: { next: '/account' } })
    return
  }
  await Promise.all([loadAuthConfig(), loadMe()])
  try {
    items.value = await fetchMyInvitations()
  } catch (e) {
    if (e && (e.status === 401 || e.status === 403)) {
      const expired = e.status === 401 ? '1' : ''
      router.replace({ path: '/login', query: { next: '/account', expired } })
      return
    }
    /* statistika bo'lmasa ham sahifa ishlaydi */
  }
})

async function logout() {
  await signOut()
  router.replace('/')
}

/* Google bilan kirgan hisob uchun parol o'rnatish */
async function savePassword() {
  if (pwBusy.value || pw.value.length < 8) return
  pwBusy.value = true
  pwMsg.value = ''
  try {
    await setPassword(pw.value)
    pwMsg.value = t('profile.setPwDone')
    pw.value = ''
  } catch (e) {
    pwMsg.value = e && e.code === 'weak_password' ? t('profile.setPwErr') : t('profile.setPwErr')
  } finally {
    pwBusy.value = false
  }
}
</script>

<style scoped>
.profile {
  display: grid;
  place-items: center;
  padding: 2.5rem 1rem 4rem;
}
.prof-card {
  width: min(44rem, 100%);
  padding: 1.8rem 1.5rem !important;
  animation: rise 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
}
.prof-top {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.prof-avatar {
  display: grid;
  place-items: center;
  width: 4rem;
  height: 4rem;
  flex: none;
  border-radius: 1.2rem;
  font-size: 1.6rem;
  font-weight: 700;
  color: #150a25;
  background: linear-gradient(135deg, #f5c451, #f0abfc 58%, #a78bfa);
  box-shadow: 0 16px 30px -18px rgba(167, 139, 250, 0.9);
}
.prof-kicker {
  font-size: 0.66rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(196, 181, 253, 0.8);
}
.prof-name {
  margin-top: 0.2rem;
  font-family: var(--font-display);
  font-size: 1.7rem;
  font-weight: 600;
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.prof-email {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.45);
}
.prof-stats {
  display: grid;
  gap: 0.6rem;
  grid-template-columns: repeat(auto-fit, minmax(7rem, 1fr));
  margin: 1.2rem 0;
}
@media (max-width: 520px) {
  .stat {
    padding: 0.6rem 0.5rem;
  }
  .stat b {
    font-size: 1.15rem;
  }
  .stat span {
    font-size: 0.6rem;
    letter-spacing: 0.02em;
  }
  .stat b.method {
    font-size: 0.85rem;
  }
}
.stat {
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.035);
  padding: 0.85rem 0.7rem;
  text-align: center;
}
.stat b {
  display: block;
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 600;
  color: #f5c451;
}
.stat b.method {
  font-family: var(--font-body);
  font-size: 0.8rem;
  color: #c4b5fd;
  line-height: 2.1rem;
}
.stat span {
  display: block;
  margin-top: 0.15rem;
  font-size: 0.68rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.4);
}
.prof-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}
.prof-actions .btn {
  border-radius: 0.95rem;
  padding: 0.7rem 1.1rem;
  font-size: 0.86rem;
}
.danger {
  color: #fca5a5;
  border-color: rgba(248, 113, 113, 0.25);
}
.danger:hover {
  background: rgba(248, 113, 113, 0.12);
}
.prof-note {
  margin-top: 1.2rem;
  font-size: 0.74rem;
  line-height: 1.6;
  color: rgba(245, 196, 81, 0.7);
}
</style>
