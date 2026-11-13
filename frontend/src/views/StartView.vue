<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="grain"></div>
  </div>

  <SiteHeader />

  <main class="start">
    <header class="start-head">
      <p class="start-kicker">{{ t('start.kicker') }}</p>
      <h1 class="start-title">{{ t('start.title') }}</h1>
      <p class="start-sub">{{ t('start.sub') }}</p>
    </header>

    <ol class="steps">
      <li v-for="(s, i) in steps" :key="s.t" class="step" :style="{ '--d': `${i * 110}ms` }">
        <span class="step-num">{{ i + 1 }}</span>
        <div>
          <h2>{{ t(s.t) }}</h2>
          <p>{{ t(s.d) }}</p>
        </div>
      </li>
    </ol>

    <div class="start-actions">
      <RouterLink v-if="auth.token" to="/create" class="btn btn-primary">
        <AppIcon name="ph:sparkle" />
        {{ t('start.ctaLogged') }}
      </RouterLink>
      <RouterLink v-else :to="{ path: '/register', query: { next: '/create' } }" class="btn btn-primary">
        <AppIcon name="ph:user-plus" />
        {{ t('start.cta') }}
      </RouterLink>
      <RouterLink to="/enter" class="btn btn-ghost">
        <AppIcon name="ph:lock-key" />
        {{ t('start.codeLink') }}
      </RouterLink>
    </div>

    <section class="faq">
      <h2 class="faq-title">{{ t('start.faq') }}</h2>
      <div class="faq-grid">
        <div v-for="n in 3" :key="n" class="glass card faq-card">
          <p class="faq-q">{{ t('start.q' + n) }}</p>
          <p class="faq-a">{{ t('start.a' + n) }}</p>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { onMounted } from 'vue'

import { auth, loadMe } from '../auth.js'
import { useI18n } from '../i18n/index.js'
import AppIcon from '../components/AppIcon.vue'
import SiteHeader from '../components/SiteHeader.vue'

const { t } = useI18n()

const steps = [
  { t: 'start.s1t', d: 'start.s1d' },
  { t: 'start.s2t', d: 'start.s2d' },
  { t: 'start.s3t', d: 'start.s3d' },
]

onMounted(() => {
  document.title = 'Taklifnoma ✦ ' + t('start.title')
  if (auth.token) loadMe()
})
</script>

<style scoped>
.start {
  position: relative;
  z-index: 1;
  margin: 0 auto;
  max-width: 62rem;
  padding: 2.6rem 1.1rem 4rem;
}
@media (min-width: 640px) {
  .start {
    padding: 3.4rem 1.5rem 5rem;
  }
}
.start-head {
  text-align: center;
  margin-bottom: 2rem;
}
.start-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: rgba(196, 181, 253, 0.8);
}
.start-title {
  margin-top: 0.45rem;
  font-family: var(--font-display);
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 600;
}
.start-sub {
  margin: 0.5rem auto 0;
  max-width: 32rem;
  font-size: 0.9rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.52);
}
.steps {
  display: grid;
  gap: 0.9rem;
  padding: 0;
  margin: 0;
  list-style: none;
}
@media (min-width: 820px) {
  .steps {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.step {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  border-radius: 1.2rem;
  padding: 1.15rem;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.035);
  opacity: 0;
  transform: translateY(14px);
  animation: rise 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  animation-delay: var(--d, 0ms);
  transition:
    border-color 0.3s,
    transform 0.3s;
}
.step:hover {
  border-color: rgba(167, 139, 250, 0.45);
  transform: translateY(-4px);
}
@keyframes rise {
  to {
    opacity: 1;
    transform: none;
  }
}
.step-num {
  display: grid;
  place-items: center;
  flex: none;
  width: 2rem;
  height: 2rem;
  border-radius: 0.7rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: #efe9ff;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.4), rgba(232, 121, 249, 0.25));
  border: 1px solid rgba(167, 139, 250, 0.45);
}
.step h2 {
  font-size: 0.98rem;
  font-weight: 600;
}
.step p {
  margin-top: 0.3rem;
  font-size: 0.82rem;
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.52);
}
.start-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.7rem;
  margin: 2rem 0 2.6rem;
}
.faq-title {
  margin-bottom: 0.9rem;
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 600;
  text-align: center;
}
.faq-grid {
  display: grid;
  gap: 0.8rem;
}
@media (min-width: 820px) {
  .faq-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.faq-card {
  padding: 1.1rem 1rem;
}
.faq-q {
  font-size: 0.9rem;
  font-weight: 600;
}
.faq-a {
  margin-top: 0.35rem;
  font-size: 0.8rem;
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.5);
}
@media (prefers-reduced-motion: reduce) {
  .step {
    animation: none;
    opacity: 1;
    transform: none;
  }
}

/* ---- Bitta ekran ---- */
.start {
  display: flex;
  flex-direction: column;
  gap: clamp(0.6rem, 1.6vh, 1rem);
  padding: clamp(0.8rem, 2.2vh, 1.5rem) 1rem clamp(0.6rem, 1.8vh, 1rem);
}
.start-head {
  margin-bottom: 0.2rem;
}
.start-title {
  font-size: clamp(1.5rem, min(5.4vh, 4.4vw), 2.6rem);
}
.start-sub {
  font-size: clamp(0.78rem, 1.5vh, 0.9rem);
}
.start .step {
  padding: 0.65rem 0.75rem;
}
.start .step h3 {
  font-size: 0.88rem;
}
.start .step p {
  font-size: 0.74rem;
  line-height: 1.35;
}
.start .faq {
  margin: 0;
}
.start .faq-grid {
  gap: 0.6rem;
}
.start .faq-card {
  padding: 0.65rem 0.75rem;
  font-size: 0.76rem;
}
.start .start-actions {
  margin-top: 0.2rem;
}
@media (max-width: 820px) {
  .start .faq-grid {
    grid-template-columns: 1fr;
  }
  .start .faq-card {
    padding: 0.55rem 0.65rem;
  }
}
</style>
