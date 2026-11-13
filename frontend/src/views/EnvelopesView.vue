<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="grain"></div>
  </div>

  <SiteHeader />

  <main class="envs">
    <header class="envs-head">
      <div>
        <p class="envs-kicker">{{ t('nav.envelopes') }}</p>
        <h1 class="envs-title">{{ t('envelopes.title') }}</h1>
        <p class="envs-sub">{{ t('envelopes.sub') }}</p>
      </div>
      <div class="envs-actions">
        <span v-if="items.length" class="count-pill">{{ tf('envelopes.count', { n: items.length }) }}</span>
        <RouterLink to="/create" class="btn btn-primary">
          <AppIcon name="ph:sparkle" />
          {{ t('envelopes.newBtn') }}
        </RouterLink>
      </div>
    </header>

    <div v-if="loading" class="grid-cards">
      <div v-for="n in 3" :key="n" class="skeleton"></div>
    </div>

    <div v-else-if="error" class="glass card state-card">
      <AppIcon name="ph:warning-circle" size="1.8rem" class="text-amber-300" />
      <p>{{ t('envelopes.err') }}</p>
      <button class="btn btn-ghost" @click="load">{{ t('envelopes.retry') }}</button>
    </div>

    <div v-else-if="!items.length" class="glass card state-card empty-card">
      <span class="empty-icn"><AppIcon name="ph:envelope-simple" size="1.6rem" /></span>
      <h2>{{ t('envelopes.empty') }}</h2>
      <p>{{ t('envelopes.emptySub') }}</p>
      <RouterLink to="/create" class="btn btn-primary">
        <AppIcon name="ph:sparkle" />
        {{ t('envelopes.newBtn') }}
      </RouterLink>
    </div>

    <template v-else>
      <div class="grid-cards">
        <article
          v-for="(inv, i) in items"
          :key="inv.code"
          class="inv-card"
          :class="{ leaving: leaving.has(inv.code) }"
          :style="cardStyle(inv, i)"
          role="button"
          tabindex="0"
          :aria-label="`${inv.first_name} ${inv.last_name} — ${prettyCode(inv.code)}`"
          @click="openSheet(inv)"
          @keydown.enter.prevent="openSheet(inv)"
          @keydown.space.prevent="openSheet(inv)"
        >
          <span class="card-glow"></span>
          <span class="sheen"></span>

          <div class="card-top">
            <p class="card-kicker">✦ INVITATION</p>
            <span class="card-views">
              <svg class="glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
                <path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6S2 12 2 12Z" />
                <circle cx="12" cy="12" r="2.6" />
              </svg>
              {{ inv.views }}
            </span>
          </div>

          <p class="card-names" :style="{ fontFamily: fontStack(inv.fonts?.names) }">
            {{ inv.first_name }} {{ inv.last_name }}
          </p>
          <p v-if="firstText(inv)" class="card-text">{{ firstText(inv) }}</p>

          <div class="card-foot">
            <span class="card-date"><AppIcon name="ph:calendar-blank" size="0.9em" /> {{ formatDate(inv.event_at) }}</span>
            <span class="card-code">{{ prettyCode(inv.code) }}</span>
          </div>

          <span v-if="inv.legacy" class="legacy-badge">{{ t('legacy.badge') }}</span>
          <span class="card-cta">
            <svg class="glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M7 17 17 7M9 7h8v8" />
            </svg>
          </span>
        </article>
      </div>
      <p class="hint">{{ t('envelopes.hint') }}</p>
    </template>
  </main>

  <Teleport to="body">
    <div v-if="selected" class="sheet-backdrop" @click.self="closeSheet">
        <div
          class="sheet"
          role="dialog"
          aria-modal="true"
          :style="cardStyle(selected, 0)"
        >
          <span class="sheet-decor" aria-hidden="true">
            <span class="sheet-aura aura-a"></span>
            <span class="sheet-aura aura-b"></span>
          </span>

          <button class="sheet-x" :aria-label="t('account.close')" @click="closeSheet">✕</button>

          <div class="sheet-body">
            <!-- Taklifnoma ko'rinishi -->
            <div class="pv">
              <span class="pv-orb pv-orb-a"></span>
              <span class="pv-orb pv-orb-b"></span>
              <p class="pv-kicker">✦ INVITATION ✦</p>
              <p class="pv-names" :style="{ fontFamily: fontStack(selected.fonts?.names) }">
                {{ selected.first_name }} {{ selected.last_name }}
              </p>
              <p v-if="selected.to_name" class="pv-to">{{ selected.to_name }}</p>
              <p class="pv-date">{{ formatDate(selected.event_at) }}</p>
              <p v-if="selected.place" class="pv-place">
                <AppIcon name="ph:map-pin" size="0.9em" /> {{ selected.place }}
              </p>
            </div>

            <!-- Boshqaruv -->
            <div class="pane">
              <div class="pane-head">
                <p class="pane-kicker">{{ t('envelope.details') }}</p>
                <button class="copy-code" type="button" @click="copyLink(selected)">
                  <span>{{ prettyCode(selected.code) }}</span>
                  <svg
                    v-if="copied === selected.code"
                    class="glyph"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="m5 13 4 4L19 7" />
                  </svg>
                  <svg
                    v-else
                    class="glyph"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.7"
                  >
                    <rect x="9" y="9" width="11" height="11" rx="2.2" />
                    <path d="M15 5.5H6.5A2.5 2.5 0 0 0 4 8v8.5" />
                  </svg>
                </button>
              </div>

              <dl class="facts">
                <div>
                  <dt>{{ t('envelope.date') }}</dt>
                  <dd>{{ formatDate(selected.event_at) }}</dd>
                </div>
                <div v-if="selected.place">
                  <dt>{{ t('envelope.place') }}</dt>
                  <dd class="clamp">{{ selected.place }}</dd>
                </div>
                <div v-if="selected.to_name">
                  <dt>{{ t('envelope.to') }}</dt>
                  <dd class="clamp">{{ selected.to_name }}</dd>
                </div>
                <div>
                  <dt>{{ t('envelope.views') }}</dt>
                  <dd>{{ selected.views }}</dd>
                </div>
              </dl>

              <template v-if="!confirming">
                <div class="pane-actions">
                  <button class="lq-btn lq-primary" type="button" @click="edit(selected)">
                    <svg class="glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M4 20h4L18.5 9.5a2.1 2.1 0 0 0-3-3L5 17v3Z" />
                      <path d="M14.5 5.5l3 3" />
                    </svg>
                    {{ t('account.edit') }}
                  </button>
                  <RouterLink :to="`/i/${selected.code}`" class="lq-btn lq-glass">
                    <svg class="glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M7 17 17 7M9 7h8v8" />
                    </svg>
                    {{ t('envelope.open') }}
                  </RouterLink>
                  <button class="lq-btn lq-danger" type="button" @click="confirming = true">
                    <svg class="glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M4 7h16M9.5 7V5h5v2M6.5 7l1 13h9l1-13" />
                    </svg>
                    {{ t('account.delete') }}
                  </button>
                </div>
              </template>

              <div v-else class="confirm">
                <p class="confirm-title">{{ t('account.confirm') }}</p>
                <p class="confirm-sub">{{ t('account.confirmSub') }}</p>
                <p v-if="deleteError" class="confirm-error">{{ deleteError }}</p>
                <div class="pane-actions">
                  <button class="lq-btn lq-danger" type="button" :disabled="deleting" @click="remove(selected)">
                    {{ deleting ? t('account.deleting') : t('account.delete') }}
                  </button>
                  <button class="lq-btn lq-glass" type="button" :disabled="deleting" @click="confirming = false">
                    {{ t('account.cancel') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>
  </Teleport>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { claimInvitation, copyText, deleteInvitation, fetchMyInvitations, shareUrl } from '../api.js'
import { auth, loadMe } from '../auth.js'
import { listMine, removeMine } from '../data/mine.js'
import { THEMES, fontStack, prettyCode } from '../data/catalog.js'
import { formatDate, useI18n } from '../i18n/index.js'
import AppIcon from '../components/AppIcon.vue'
import SiteHeader from '../components/SiteHeader.vue'

const { t, tf, locale } = useI18n()
const router = useRouter()

const items = ref([])
const loading = ref(true)
const error = ref('')
const selected = ref(null)
const confirming = ref(false)
const deleting = ref(false)
const copied = ref('')
const deleteError = ref('')
const leaving = ref(new Set())
let copiedTimer = null

function firstText(inv) {
  const list = Array.isArray(inv.texts) ? inv.texts : []
  return list.find((x) => x && x.trim()) || ''
}

function cardStyle(inv, i) {
  const th = THEMES.find((x) => x.id === inv.theme) || THEMES[0]
  return {
    '--d': `${Math.min(i, 8) * 70}ms`,
    '--bg': `linear-gradient(168deg, ${th.bg1}, ${th.bg2} 58%, ${th.bg3})`,
    '--ac': th.accent,
    '--ac2': th.accent2,
    '--tx': th.txt,
  }
}

/* Login'dan oldin yaratilgan (egasiz) taklifnoma yozuvini karta shakliga
   aylantiradi — u faqat shu qurilmada, edit_key bilan tahrirlanadi. */
function legacyToInvitation(entry) {
  const p = entry.payload || {}
  const date = p.date || ''
  const time = p.time || '18:00'
  const parsed = date ? new Date(`${date}T${time}:00`) : new Date(entry.updated_at || Date.now())
  const iso = Number.isNaN(parsed.getTime()) ? new Date().toISOString() : parsed.toISOString()
  return {
    code: entry.code,
    first_name: p.first_name || '',
    last_name: p.last_name || '',
    to_name: p.to_name || '',
    from_name: p.from_name || '',
    event_at: iso,
    place: p.place || '',
    theme: p.theme || 'gold',
    texts: Array.isArray(p.texts) ? p.texts : [],
    fonts: p.fonts || {},
    ambient_effects: p.ambient_effects || [],
    particle_effects: p.particle_effects || [],
    views: 0,
    created_at: new Date(entry.updated_at || Date.now()).toISOString(),
    legacy: true,
    editKey: entry.editKey || '',
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [list] = await Promise.all([fetchMyInvitations(), auth.user ? null : loadMe()])

    // Shu qurilmada saqlangan, hali egasi yo'q taklifnomalar
    const local = listMine()
    const known = new Set(list.map((i) => i.code))
    const pending = local.filter((e) => !known.has(e.code))

    // Kaliti borlarini hisobga avtomatik bog'laymiz.
    // 409 = boshqa hisobga tegishli -> bu ro'yxatda ko'rsatilmaydi.
    const foreign = new Set()
    await Promise.all(
      pending.map(async (e) => {
        try {
          await claimInvitation(e.code, e.editKey)
        } catch (err) {
          if (err && err.status === 409) foreign.add(e.code)
          /* qolgan holatlarda pastda lokal karta sifatida ko'rsatamiz */
        }
      }),
    )

    let merged = list
    if (pending.length) {
      try {
        merged = await fetchMyInvitations()
      } catch {
        /* eski ro'yxat bilan davom etamiz */
      }
    }

    const after = new Set(merged.map((i) => i.code))
    const extras = pending
      .filter((e) => !after.has(e.code) && !foreign.has(e.code))
      .map(legacyToInvitation)
    items.value = [...merged, ...extras]
  } catch (e) {
    if (e && (e.status === 401 || e.status === 403)) {
      const expired = e.status === 401 ? '1' : ''
      router.replace({ path: '/login', query: { next: '/envelopes', expired } })
      return
    }
    error.value = e?.message || 'error'
  } finally {
    loading.value = false
  }
}

function openSheet(inv) {
  selected.value = inv
  confirming.value = false
  deleteError.value = ''
  copied.value = ''
  document.body.style.overflow = 'hidden'
}

function closeSheet() {
  selected.value = null
  confirming.value = false
  deleteError.value = ''
  document.body.style.overflow = ''
}

const edit = (inv) => router.push({ path: '/create', query: { edit: inv.code } })

async function copyLink(inv) {
  const ok = await copyText(shareUrl(inv.code))
  if (!ok) return
  copied.value = inv.code
  clearTimeout(copiedTimer)
  copiedTimer = setTimeout(() => (copied.value = ''), 1800)
}

async function remove(inv) {
  deleting.value = true
  try {
    await deleteInvitation(inv.code, inv.editKey || '')
    if (inv.legacy) removeMine(inv.code)
    leaving.value.add(inv.code)
    setTimeout(() => {
      items.value = items.value.filter((x) => x.code !== inv.code)
      leaving.value.delete(inv.code)
    }, 260)
    closeSheet()
  } catch (e) {
    deleteError.value = e?.message || t('envelopes.err')
  } finally {
    deleting.value = false
  }
}

function onKey(e) {
  if (e.key !== 'Escape') return
  if (selected.value) closeSheet()
}

onMounted(() => {
  document.title = 'Taklifnoma ✦ ' + t('envelopes.title')
  if (!auth.token) {
    router.replace({ path: '/login', query: { next: '/envelopes' } })
    return
  }
  window.addEventListener('keydown', onKey)
  load()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
  clearTimeout(copiedTimer)
})

watch(locale, () => {
  document.title = 'Taklifnoma ✦ ' + t('envelopes.title')
})
</script>

<style scoped>
.envs {
  position: relative;
  z-index: 1;
  margin: 0 auto;
  max-width: 80rem;
  padding: 1.2rem 1.1rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.envs > .grid-cards {
  min-height: 0;
  align-content: start;
}
@media (min-width: 640px) {
  .envs {
    padding: 1.4rem 1.5rem 1.6rem;
  }
}
.envs-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.2rem;
  margin-bottom: 1.1rem;
}
@media (max-height: 760px) {
  .envs-title {
    font-size: clamp(1.4rem, 3vh, 2rem);
  }
  .envs-sub {
    display: none;
  }
}
.envs-kicker {
  font-size: 0.7rem;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: rgba(196, 181, 253, 0.8);
}
.envs-title {
  margin-top: 0.35rem;
  font-family: var(--font-display);
  font-size: clamp(1.9rem, 4.4vw, 2.8rem);
  font-weight: 600;
}
.envs-sub {
  margin-top: 0.4rem;
  max-width: 32rem;
  font-size: 0.88rem;
  color: rgba(255, 255, 255, 0.5);
}
.envs-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.count-pill {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.4rem 0.85rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.65);
}

/* 3 ta karta bir qatorda */
.grid-cards {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}
@media (min-width: 640px) {
  .grid-cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (min-width: 1024px) {
  .grid-cards {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.3rem;
  }
}

/* ---- Karta ------------------------------------------------------------ */
.inv-card {
  position: relative;
  isolation: isolate;
  min-width: 0;
  overflow: hidden;
  border-radius: 1.4rem;
  padding: 1.35rem 1.15rem 1.1rem;
  background: var(--bg);
  border: 1px solid color-mix(in srgb, var(--ac) 34%, transparent);
  color: var(--tx);
  cursor: pointer;
  text-align: left;
  opacity: 0;
  transform: translateY(16px);
  animation: cardIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  animation-delay: var(--d, 0ms);
  transition:
    transform 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.35s,
    border-color 0.35s;
  outline: none;
}
@keyframes cardIn {
  to {
    opacity: 1;
    transform: none;
  }
}
.card-glow {
  position: absolute;
  inset: -30% -20% auto -20%;
  height: 70%;
  z-index: -1;
  background: radial-gradient(60% 70% at 30% 0%, color-mix(in srgb, var(--ac) 45%, transparent), transparent 70%);
  opacity: 0.45;
  transition: opacity 0.35s;
}
.inv-card:hover,
.inv-card:focus-visible {
  transform: translateY(-6px);
  border-color: color-mix(in srgb, var(--ac) 70%, transparent);
  box-shadow:
    0 28px 55px -30px color-mix(in srgb, var(--ac) 75%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.22);
}
.inv-card:hover .card-glow {
  opacity: 0.8;
}
.inv-card.leaving {
  opacity: 0 !important;
  transform: scale(0.92) !important;
  transition: all 0.25s ease;
}
.sheen {
  position: absolute;
  inset: -40% -60%;
  background: linear-gradient(115deg, transparent 42%, rgba(255, 255, 255, 0.16) 50%, transparent 58%);
  transform: translateX(-70%);
  pointer-events: none;
}
.inv-card:hover .sheen {
  animation: sheenMove 1.1s ease;
}
@keyframes sheenMove {
  to {
    transform: translateX(70%);
  }
}
.card-top {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
}
.card-kicker {
  font-size: 0.56rem;
  letter-spacing: 0.3em;
  opacity: 0.55;
}
.card-views {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  border-radius: 999px;
  padding: 0.16rem 0.5rem;
  font-size: 0.64rem;
  background: rgba(0, 0, 0, 0.26);
  border: 1px solid rgba(255, 255, 255, 0.12);
  opacity: 0.85;
}
.card-names {
  position: relative;
  margin-top: 0.7rem;
  min-width: 0;
  font-size: 1.3rem;
  font-weight: 600;
  line-height: 1.22;
  color: var(--ac2);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere;
}
.card-text {
  position: relative;
  margin-top: 0.4rem;
  font-size: 0.83rem;
  line-height: 1.5;
  opacity: 0.72;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-foot {
  position: relative;
  margin-top: 1.15rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.45rem;
  font-size: 0.7rem;
}
.card-date {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  opacity: 0.7;
}
.card-code {
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--ac) 45%, transparent);
  background: rgba(0, 0, 0, 0.28);
  padding: 0.16rem 0.55rem;
  letter-spacing: 0.14em;
  opacity: 0.9;
}
.card-cta {
  position: absolute;
  right: 1rem;
  bottom: 2.9rem;
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  opacity: 0;
  transform: translateY(6px);
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  backdrop-filter: blur(6px);
}
.inv-card:hover .card-cta,
.inv-card:focus-visible .card-cta {
  opacity: 1;
  transform: none;
}
.hint {
  margin-top: 1.1rem;
  font-size: 0.76rem;
  color: rgba(255, 255, 255, 0.35);
}
.legacy-badge {
  position: absolute;
  top: 0.75rem;
  left: 0;
  border-radius: 0 999px 999px 0;
  padding: 0.12rem 0.55rem;
  font-size: 0.58rem;
  background: rgba(0, 0, 0, 0.4);
  color: var(--ac);
}

.skeleton {
  height: 12.5rem;
  border-radius: 1.4rem;
  background: linear-gradient(100deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.09), rgba(255, 255, 255, 0.04));
  background-size: 220% 100%;
  animation: shimmer 1.4s linear infinite;
}
@keyframes shimmer {
  to {
    background-position: -120% 0;
  }
}
.state-card {
  display: grid;
  place-items: center;
  gap: 0.7rem;
  padding: 3rem 1.4rem;
  text-align: center;
}
.state-card h2 {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 600;
}
.state-card p {
  max-width: 24rem;
  font-size: 0.86rem;
  color: rgba(255, 255, 255, 0.5);
}
.empty-icn {
  display: grid;
  place-items: center;
  width: 3.2rem;
  height: 3.2rem;
  border-radius: 1rem;
  color: #f5c451;
  background: rgba(245, 196, 81, 0.12);
  border: 1px solid rgba(245, 196, 81, 0.35);
}

/* ---- Liquid glass popup ---------------------------------------------- */
.sheet-backdrop {
  position: fixed;
  inset: 0;
  animation: fadeIn 0.2s ease both;
  z-index: 60;
  display: grid;
  place-items: center;
  padding: clamp(0.8rem, 3vw, 2rem);
  background:
    radial-gradient(60% 60% at 20% 15%, rgba(124, 58, 237, 0.28), transparent 70%),
    radial-gradient(55% 55% at 85% 85%, rgba(236, 72, 153, 0.22), transparent 70%),
    rgba(6, 5, 12, 0.55);
  backdrop-filter: blur(14px) saturate(140%);
  -webkit-backdrop-filter: blur(14px) saturate(140%);
}
.sheet {
  position: relative;
  width: min(56rem, 100%);
  animation: sheetIn 0.34s cubic-bezier(0.22, 1, 0.36, 1) both;
  max-height: 92vh;
  overflow: auto;
  padding: clamp(1rem, 2.4vw, 1.6rem);
  border-radius: 2rem;
  color: #fff;
  background: linear-gradient(
    142deg,
    rgba(255, 255, 255, 0.2) 0%,
    rgba(255, 255, 255, 0.06) 38%,
    rgba(255, 255, 255, 0.03) 62%,
    rgba(255, 255, 255, 0.14) 100%
  );
  border: 1px solid rgba(255, 255, 255, 0.26);
  backdrop-filter: blur(30px) saturate(180%);
  -webkit-backdrop-filter: blur(30px) saturate(180%);
  box-shadow:
    0 60px 120px -45px rgba(0, 0, 0, 0.9),
    0 0 0 1px rgba(255, 255, 255, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.55),
    inset 0 -1px 0 rgba(255, 255, 255, 0.14),
    inset 0 35px 60px -50px rgba(255, 255, 255, 0.9);
  isolation: isolate;
}
.sheet::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  border-radius: inherit;
  background: radial-gradient(120% 90% at 8% -10%, rgba(255, 255, 255, 0.35), transparent 45%);
  opacity: 0.55;
  pointer-events: none;
}
/* Dekor qatlami alohida: scroll maydonini kattalashtirmaydi */
.sheet-decor {
  position: absolute;
  inset: 0;
  z-index: -2;
  overflow: hidden;
  border-radius: inherit;
  pointer-events: none;
}
.sheet-aura {
  position: absolute;
  border-radius: 50%;
  filter: blur(46px);
  pointer-events: none;
}
.aura-a {
  width: 22rem;
  height: 22rem;
  top: -8rem;
  left: -6rem;
  background: color-mix(in srgb, var(--ac2) 46%, transparent);
  opacity: 0.5;
}
.aura-b {
  width: 20rem;
  height: 20rem;
  right: -6rem;
  bottom: -9rem;
  background: color-mix(in srgb, var(--ac) 50%, transparent);
  opacity: 0.42;
}
.sheet-x {
  position: absolute;
  top: 0.9rem;
  right: 0.9rem;
  z-index: 4;
  display: grid;
  place-items: center;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  color: #fff;
  font-size: 0.95rem;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(12px);
  transition:
    background 0.2s,
    transform 0.2s;
}
.sheet-x:hover {
  background: rgba(255, 255, 255, 0.28);
  transform: rotate(90deg);
}
.sheet-body {
  display: grid;
  gap: clamp(1rem, 2.4vw, 1.6rem);
  align-items: stretch;
}
@media (min-width: 780px) {
  .sheet-body {
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
  }
}

/* Taklifnoma ko'rinishi (tema ranglarida) */
.pv {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: 15rem;
  padding: 1.6rem 1.3rem 1.4rem;
  border-radius: 1.5rem;
  background: var(--bg);
  color: var(--tx);
  border: 1px solid color-mix(in srgb, var(--ac) 38%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.24),
    0 30px 60px -40px rgba(0, 0, 0, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}
.pv-orb {
  position: absolute;
  z-index: -1;
  border-radius: 50%;
  filter: blur(30px);
}
.pv-orb-a {
  width: 12rem;
  height: 12rem;
  top: -4rem;
  left: -3rem;
  background: color-mix(in srgb, var(--ac) 55%, transparent);
  opacity: 0.5;
}
.pv-orb-b {
  width: 11rem;
  height: 11rem;
  right: -3rem;
  bottom: -4rem;
  background: color-mix(in srgb, var(--ac2) 50%, transparent);
  opacity: 0.45;
}
.pv-kicker {
  font-size: 0.6rem;
  letter-spacing: 0.34em;
  opacity: 0.6;
}
.pv-names {
  margin-top: 0.7rem;
  font-size: clamp(1.5rem, 3.4vw, 2rem);
  font-weight: 600;
  line-height: 1.18;
  color: var(--ac2);
  overflow-wrap: anywhere;
}
.pv-to {
  margin-top: 0.3rem;
  font-size: 0.82rem;
  opacity: 0.7;
}
.pv-date {
  margin-top: 1rem;
  font-size: 0.74rem;
  letter-spacing: 0.14em;
  color: var(--ac);
}
.pv-place {
  margin-top: 0.3rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  opacity: 0.62;
}

/* Boshqaruv paneli */
.pane {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 0.2rem 0.15rem;
}
.pane-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding-right: 2.4rem;
}
.pane-kicker {
  font-size: 0.66rem;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.55);
}
.copy-code {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 999px;
  padding: 0.32rem 0.7rem;
  font-size: 0.74rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  color: #ffe5a3;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: rgba(255, 255, 255, 0.1);
  transition: background 0.2s;
}
.copy-code:hover {
  background: rgba(255, 255, 255, 0.2);
}
.facts {
  display: grid;
  gap: 0.5rem;
  margin: 1rem 0 0;
}
.facts div {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.9rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
}
.facts dt {
  flex: none;
  font-size: 0.64rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.48);
}
.facts dd {
  margin: 0;
  min-width: 0;
  font-size: 0.84rem;
  text-align: right;
  color: rgba(255, 255, 255, 0.9);
}
.facts dd.clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere;
}
.pane-actions {
  margin-top: auto;
  padding-top: 1.2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}
.lq-btn {
  position: relative;
  display: inline-flex;
  flex: 1 1 7.5rem;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  white-space: nowrap;
  padding: 0.72rem 0.9rem;
  border-radius: 999px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.26);
  transition:
    transform 0.2s,
    background 0.2s,
    box-shadow 0.2s;
}
.lq-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}
.lq-btn:disabled {
  opacity: 0.6;
  cursor: default;
}
.lq-primary {
  color: #1a1206;
  border-color: rgba(255, 255, 255, 0.5);
  background: linear-gradient(140deg, #ffe9b0, #f5c451 55%, #e0a93a);
  box-shadow:
    0 14px 30px -16px rgba(245, 196, 81, 0.85),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}
.lq-glass {
  color: #fff;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
}
.lq-glass:hover {
  background: rgba(255, 255, 255, 0.22);
}
.lq-danger {
  color: #ffd9d9;
  border-color: rgba(255, 120, 120, 0.35);
  background: rgba(220, 38, 38, 0.22);
  backdrop-filter: blur(10px);
}
.lq-danger:hover {
  background: rgba(220, 38, 38, 0.36);
}

.confirm {
  margin-top: 1rem;
  border-radius: 1.1rem;
  border: 1px solid rgba(255, 140, 140, 0.34);
  background: rgba(220, 38, 38, 0.14);
  padding: 0.85rem 0.9rem;
}
.confirm-title {
  font-size: 0.9rem;
  font-weight: 600;
}
.confirm-sub {
  margin: 0.25rem 0 0;
  font-size: 0.76rem;
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.66);
}
.confirm-error {
  margin: 0.4rem 0 0;
  font-size: 0.76rem;
  color: #ffb4b4;
}
.confirm .pane-actions {
  padding-top: 0.8rem;
}

/* Ochilish animatsiyasi (chiqishda darhol yopiladi) */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
}
@keyframes sheetIn {
  from {
    opacity: 0;
    transform: translateY(18px) scale(0.96);
  }
}

.glyph {
  width: 1em;
  height: 1em;
  flex: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

@media (max-width: 779px) {
  .sheet {
    border-radius: 1.6rem;
    padding: 0.9rem;
  }
  .pv {
    min-height: 10.5rem;
    padding: 1.1rem 1rem 1rem;
  }
  .pv-names {
    font-size: 1.35rem;
  }
  .pane {
    padding: 0;
  }
  .facts {
    margin-top: 0.8rem;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem 0.9rem;
  }
  .facts div {
    display: block;
    border-bottom: 0;
    padding-bottom: 0;
  }
  .facts dt {
    font-size: 0.58rem;
  }
  .facts dd {
    margin-top: 0.15rem;
    text-align: left;
    font-size: 0.8rem;
  }
  .pane-actions {
    padding-top: 0.9rem;
  }
  .lq-btn {
    font-size: 0.8rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .inv-card,
  .skeleton,
  .sheet,
  .sheet-backdrop {
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
    transition: none !important;
  }
}
</style>
