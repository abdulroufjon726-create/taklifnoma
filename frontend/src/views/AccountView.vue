<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="grain"></div>
  </div>

  <SiteHeader />

  <main class="acct">
    <header class="acct-head">
      <div>
        <p class="acct-kicker">{{ t('auth.account') }}</p>
        <h1 class="acct-title">{{ t('account.title') }}</h1>
        <p class="acct-sub">{{ t('account.sub') }}</p>
      </div>
      <div class="acct-actions">
        <span v-if="items.length" class="count-pill">{{ tf('account.count', { n: items.length }) }}</span>
        <RouterLink to="/create" class="btn btn-primary">
          <AppIcon name="ph:plus" />
          {{ t('account.newBtn') }}
        </RouterLink>
      </div>
    </header>

    <!-- Yuklanmoqda -->
    <div v-if="loading" class="grid-cards">
      <div v-for="n in 3" :key="n" class="skeleton"></div>
    </div>

    <!-- Xato -->
    <div v-else-if="error" class="glass card state-card">
      <AppIcon name="ph:warning-circle" size="1.8rem" class="text-amber-300" />
      <p>{{ t('account.err') }}</p>
      <button class="btn btn-ghost" @click="load">{{ t('account.retry') }}</button>
    </div>

    <!-- Bo'sh -->
    <div v-else-if="!items.length" class="glass card state-card empty-card">
      <span class="empty-icn"><AppIcon name="ph:envelope-simple" size="1.6rem" /></span>
      <h2>{{ t('account.empty') }}</h2>
      <p>{{ t('account.emptySub') }}</p>
      <RouterLink to="/create" class="btn btn-primary">
        <AppIcon name="ph:sparkle" />
        {{ t('account.newBtn') }}
      </RouterLink>
    </div>

    <!-- Kartalar: ekran eniga 3 ta -->
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
          @click="open(inv)"
          @keydown.enter.prevent="open(inv)"
          @keydown.space.prevent="open(inv)"
        >
          <span class="sheen"></span>
          <p class="card-kicker">✦ INVITATION</p>
          <p class="card-names" :style="{ fontFamily: fontStack(inv.fonts?.names) }">
            {{ inv.first_name }} {{ inv.last_name }}
          </p>
          <p class="card-text" :style="{ fontFamily: fontStack(inv.fonts?.salute) }">
            {{ firstText(inv) }}
          </p>
          <div class="card-meta">
            <span>{{ formatDate(inv.event_at) }}</span>
            <span class="card-code">{{ prettyCode(inv.code) }}</span>
          </div>
          <span class="card-views">
            <AppIcon name="ph:eye" size="0.9em" /> {{ inv.views }}
          </span>
        </article>
      </div>
      <p class="hint">{{ t('account.editHint') }}</p>
    </template>
  </main>

  <!-- ============ Pop-up: tahrirlash / o'chirish ============ -->
  <Teleport to="body">
    <div v-if="selected" class="modal-backdrop" @click.self="closeModal">
        <div class="modal" role="dialog" aria-modal="true">
          <button class="modal-x" :aria-label="t('account.close')" @click="closeModal">✕</button>

          <div class="modal-preview" :style="previewStyle(selected)">
            <span class="sheen"></span>
            <p class="card-kicker">✦ INVITATION ✦</p>
            <p class="card-names big" :style="{ fontFamily: fontStack(selected.fonts?.names) }">
              {{ selected.first_name }} {{ selected.last_name }}
            </p>
            <p class="modal-to" :style="{ fontFamily: fontStack(selected.fonts?.to || selected.fonts?.from) }">
              {{ selected.to_name }}
            </p>
            <p class="modal-date">{{ formatDate(selected.event_at) }}</p>
            <p v-if="selected.place" class="modal-place">{{ selected.place }}</p>
          </div>

          <div class="modal-body">
            <div class="modal-facts">
              <span class="fact"><b>{{ prettyCode(selected.code) }}</b> · code</span>
              <span class="fact">{{ tf('account.views', { n: selected.views }) }}</span>
            </div>

            <template v-if="!confirming">
              <div class="modal-actions">
                <button class="btn btn-primary" @click="edit(selected)">
                  <AppIcon name="ph:pencil-simple" />
                  {{ t('account.edit') }}
                </button>
                <button class="btn btn-danger" @click="confirming = true">
                  <AppIcon name="ph:trash" />
                  {{ t('account.delete') }}
                </button>
              </div>
              <RouterLink :to="`/i/${selected.code}`" class="modal-open">
                {{ t('account.open') }} →
              </RouterLink>
            </template>

            <div v-else class="confirm">
              <p class="confirm-title">{{ t('account.confirm') }}</p>
              <p class="confirm-sub">{{ t('account.confirmSub') }}</p>
              <div class="modal-actions">
                <button class="btn btn-danger" :disabled="deleting" @click="remove(selected)">
                  {{ deleting ? t('account.deleting') : t('account.delete') }}
                </button>
                <button class="btn btn-ghost" :disabled="deleting" @click="confirming = false">
                  {{ t('account.cancel') }}
                </button>
              </div>
            </div>
          </div>
        </div>
    </div>
  </Teleport>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { deleteInvitation, fetchMyInvitations } from '../api.js'
import { auth, loadMe, signIn } from '../auth.js'
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
const leaving = ref(new Set())

function themeOf(id) {
  return THEMES.find((x) => x.id === id) || THEMES[0]
}

function firstText(inv) {
  const list = Array.isArray(inv.texts) ? inv.texts : []
  return list.find((x) => x && x.trim()) || ''
}

function cardStyle(inv, i) {
  const th = themeOf(inv.theme)
  return {
    '--d': `${Math.min(i, 8) * 70}ms`,
    '--bg': `linear-gradient(168deg, ${th.bg1}, ${th.bg2} 58%, ${th.bg3})`,
    '--ac': th.accent,
    '--ac2': th.accent2,
    '--tx': th.txt,
  }
}

function previewStyle(inv) {
  return cardStyle(inv, 0)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [list] = await Promise.all([fetchMyInvitations(), auth.user ? null : loadMe()])
    items.value = list
  } catch (e) {
    error.value = e?.message || 'error'
  } finally {
    loading.value = false
  }
}

function open(inv) {
  selected.value = inv
  confirming.value = false
}

function closeModal() {
  selected.value = null
  confirming.value = false
}

function edit(inv) {
  router.push({ path: '/create', query: { edit: inv.code } })
}

async function remove(inv) {
  deleting.value = true
  try {
    await deleteInvitation(inv.code)
    leaving.value.add(inv.code)
    setTimeout(() => {
      items.value = items.value.filter((x) => x.code !== inv.code)
      leaving.value.delete(inv.code)
    }, 260)
    selected.value = null
    confirming.value = false
  } catch {
    error.value = 'delete'
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  document.title = 'Taklifnoma ✦ ' + t('account.title')
  if (!auth.token) {
    router.replace({ path: '/', query: { login: '1', next: '/account' } })
    return
  }
  load()
})

watch(locale, () => {
  document.title = 'Taklifnoma ✦ ' + t('account.title')
})
</script>

<style scoped>
.acct {
  position: relative;
  z-index: 1;
  margin: 0 auto;
  max-width: 80rem;
  padding: 2.4rem 1.1rem 4rem;
}
@media (min-width: 640px) {
  .acct {
    padding: 3rem 1.5rem 5rem;
  }
}
.acct-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.2rem;
  margin-bottom: 2rem;
}
.acct-kicker {
  font-size: 0.7rem;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: rgba(196, 181, 253, 0.8);
}
.acct-title {
  margin-top: 0.35rem;
  font-family: var(--font-display);
  font-size: clamp(1.9rem, 4.4vw, 2.8rem);
  font-weight: 600;
}
.acct-sub {
  margin-top: 0.4rem;
  max-width: 32rem;
  font-size: 0.88rem;
  color: rgba(255, 255, 255, 0.5);
}
.acct-actions {
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

/* ---- 3 ta karta bir qatorda ---- */
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

.inv-card {
  position: relative;
  overflow: hidden;
  border-radius: 1.25rem;
  padding: 1.5rem 1.2rem 1.2rem;
  background: var(--bg);
  border: 1px solid color-mix(in srgb, var(--ac) 32%, transparent);
  color: var(--tx);
  cursor: pointer;
  text-align: left;
  opacity: 0;
  transform: translateY(16px);
  animation: cardIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  animation-delay: var(--d, 0ms);
  transition:
    transform 0.3s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.3s,
    border-color 0.3s;
  outline: none;
}
@keyframes cardIn {
  to {
    opacity: 1;
    transform: none;
  }
}
.inv-card:hover,
.inv-card:focus-visible {
  transform: translateY(-6px);
  border-color: color-mix(in srgb, var(--ac) 65%, transparent);
  box-shadow: 0 26px 50px -30px color-mix(in srgb, var(--ac) 70%, transparent);
}
.inv-card.leaving {
  opacity: 0 !important;
  transform: scale(0.92) !important;
  transition: all 0.25s ease;
}
.sheen {
  position: absolute;
  inset: -40% -60%;
  background: linear-gradient(115deg, transparent 42%, rgba(255, 255, 255, 0.14) 50%, transparent 58%);
  transform: translateX(-70%);
  pointer-events: none;
}
.inv-card:hover .sheen,
.modal-preview:hover .sheen {
  animation: sheenMove 1.1s ease;
}
@keyframes sheenMove {
  to {
    transform: translateX(70%);
  }
}
.card-kicker {
  position: relative;
  font-size: 0.58rem;
  letter-spacing: 0.3em;
  opacity: 0.55;
}
.card-names {
  position: relative;
  margin-top: 0.55rem;
  font-size: 1.28rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--ac2);
}
.card-names.big {
  font-size: 1.8rem;
}
.card-text {
  position: relative;
  margin-top: 0.35rem;
  font-size: 0.85rem;
  opacity: 0.72;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  position: relative;
  margin-top: 1.1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.4rem;
  font-size: 0.7rem;
  opacity: 0.68;
}
.card-code {
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--ac) 45%, transparent);
  background: rgba(0, 0, 0, 0.25);
  padding: 0.15rem 0.55rem;
  letter-spacing: 0.12em;
}
.card-views {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  border-radius: 999px;
  padding: 0.2rem 0.5rem;
  font-size: 0.66rem;
  background: rgba(0, 0, 0, 0.28);
  border: 1px solid rgba(255, 255, 255, 0.1);
  opacity: 0.8;
}
.hint {
  margin-top: 1.1rem;
  font-size: 0.76rem;
  color: rgba(255, 255, 255, 0.35);
}

/* ---- states ---- */
.skeleton {
  height: 12.5rem;
  border-radius: 1.25rem;
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

/* ---- modal ---- */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(6, 5, 12, 0.68);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
.modal {
  position: relative;
  width: min(30rem, 100%);
  max-height: 92vh;
  overflow: auto;
  border-radius: 1.5rem;
  background: #12101f;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 50px 100px -40px rgba(0, 0, 0, 0.95);
}
.modal-x {
  position: absolute;
  top: 0.7rem;
  right: 0.7rem;
  z-index: 3;
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.35);
  color: #fff;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s;
}
.modal-x:hover {
  background: rgba(255, 255, 255, 0.16);
}
.modal-preview {
  position: relative;
  overflow: hidden;
  padding: 1.8rem 1.4rem 1.5rem;
  text-align: center;
  background: var(--bg);
  color: var(--tx);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.modal-to {
  position: relative;
  margin-top: 0.4rem;
  font-size: 0.9rem;
  opacity: 0.75;
}
.modal-date {
  position: relative;
  margin-top: 0.6rem;
  font-size: 0.72rem;
  letter-spacing: 0.16em;
  color: var(--ac);
}
.modal-place {
  position: relative;
  margin-top: 0.25rem;
  font-size: 0.7rem;
  opacity: 0.55;
}
.modal-body {
  padding: 1.2rem 1.3rem 1.4rem;
}
.modal-facts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.fact {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  padding: 0.25rem 0.65rem;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.6);
}
.fact b {
  letter-spacing: 0.12em;
  color: #f5c451;
}
.modal-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}
.modal-actions .btn {
  flex: 1 1 8rem;
  padding: 0.75rem 1rem;
  font-size: 0.88rem;
  border-radius: 0.95rem;
}
.btn-danger {
  color: #fff;
  background: linear-gradient(135deg, #ef4444, #b91c1c);
  box-shadow: 0 12px 26px -14px rgba(239, 68, 68, 0.8);
}
.btn-danger:hover:not(:disabled) {
  transform: translateY(-2px);
}
.modal-open {
  display: inline-block;
  margin-top: 0.9rem;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.2s;
}
.modal-open:hover {
  color: #f5c451;
}
.confirm {
  border-radius: 1rem;
  border: 1px solid rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.08);
  padding: 0.9rem;
}
.confirm-title {
  font-size: 0.92rem;
  font-weight: 600;
}
.confirm-sub {
  margin: 0.25rem 0 0.75rem;
  font-size: 0.78rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.55);
}

/* ---- modal kirish animatsiyasi (chiqishi darhol) ---- */
.modal-backdrop {
  animation: backdropIn 0.22s ease both;
}
.modal {
  animation: modalIn 0.3s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes backdropIn {
  from {
    opacity: 0;
  }
}
@keyframes modalIn {
  from {
    opacity: 0;
    transform: translateY(14px) scale(0.96);
  }
}

@media (prefers-reduced-motion: reduce) {
  .inv-card,
  .skeleton {
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}
</style>
