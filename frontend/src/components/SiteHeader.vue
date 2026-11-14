<template>
  <header class="site-head">
    <div class="site-head-in">
      <RouterLink to="/" class="brand">
        <span class="brand-icn"><AppIcon name="ph:envelope-simple" size="1.35rem" /></span>
        <span class="grad-text font-display text-2xl font-semibold">Taklifnoma</span>
      </RouterLink>

      <nav class="head-nav">
        <RouterLink to="/" class="nav-link">{{ t('nav.home') }}</RouterLink>
        <RouterLink to="/start" class="nav-link">{{ t('nav.howTo') }}</RouterLink>
        <RouterLink v-if="auth.token" to="/envelopes" class="nav-link">
          {{ t('nav.envelopes') }}
        </RouterLink>
        <LangSwitch />

        <RouterLink v-if="auth.token" to="/account" class="head-user" :title="name">
          <span class="avatar">{{ initial }}</span>
          <div class="hidden leading-tight sm:block">
            <p class="max-w-[9rem] truncate text-xs font-semibold text-white/90">{{ name }}</p>
            <span class="text-[0.68rem] text-white/45">{{ t('nav.account') }}</span>
          </div>
        </RouterLink>
        <RouterLink v-else :to="registerTo" class="btn btn-primary head-login">
          <AppIcon name="ph:user-plus" />
          <span class="hidden sm:inline">{{ t('nav.register') }}</span>
          <span class="sm:hidden">{{ t('nav.login') }}</span>
        </RouterLink>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { auth, loadMe } from '../auth.js'
import { useI18n } from '../i18n/index.js'
import AppIcon from './AppIcon.vue'
import LangSwitch from './LangSwitch.vue'

const { t } = useI18n()
const route = useRoute()

const onBuilder = computed(() => route.name === 'builder')

// Sahifa foydalanuvchini o'zi yuklamasa ham avatar/ism to'g'ri ko'rinadi
onMounted(() => {
  if (auth.token && !auth.user) loadMe()
})
const name = computed(() => auth.user?.name || auth.user?.email || '')
const initial = computed(() => (name.value || '?').trim().charAt(0).toUpperCase())
const registerTo = computed(() => ({ path: '/register', query: { next: '/envelopes' } }))
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
.nav-link {
  display: none;
  padding: 0.35rem 0.2rem;
  font-size: 0.84rem;
  color: rgba(255, 255, 255, 0.62);
  text-decoration: none;
  transition: color 0.2s;
}
.nav-link:hover {
  color: #fff;
}
.nav-link.router-link-active {
  color: #f5c451;
}
@media (min-width: 900px) {
  .nav-link {
    display: inline-block;
    margin-right: 0.5rem;
  }
}
/* Tor ekranda sarlavhadagi qo'shimcha tugmalar sig'maydi — yashiriladi */
@media (max-width: 639px) {
  .site-head-in {
    padding: 0 0.55rem;
  }
  .head-nav {
    gap: 0.2rem;
  }
  .head-login {
    padding: 0.5rem 0.55rem !important;
    font-size: 0.76rem;
  }
  .head-login :deep(.icn) {
    display: none;
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
  border-radius: 0.9rem;
  text-decoration: none;
  transition: opacity 0.2s;
}
.head-user:hover {
  opacity: 0.85;
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
