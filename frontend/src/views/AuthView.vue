<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="grain"></div>
  </div>
  <div class="grid min-h-screen place-items-center px-5">
    <div class="glass card auth-card w-full max-w-sm text-center">
      <div class="auth-spinner mx-auto mb-5"></div>
      <p class="text-sm text-white/70">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { loadMe, saveToken } from '../auth.js'
import { useI18n } from '../i18n/index.js'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const message = ref(t('auth.signingIn'))

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token : ''
  const next = typeof route.query.next === 'string' && route.query.next.startsWith('/')
    ? route.query.next
    : '/account'

  if (!token) {
    message.value = t('auth.failed')
    setTimeout(() => router.replace('/'), 1200)
    return
  }

  saveToken(token)
  await loadMe()
  router.replace(next)
})
</script>

<style scoped>
.auth-card {
  padding: 2.4rem 1.8rem;
}
.auth-spinner {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.15);
  border-top-color: #f5c451;
  animation: authSpin 0.9s linear infinite;
}
@keyframes authSpin {
  to {
    transform: rotate(360deg);
  }
}
</style>
