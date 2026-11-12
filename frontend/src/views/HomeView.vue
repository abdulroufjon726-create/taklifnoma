<template>
  <div class="page-bg home-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="grain"></div>
  </div>

  <SiteHeader />

  <main class="home">
    <!-- ============================= HERO ============================= -->
    <section class="hero">
      <div class="hero-copy">
        <p class="badge reveal" style="--d: 0ms">
          <span class="badge-dot"></span>{{ t('home.badge') }}
        </p>
        <h1 class="hero-title reveal" style="--d: 90ms">
          {{ t('home.titleA') }}
          <span class="grad-text shimmer">{{ t('home.titleB') }}</span>
          <br />
          <span class="script-line">{{ t('home.titleC') }}</span>
        </h1>
        <p class="hero-lead reveal" style="--d: 180ms">{{ t('home.lead') }}</p>

        <div class="hero-actions reveal" style="--d: 260ms">
          <button class="btn btn-primary hero-btn" @click="create">
            <AppIcon name="ph:sparkle" />
            {{ t('home.cta') }}
            <span class="arrow">→</span>
          </button>
          <RouterLink to="/enter" class="btn btn-ghost hero-btn">
            <AppIcon name="ph:lock-key" />
            {{ t('home.codeLink') }}
          </RouterLink>
        </div>
        <p class="hero-note reveal" style="--d: 330ms">{{ t('home.ctaSub') }}</p>
        <p v-if="loginNotice" class="hero-notice">{{ loginNotice }}</p>
      </div>

      <!-- Jonli namuna kartasi -->
      <div class="hero-art reveal" style="--d: 220ms" aria-hidden="true">
        <div class="spark s1">✦</div>
        <div class="spark s2">✧</div>
        <div class="spark s3">✦</div>
        <div class="demo-card">
          <div class="demo-env">
            <span class="env-flap"></span>
            <span class="env-seal">✦</span>
          </div>
          <p class="demo-to">{{ t('home.showTitle') }}</p>
          <p class="demo-names">Aziz &amp; Malika</p>
          <p class="demo-date">25 · 12 · 2026</p>
          <div class="demo-chips">
            <span>✦</span><span>❦</span><span>✦</span>
          </div>
        </div>
        <div class="demo-glow"></div>
      </div>
    </section>

    <!-- =========================== FEATURES =========================== -->
    <section class="features">
      <article
        v-for="(f, i) in features"
        :key="f.t"
        class="glass card feature reveal"
        :style="{ '--d': `${120 + i * 90}ms` }"
      >
        <span class="feature-icn" :class="f.tone"><AppIcon :name="f.icon" size="1.35rem" /></span>
        <h3>{{ t(f.t) }}</h3>
        <p>{{ t(f.d) }}</p>
      </article>
    </section>

    <!-- ============================ GALLERY =========================== -->
    <section class="gallery">
      <header class="sec-head">
        <h2 class="sec-title">{{ t('home.galleryTitle') }}</h2>
        <p class="sec-sub">{{ t('home.gallerySub') }}</p>
      </header>
      <div class="gallery-grid">
        <article
          v-for="(theme, i) in themes"
          :key="theme.id"
          class="theme-card reveal"
          :style="{
            '--d': `${i * 100}ms`,
            '--bg': `linear-gradient(165deg, ${theme.bg1}, ${theme.bg2} 55%, ${theme.bg3})`,
            '--ac': theme.accent,
            '--ac2': theme.accent2,
            '--tx': theme.txt,
          }"
        >
          <span class="theme-sheen"></span>
          <p class="theme-kicker">✦ INVITATION ✦</p>
          <p class="theme-names">Aziz &amp; Malika</p>
          <p class="theme-meta">25.12.2026 · 18:00</p>
          <span class="theme-name">{{ theme.name }}</span>
        </article>
      </div>
    </section>

    <!-- ============================= STEPS ============================ -->
    <section class="steps">
      <h2 class="sec-title center">{{ t('home.howTitle') }}</h2>
      <ol class="steps-list">
        <li v-for="(s, i) in steps" :key="s.t" class="step reveal" :style="{ '--d': `${i * 110}ms` }">
          <span class="step-num">{{ i + 1 }}</span>
          <div>
            <h3>{{ t(s.t) }}</h3>
            <p>{{ t(s.d) }}</p>
          </div>
        </li>
      </ol>
    </section>

    <!-- ============================== CTA ============================= -->
    <section class="cta-wrap reveal">
      <div class="glass card cta-card">
        <h2>{{ t('home.ctaTitle') }}</h2>
        <p>{{ t('home.ctaSub') }}</p>
        <button class="btn btn-primary" @click="create">
          <AppIcon name="ph:sparkle" />
          {{ auth.token ? t('home.cta') : t('nav.login') }}
        </button>
      </div>
    </section>

    <footer class="foot">
      <span class="grad-text font-display text-lg">Taklifnoma</span>
      <span class="foot-dot">✦</span>
      <span>{{ t('home.foot') }}</span>
    </footer>
  </main>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { auth, loadMe } from '../auth.js'
import { THEMES } from '../data/catalog.js'
import { useI18n } from '../i18n/index.js'
import AppIcon from '../components/AppIcon.vue'
import SiteHeader from '../components/SiteHeader.vue'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

const features = [
  { t: 'home.f1t', d: 'home.f1d', icon: 'ph:lightning', tone: 'gold' },
  { t: 'home.f2t', d: 'home.f2d', icon: 'ph:text-aa', tone: 'violet' },
  { t: 'home.f3t', d: 'home.f3d', icon: 'ph:confetti', tone: 'rose' },
]

const steps = [
  { t: 'home.s1t', d: 'home.s1d' },
  { t: 'home.s2t', d: 'home.s2d' },
  { t: 'home.s3t', d: 'home.s3d' },
]

const themes = computed(() => {
  const pick = ['gold', 'rose', 'ocean', 'night']
  return pick.map((id) => THEMES.find((x) => x.id === id)).filter(Boolean)
})

const loginNotice = computed(() => {
  if (route.query.login === '1') return t('auth.required')
  const err = route.query.auth_error
  if (!err) return ''
  if (err === 'google_not_configured') return t('auth.notConfigured')
  if (err === 'google_email') return t('login.err.invalid_email')
  return t('auth.failed')
})

onMounted(() => {
  document.title = 'Taklifnoma ✦ ' + t('home.badge')
  if (auth.token) loadMe()
})

function create() {
  router.push(auth.token ? '/create' : '/login?next=/create')
}

// til o'zgarganda sarlavha yangilanadi
watch(locale, () => {
  document.title = 'Taklifnoma ✦ ' + t('home.badge')
})
</script>

<style scoped>
.home {
  position: relative;
  z-index: 1;
  margin: 0 auto;
  max-width: 80rem;
  padding: 3rem 1.1rem 4rem;
}
@media (min-width: 640px) {
  .home {
    padding: 4rem 1.5rem 5rem;
  }
}

/* ---------- reveal animation ---------- */
.reveal {
  opacity: 0;
  transform: translateY(18px);
  animation: revealUp 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  animation-delay: var(--d, 0ms);
}
@keyframes revealUp {
  to {
    opacity: 1;
    transform: none;
  }
}

/* ---------- hero ---------- */
.hero {
  display: grid;
  gap: 2.5rem;
  align-items: center;
  padding-bottom: 3.5rem;
}
@media (min-width: 1024px) {
  .hero {
    grid-template-columns: 1.15fr 0.85fr;
    gap: 3.5rem;
    padding-bottom: 5rem;
  }
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(167, 139, 250, 0.35);
  background: rgba(167, 139, 250, 0.1);
  padding: 0.4rem 0.9rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #ddd3ff;
}
.badge-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #f5c451;
  box-shadow: 0 0 0 0 rgba(245, 196, 81, 0.6);
  animation: pulseDot 2.4s infinite;
}
@keyframes pulseDot {
  0% {
    box-shadow: 0 0 0 0 rgba(245, 196, 81, 0.55);
  }
  70% {
    box-shadow: 0 0 0 9px rgba(245, 196, 81, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(245, 196, 81, 0);
  }
}
.hero-title {
  margin: 1.1rem 0 0;
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 6vw, 4.1rem);
  line-height: 1.04;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.hero-title .shimmer {
  background-size: 200% auto;
  animation: shimmerPan 6s linear infinite;
}
@keyframes shimmerPan {
  to {
    background-position: 200% center;
  }
}
.script-line {
  font-family: var(--font-script);
  font-size: 0.78em;
  color: #ffe9a8;
  display: inline-block;
  padding-top: 0.1em;
}
.hero-lead {
  margin-top: 1.1rem;
  max-width: 34rem;
  font-size: 1.02rem;
  line-height: 1.75;
  color: rgba(255, 255, 255, 0.6);
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.8rem;
}
.hero-btn {
  border-radius: 1rem;
}
.hero-btn .arrow {
  transition: transform 0.25s;
}
.hero-btn:hover .arrow {
  transform: translateX(4px);
}
.hero-note {
  margin-top: 0.85rem;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.4);
}
.hero-notice {
  margin-top: 1rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(245, 196, 81, 0.35);
  background: rgba(245, 196, 81, 0.1);
  padding: 0.65rem 0.9rem;
  font-size: 0.8rem;
  color: #ffe9a8;
}

/* ---------- demo card ---------- */
.hero-art {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 20rem;
}
.demo-glow {
  position: absolute;
  width: 74%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(167, 139, 250, 0.35), transparent 65%);
  filter: blur(28px);
  animation: breathe 7s ease-in-out infinite;
}
@keyframes breathe {
  50% {
    transform: scale(1.12);
    opacity: 0.75;
  }
}
.demo-card {
  position: relative;
  z-index: 1;
  width: min(19rem, 78vw);
  border-radius: 1.6rem;
  padding: 1.9rem 1.5rem 1.6rem;
  text-align: center;
  background: linear-gradient(165deg, #14100a, #241b09 55%, #4a3712);
  border: 1px solid rgba(245, 196, 81, 0.35);
  box-shadow:
    0 40px 80px -50px rgba(0, 0, 0, 0.95),
    inset 0 1px 0 rgba(255, 233, 168, 0.15);
  animation: floaty 7s ease-in-out infinite;
}
@keyframes floaty {
  50% {
    transform: translateY(-12px) rotate(-0.6deg);
  }
}
.demo-env {
  position: relative;
  width: 74px;
  height: 52px;
  margin: 0 auto 1.1rem;
  border-radius: 0.55rem;
  background: linear-gradient(160deg, #f5c451, #e8b93c);
  box-shadow: 0 12px 26px -14px rgba(245, 196, 81, 0.9);
}
.env-flap {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(160deg, #ffe9a8, #f5c451);
  clip-path: polygon(0 0, 100% 0, 50% 62%);
  transform-origin: top;
  animation: flap 4.2s ease-in-out infinite;
}
@keyframes flap {
  0%,
  55%,
  100% {
    transform: rotateX(0deg);
  }
  70% {
    transform: rotateX(-155deg);
  }
}
.env-seal {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-size: 0.7rem;
  color: #4a3712;
  background: #fff7df;
  z-index: 2;
}
.demo-to {
  font-size: 0.66rem;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: rgba(253, 247, 232, 0.55);
}
.demo-names {
  margin-top: 0.5rem;
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 600;
  color: #fdf7e8;
}
.demo-date {
  margin-top: 0.35rem;
  font-size: 0.76rem;
  letter-spacing: 0.22em;
  color: #f5c451;
}
.demo-chips {
  display: flex;
  justify-content: center;
  gap: 0.9rem;
  margin-top: 1rem;
  font-size: 0.72rem;
  color: rgba(253, 247, 232, 0.45);
}
.spark {
  position: absolute;
  z-index: 2;
  color: #ffe9a8;
  font-size: 1.1rem;
  opacity: 0.85;
  animation: twinkle 3.4s ease-in-out infinite;
}
.s1 {
  top: 12%;
  left: 8%;
}
.s2 {
  top: 66%;
  right: 6%;
  animation-delay: 0.9s;
  color: #d8b4fe;
}
.s3 {
  bottom: 8%;
  left: 22%;
  animation-delay: 1.7s;
  font-size: 0.8rem;
}
@keyframes twinkle {
  0%,
  100% {
    opacity: 0.2;
    transform: scale(0.85);
  }
  50% {
    opacity: 1;
    transform: scale(1.15);
  }
}

/* ---------- features ---------- */
.features {
  display: grid;
  gap: 1rem;
  padding-bottom: 3.5rem;
}
@media (min-width: 768px) {
  .features {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.2rem;
  }
}
.feature {
  transition:
    transform 0.3s cubic-bezier(0.22, 1, 0.36, 1),
    border-color 0.3s;
}
.feature:hover {
  transform: translateY(-6px);
}
.feature-icn {
  display: grid;
  place-items: center;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 0.9rem;
  margin-bottom: 0.85rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
}
.feature-icn.gold {
  color: #f5c451;
  background: rgba(245, 196, 81, 0.13);
}
.feature-icn.violet {
  color: #c4b5fd;
  background: rgba(167, 139, 250, 0.15);
}
.feature-icn.rose {
  color: #ff9db4;
  background: rgba(255, 157, 180, 0.13);
}
.feature h3 {
  font-size: 1.02rem;
  font-weight: 600;
}
.feature p {
  margin-top: 0.45rem;
  font-size: 0.85rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.55);
}

/* ---------- gallery ---------- */
.gallery {
  padding-bottom: 3.5rem;
}
.sec-head {
  margin-bottom: 1.4rem;
}
.sec-title {
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 3.4vw, 2.2rem);
  font-weight: 600;
}
.sec-title.center {
  text-align: center;
  margin-bottom: 1.8rem;
}
.sec-sub {
  margin-top: 0.3rem;
  font-size: 0.86rem;
  color: rgba(255, 255, 255, 0.45);
}
.gallery-grid {
  display: grid;
  gap: 1rem;
}
@media (min-width: 768px) {
  .gallery-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.theme-card {
  position: relative;
  overflow: hidden;
  border-radius: 1.3rem;
  padding: 2.4rem 1.2rem 1.2rem;
  text-align: center;
  background: var(--bg);
  border: 1px solid color-mix(in srgb, var(--ac) 35%, transparent);
  color: var(--tx);
  transition:
    transform 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.35s;
}
.theme-card:nth-child(4) {
  display: none;
}
@media (min-width: 768px) {
  .theme-card:hover {
    transform: translateY(-8px) scale(1.015);
    box-shadow: 0 30px 60px -34px color-mix(in srgb, var(--ac) 55%, transparent);
  }
}
.theme-sheen {
  position: absolute;
  inset: -40% -60%;
  background: linear-gradient(115deg, transparent 40%, rgba(255, 255, 255, 0.16) 50%, transparent 60%);
  transform: translateX(-60%);
  animation: sheen 7s ease-in-out infinite;
}
@keyframes sheen {
  0%,
  65% {
    transform: translateX(-70%);
  }
  100% {
    transform: translateX(70%);
  }
}
.theme-kicker {
  position: relative;
  font-size: 0.6rem;
  letter-spacing: 0.3em;
  opacity: 0.6;
}
.theme-names {
  position: relative;
  margin-top: 0.5rem;
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 600;
  color: var(--ac2);
}
.theme-meta {
  position: relative;
  margin-top: 0.3rem;
  font-size: 0.68rem;
  letter-spacing: 0.14em;
  opacity: 0.7;
}
.theme-name {
  position: relative;
  display: inline-block;
  margin-top: 0.9rem;
  border-radius: 999px;
  padding: 0.22rem 0.7rem;
  font-size: 0.64rem;
  letter-spacing: 0.08em;
  border: 1px solid color-mix(in srgb, var(--ac) 45%, transparent);
  background: rgba(0, 0, 0, 0.25);
  opacity: 0.85;
}

/* ---------- steps ---------- */
.steps {
  padding-bottom: 3.5rem;
}
.steps-list {
  display: grid;
  gap: 1rem;
  list-style: none;
  padding: 0;
  margin: 0 auto;
  max-width: 56rem;
}
@media (min-width: 768px) {
  .steps-list {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.step {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  border-radius: 1.2rem;
  padding: 1.15rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  transition:
    border-color 0.3s,
    transform 0.3s;
}
.step:hover {
  border-color: rgba(167, 139, 250, 0.45);
  transform: translateY(-4px);
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
.step h3 {
  font-size: 0.95rem;
  font-weight: 600;
}
.step p {
  margin-top: 0.3rem;
  font-size: 0.8rem;
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.5);
}

/* ---------- cta + footer ---------- */
.cta-wrap {
  margin-bottom: 3rem;
}
.cta-card {
  text-align: center;
  padding: 2.4rem 1.5rem;
  background:
    radial-gradient(80% 120% at 50% 0%, rgba(167, 139, 250, 0.2), transparent 70%),
    linear-gradient(165deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.02));
}
.cta-card h2 {
  font-family: var(--font-display);
  font-size: clamp(1.7rem, 4vw, 2.4rem);
  font-weight: 600;
}
.cta-card p {
  margin: 0.5rem auto 1.4rem;
  max-width: 26rem;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.55);
}
.foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.35);
}
.foot-dot {
  color: #f5c451;
}

@media (prefers-reduced-motion: reduce) {
  .reveal,
  .demo-card,
  .demo-glow,
  .env-flap,
  .spark,
  .theme-sheen,
  .hero-title .shimmer,
  .badge-dot {
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}
</style>
