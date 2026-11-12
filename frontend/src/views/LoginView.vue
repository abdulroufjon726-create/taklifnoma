<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="grain"></div>
  </div>

  <SiteHeader />

  <main class="auth-wrap">
    <div class="glass card auth-card">
      <p class="auth-kicker">
        {{ mode === 'register' ? t('loginExtra.registerKicker') : t('loginExtra.loginKicker') }}
      </p>
      <h1 class="auth-title">{{ t('login.title') }}</h1>
      <p class="auth-sub">{{ t('login.sub') }}</p>

      <button
        class="btn google-btn"
        type="button"
        :class="{ 'google-off': !authConfig.google }"
        @click="google"
      >
        <AppIcon name="ph:google-logo" />
        {{ t('login.google') }}
      </button>
      <p v-if="!authConfig.google" class="google-note">{{ t('login.googleOff') }}</p>

      <div class="or"><span>{{ t('login.or') }}</span></div>

      <form class="email-form" @submit.prevent="submit">
        <label v-if="mode === 'register'" class="flabel">
          <span>{{ t('login.name') }}</span>
          <input v-model="form.name" class="field" type="text" autocomplete="name" placeholder="Aziz Karimov" />
        </label>
        <label class="flabel">
          <span>{{ t('login.email') }}</span>
          <input
            v-model="form.email"
            class="field"
            type="email"
            inputmode="email"
            autocomplete="email"
            placeholder="siz@email.com"
            required
          />
        </label>
        <label class="flabel">
          <span>{{ t('login.password') }}</span>
          <input
            v-model="form.password"
            class="field"
            type="password"
            :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
            placeholder="••••••••"
            required
          />
        </label>

        <p v-if="expired && !errorMsg" class="form-note">{{ t('loginExtra.expired') }}</p>
        <p v-if="errorMsg" class="form-err">{{ errorMsg }}</p>

        <button class="btn btn-primary submit" type="submit" :disabled="busy">
          {{ busy ? t('login.working') : mode === 'login' ? t('login.signIn') : t('login.signUp') }}
        </button>
      </form>

      <p class="switch">
        {{ mode === 'login' ? t('login.noAccount') : t('login.haveAccount') }}
        <button type="button" @click="toggleMode">
          {{ mode === 'login' ? t('login.signUp') : t('login.signIn') }}
        </button>
      </p>

      <RouterLink to="/" class="back-link">← {{ t('login.back') }}</RouterLink>
    </div>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  auth,
  authConfig,
  loadAuthConfig,
  passwordLogin,
  registerAccount,
  signIn,
} from '../auth.js'
import { useI18n } from '../i18n/index.js'
import AppIcon from '../components/AppIcon.vue'
import SiteHeader from '../components/SiteHeader.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const mode = ref(route.name === 'register' ? 'register' : 'login')
const expired = ref(route.query.expired === '1')
const busy = ref(false)
const errorMsg = ref('')
const form = reactive({ name: '', email: '', password: '' })

const target = (() => {
  const next = route.query.next
  return typeof next === 'string' && next.startsWith('/') && !next.startsWith('//')
    ? next
    : '/envelopes'
})()

onMounted(async () => {
  document.title = 'Taklifnoma ✦ ' + t('login.title')
  await loadAuthConfig()
  if (auth.token) router.replace(target)
})

watch(
  () => route.name,
  (name) => {
    mode.value = name === 'register' ? 'register' : 'login'
    errorMsg.value = ''
  },
)

function toggleMode() {
  router.replace({ path: mode.value === 'login' ? '/register' : '/login', query: route.query })
}

function google() {
  if (!authConfig.google) return
  signIn(target)
}

function errorText(code) {
  if (code === 'too_many_attempts') return t('loginExtra.tooMany')
  const key = 'login.err.' + code
  const msg = t(key)
  return msg === key ? t('login.err.default') : msg
}

async function submit() {
  if (busy.value) return
  errorMsg.value = ''
  busy.value = true
  try {
    if (mode.value === 'login') {
      await passwordLogin(form.email.trim(), form.password)
    } else {
      await registerAccount(form.name.trim(), form.email.trim(), form.password)
    }
    router.replace(target)
  } catch (e) {
    errorMsg.value = errorText(e && e.code ? e.code : 'default')
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.auth-wrap {
  display: grid;
  place-items: center;
  padding: 2.5rem 1rem 3.5rem;
}
.auth-card {
  width: min(26rem, 100%);
  padding: 1.9rem 1.5rem 1.7rem !important;
  animation: cardIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
}
.auth-kicker {
  font-size: 0.66rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(196, 181, 253, 0.8);
}
.auth-title {
  margin-top: 0.3rem;
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 600;
  line-height: 1.25;
}
.auth-sub {
  margin-top: 0.45rem;
  font-size: 0.82rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.5);
}
.google-btn {
  width: 100%;
  margin-top: 1.2rem;
  border-radius: 1rem;
  font-size: 0.88rem;
  color: #fff;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.15);
}
.google-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}
.google-off {
  opacity: 0.55;
  cursor: not-allowed;
}
.google-off:hover {
  background: rgba(255, 255, 255, 0.07);
}
.google-note {
  margin-top: 0.45rem;
  font-size: 0.72rem;
  line-height: 1.5;
  color: rgba(245, 196, 81, 0.75);
}
.or {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin: 1.1rem 0;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: rgba(255, 255, 255, 0.3);
}
.or::before,
.or::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}
.email-form {
  display: grid;
  gap: 0.7rem;
}
.flabel {
  display: grid;
  gap: 0.3rem;
  font-size: 0.74rem;
  letter-spacing: 0.05em;
  color: rgba(255, 255, 255, 0.5);
}
.form-note {
  border-radius: 0.8rem;
  border: 1px solid rgba(245, 196, 81, 0.35);
  background: rgba(245, 196, 81, 0.1);
  padding: 0.55rem 0.75rem;
  font-size: 0.78rem;
  color: #f5c451;
}
.form-err {
  border-radius: 0.8rem;
  border: 1px solid rgba(248, 113, 113, 0.35);
  background: rgba(248, 113, 113, 0.1);
  padding: 0.55rem 0.75rem;
  font-size: 0.78rem;
  color: #fca5a5;
}
.submit {
  width: 100%;
  margin-top: 0.3rem;
  border-radius: 1rem;
}
.switch {
  margin-top: 1rem;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.45);
}
.switch button {
  margin-left: 0.3rem;
  font-weight: 600;
  color: #c4b5fd;
  background: none;
  border: none;
  cursor: pointer;
}
.switch button:hover {
  color: #f5c451;
}
.back-link {
  display: inline-block;
  margin-top: 1.1rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.35);
}
.back-link:hover {
  color: #fff;
}
</style>
