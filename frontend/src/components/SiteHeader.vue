<template>
  <header class="site-head">
    <div class="site-head-in">
      <RouterLink to="/" class="brand">
        <span class="brand-icn"><AppIcon name="ph:envelope-simple" size="1.35rem" /></span>
        <span class="grad-text font-display text-2xl font-semibold">Taklifnoma</span>
      </RouterLink>

      <nav class="head-nav">
        <RouterLink v-if="!onBuilder" to="/create" class="btn btn-ghost head-cta">
          <AppIcon name="ph:sparkle" />
          <span class="hidden sm:inline">{{ t('account.newBtn') }}</span>
        </RouterLink>
        <RouterLink v-if="auth.token" to="/account" class="btn btn-ghost head-cta">
          <AppIcon name="ph:user-circle" />
          <span class="hidden sm:inline">{{ t('auth.account') }}</span>
        </RouterLink>
        <LangSwitch />

        <div v-if="auth.token" class="head-user">
          <span class="avatar">{{ initial }}</span>
          <div class="hidden leading-tight sm:block">
            <p class="max-w-[9rem] truncate text-xs font-semibold text-white/90">{{ name }}</p>
            <button class="text-[0.68rem] text-white/45 transition hover:text-white/80" @click="logout">
              {{ t('auth.logout') }}
            </button>
          </div>
        </div>
        <button v-else class="btn btn-primary head-login" @click="startLogin">
          <AppIcon name="ph:google-logo" />
          <span class="hidden sm:inline">{{ t('auth.googleBtn') }}</span>
          <span class="sm:hidden">Google</span>
        </button>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { auth, signIn, signOut } from '../auth.js'
import { useI18n } from '../i18n/index.js'
import AppIcon from './AppIcon.vue'
import LangSwitch from './LangSwitch.vue'

const { t } = useI18n()
const route = useRoute()

const onBuilder = computed(() => route.name === 'builder')
const name = computed(() => auth.user?.name || auth.user?.email || '')
const initial = computed(() => (name.value || '?').trim().charAt(0).toUpperCase())

function startLogin() {
  signIn('/create')
}

async function logout() {
  await signOut()
  if (route.name === 'account' || route.name === 'builder') {
    window.location.href = '/'
  }
}
</script>

<style scoped>
.site-head {
  position: sticky;
  top: 0;
  z-index: 40;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(10, 9, 18, 0.72);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}
.site-head-in {
  margin: 0 auto;
  display: flex;
  height: 4rem;
  max-width: 80rem;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0 1rem;
}
@media (min-width: 640px) {
  .site-head-in {
    padding: 0 1.5rem;
  }
}
.brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.brand-icn {
  display: grid;
  place-items: center;
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 0.8rem;
  color: #c4b5fd;
  background: linear-gradient(140deg, rgba(167, 139, 250, 0.28), rgba(232, 121, 249, 0.16));
  border: 1px solid rgba(167, 139, 250, 0.4);
}
.head-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.head-cta {
  padding: 0.55rem 0.85rem !important;
  font-size: 0.82rem;
  border-radius: 0.9rem;
}
/* Tor ekranda sarlavhadagi qo'shimcha tugmalar sig'maydi — yashiriladi */
@media (max-width: 639px) {
  .head-cta {
    display: none;
  }
  .site-head-in {
    padding: 0 0.8rem;
  }
  .head-nav {
    gap: 0.35rem;
  }
  .head-login {
    padding: 0.55rem 0.75rem !important;
    font-size: 0.78rem;
  }
}
.head-login {
  padding: 0.6rem 1rem !important;
  font-size: 0.85rem;
  border-radius: 0.95rem;
}
.head-user {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding-left: 0.35rem;
}
.avatar {
  display: grid;
  place-items: center;
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: 700;
  color: #150a25;
  background: linear-gradient(135deg, #f5c451, #f0abfc 60%, #a78bfa);
  box-shadow: 0 6px 18px -8px rgba(167, 139, 250, 0.9);
}
</style>
