<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="grain"></div>
  </div>

  <SiteHeader />

  <main class="login-wrap">
    <div class="login-card glass">
      <!-- Chap panel: brend -->
      <aside class="login-side">
        <span class="side-glow"></span>
        <div class="side-env" aria-hidden="true">
          <span class="side-flap"></span>
          <span class="side-seal">✦</span>
        </div>
        <p class="side-kicker">✦ Taklifnoma</p>
        <h2 class="side-title">Har bir lahzani<br />chiroyli ulashing</h2>
        <ul class="side-list">
          <li><AppIcon name="ph:lightning" /> Tez ochiladigan taklifnomalar</li>
          <li><AppIcon name="ph:text-aa" /> 5 xil shrift, har matnga alohida</li>
          <li><AppIcon name="ph:device-mobile" /> Barcha qurilmalarda saqlanadi</li>
        </ul>
      </aside>

      <!-- O'ng panel: forma -->
      <section class="login-form">
        <p class="form-kicker">{{ t('login.kicker') }}</p>
        <h1 class="form-title">{{ t('login.title') }}</h1>
        <p class="form-sub">{{ t('login.sub') }}</p>

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
      </section>
    </div>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
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

const mode = ref('login')
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

function toggleMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  errorMsg.value = ''
}

function google() {
  if (!authConfig.google) return
  signIn(target)
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
    const code = e && e.code ? e.code : 'default'
    const key = 'login.err.' + code
    const msg = t(key)
    errorMsg.value = msg === key ? t('login.err.default') : msg
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  display: grid;
  place-items: center;
  padding: 2.5rem 1rem 3.5rem;
}
.login-card {
  display: grid;
  width: min(64rem, 100%);
  overflow: hidden;
  border-radius: 1.6rem;
  padding: 0 !important;
  animation: cardIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
}
@media (min-width: 900px) {
  .login-card {
    grid-template-columns: 1fr 1.05fr;
  }
}

/* chap panel */
.login-side {
  position: relative;
  display: none;
  overflow: hidden;
  padding: 2.6rem 2.2rem;
  background:
    radial-gradient(90% 80% at 20% 0%, rgba(167, 139, 250, 0.3), transparent 65%),
    radial-gradient(80% 90% at 100% 100%, rgba(245, 196, 81, 0.18), transparent 60%),
    #120f22;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
}
@media (min-width: 900px) {
  .login-side {
    display: block;
  }
}
.side-glow {
  position: absolute;
  width: 18rem;
  height: 18rem;
  right: -6rem;
  bottom: -7rem;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(232, 121, 249, 0.35), transparent 65%);
  filter: blur(18px);
  animation: breathe 8s ease-in-out infinite;
}
@keyframes breathe {
  50% {
    transform: scale(1.15);
    opacity: 0.7;
  }
}
.side-env {
  position: relative;
  width: 84px;
  height: 58px;
  margin-bottom: 1.6rem;
  border-radius: 0.6rem;
  background: linear-gradient(160deg, #f5c451, #e8b93c);
  box-shadow: 0 16px 30px -16px rgba(245, 196, 81, 0.85);
  animation: floaty 6s ease-in-out infinite;
}
@keyframes floaty {
  50% {
    transform: translateY(-8px);
  }
}
.side-flap {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(160deg, #ffe9a8, #f5c451);
  clip-path: polygon(0 0, 100% 0, 50% 62%);
  transform-origin: top;
  animation: flap 5s ease-in-out infinite;
}
@keyframes flap {
  0%,
  60%,
  100% {
    transform: rotateX(0deg);
  }
  74% {
    transform: rotateX(-150deg);
  }
}
.side-seal {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.72rem;
  color: #4a3712;
  background: #fff7df;
  z-index: 2;
}
.side-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(255, 233, 168, 0.7);
}
.side-title {
  margin-top: 0.6rem;
  font-family: var(--font-display);
  font-size: 1.9rem;
  line-height: 1.2;
  font-weight: 600;
}
.side-list {
  margin-top: 1.6rem;
  display: grid;
  gap: 0.7rem;
  padding: 0;
  list-style: none;
  font-size: 0.84rem;
  color: rgba(255, 255, 255, 0.62);
}
.side-list li {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}
.side-list :deep(svg) {
  color: #f5c451;
}

/* forma */
.login-form {
  padding: 2rem 1.5rem 1.8rem;
}
@media (min-width: 640px) {
  .login-form {
    padding: 2.6rem 2.4rem 2.2rem;
  }
}
.form-kicker {
  font-size: 0.66rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(196, 181, 253, 0.8);
}
.form-title {
  margin-top: 0.35rem;
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.2;
}
.form-sub {
  margin-top: 0.5rem;
  font-size: 0.83rem;
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.5);
}
.google-btn {
  width: 100%;
  margin-top: 1.4rem;
  border-radius: 1rem;
  font-size: 0.9rem;
  color: #fff;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.15);
}
.google-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
}
.google-off {
  opacity: 0.55;
  cursor: not-allowed;
}
.google-off:hover {
  transform: none;
  background: rgba(255, 255, 255, 0.07);
}
.google-note {
  margin-top: 0.5rem;
  font-size: 0.72rem;
  line-height: 1.55;
  color: rgba(245, 196, 81, 0.75);
}
.or {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin: 1.2rem 0;
  font-size: 0.7rem;
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
  gap: 0.75rem;
}
.flabel {
  display: grid;
  gap: 0.3rem;
  font-size: 0.74rem;
  letter-spacing: 0.05em;
  color: rgba(255, 255, 255, 0.5);
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
  margin-top: 0.35rem;
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
  margin-top: 1.3rem;
  font-size: 0.76rem;
  color: rgba(255, 255, 255, 0.35);
  transition: color 0.2s;
}
.back-link:hover {
  color: #fff;
}

@media (prefers-reduced-motion: reduce) {
  .side-env,
  .side-flap,
  .side-glow,
  .login-card {
    animation: none;
  }
}
</style>
