<template>
  <div class="page-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="grain"></div>
  </div>

  <SiteHeader />

  <main class="env">
    <header class="env-head">
      <RouterLink to="/envelopes" class="back">← {{ t('envelope.back') }}</RouterLink>
      <div class="env-actions">
        <RouterLink v-if="inv" :to="`/i/${inv.code}`" class="btn btn-ghost">
          <AppIcon name="ph:arrow-up-right" />
          {{ t('envelope.open') }}
        </RouterLink>
        <RouterLink v-if="inv" :to="`/create?edit=${inv.code}`" class="btn btn-primary">
          <AppIcon name="ph:pencil-simple" />
          {{ t('envelope.edit') }}
        </RouterLink>
        <button v-if="inv" class="btn btn-danger" @click="confirming = true">
          <AppIcon name="ph:trash" />
          {{ t('envelope.delete') }}
        </button>
      </div>
    </header>

    <div v-if="loading" class="glass card state-card">
      <div class="spinner"></div>
      <p>{{ t('envelopes.loading') }}</p>
    </div>

    <div v-else-if="!inv" class="glass card state-card">
      <AppIcon name="ph:envelope-open" size="1.9rem" class="text-amber-300" />
      <p>{{ t('envelope.notFound') }}</p>
      <RouterLink to="/envelopes" class="btn btn-primary">{{ t('envelope.back') }}</RouterLink>
    </div>

    <template v-else>
      <div class="env-grid">
        <!-- Jonli ko'rinish -->
        <section class="preview-card">
          <p class="preview-label">{{ t('envelope.preview') }}</p>
          <div class="preview-box">
            <InvitationStage :data="inv" />
          </div>
        </section>

        <!-- Tafsilotlar -->
        <aside class="glass card details">
          <h1 class="details-title" :style="{ fontFamily: fontStack(inv.fonts?.names) }">
            {{ inv.first_name }} {{ inv.last_name }}
          </h1>
          <p class="details-code">{{ t('envelope.code') }}: <b>{{ prettyCode(inv.code) }}</b></p>

          <dl class="facts">
            <div>
              <dt>{{ t('envelope.date') }}</dt>
              <dd>{{ formatDate(inv.event_at) }}</dd>
            </div>
            <div v-if="inv.place">
              <dt>{{ t('envelope.place') }}</dt>
              <dd>{{ inv.place }}</dd>
            </div>
            <div>
              <dt>{{ t('envelope.to') }}</dt>
              <dd>{{ inv.to_name }}</dd>
            </div>
            <div>
              <dt>{{ t('envelope.from') }}</dt>
              <dd>{{ inv.from_name }}</dd>
            </div>
            <div>
              <dt>{{ t('envelope.views') }}</dt>
              <dd>{{ inv.views }}</dd>
            </div>
            <div>
              <dt>{{ t('envelope.created') }}</dt>
              <dd>{{ formatDate(inv.created_at) }}</dd>
            </div>
          </dl>

          <div v-if="texts.length" class="texts">
            <p class="sub-title">{{ t('envelope.texts') }}</p>
            <p
              v-for="(line, i) in texts"
              :key="i"
              class="text-line"
              :style="textStyle(i)"
            >
              {{ line }}
            </p>
          </div>

          <div class="design">
            <p class="sub-title">{{ t('envelope.design') }}</p>
            <div class="chips">
              <span class="dchip">{{ themeName }}</span>
              <span v-for="e in effects" :key="e" class="dchip">{{ e }}</span>
            </div>
          </div>
        </aside>
      </div>
    </template>
  </main>

  <Teleport to="body">
    <div v-if="confirming" class="modal-backdrop" @click.self="confirming = false">
      <div class="modal" role="dialog" aria-modal="true">
        <p class="confirm-title">{{ t('envelope.confirm') }}</p>
        <p class="confirm-sub">{{ t('envelope.confirmSub') }}</p>
        <div class="confirm-actions">
          <button class="btn btn-danger" :disabled="deleting" @click="remove">
            {{ deleting ? t('envelope.deleting') : t('envelope.delete') }}
          </button>
          <button class="btn btn-ghost" :disabled="deleting" @click="confirming = false">
            {{ t('envelope.cancel') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { deleteInvitation, fetchMyInvitations } from '../api.js'
import { auth } from '../auth.js'
import { THEMES, fontStack, prettyCode } from '../data/catalog.js'
import { formatDate, useI18n } from '../i18n/index.js'
import AppIcon from '../components/AppIcon.vue'
import InvitationStage from '../components/InvitationStage.vue'
import SiteHeader from '../components/SiteHeader.vue'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

const inv = ref(null)
const loading = ref(true)
const confirming = ref(false)
const deleting = ref(false)

const texts = computed(() => (Array.isArray(inv.value?.texts) ? inv.value.texts : []))
const effects = computed(() => [
  ...(inv.value?.ambient_effects || []),
  ...(inv.value?.particle_effects || []),
])
const themeName = computed(
  () => (THEMES.find((x) => x.id === inv.value?.theme) || THEMES[0]).name,
)

function textStyle(i) {
  const stack = fontStack((inv.value?.fonts?.texts || [])[i])
  return stack ? { fontFamily: stack } : {}
}

async function load() {
  loading.value = true
  try {
    const list = await fetchMyInvitations()
    const code = String(route.params.code || '').toUpperCase()
    inv.value = list.find((x) => x.code === code) || null
  } catch (e) {
    if (e && (e.status === 401 || e.status === 403)) {
      const expired = e.status === 401 ? '1' : ''
      router.replace({ path: '/login', query: { next: route.fullPath, expired } })
      return
    }
    inv.value = null
  } finally {
    loading.value = false
  }
}

async function remove() {
  if (!inv.value) return
  deleting.value = true
  try {
    await deleteInvitation(inv.value.code)
    router.replace('/envelopes')
  } catch {
    deleting.value = false
    confirming.value = false
  }
}

onMounted(() => {
  document.title = 'Taklifnoma ✦ ' + t('envelope.details')
  if (!auth.token) {
    router.replace({ path: '/login', query: { next: route.fullPath } })
    return
  }
  load()
})

watch(
  () => route.params.code,
  () => {
    if (auth.token) load()
  },
)

watch(locale, () => {
  document.title = 'Taklifnoma ✦ ' + t('envelope.details')
})
</script>

<style scoped>
.env {
  position: relative;
  z-index: 1;
  margin: 0 auto;
  max-width: 80rem;
  padding: 1.6rem 1.1rem 4rem;
}
@media (min-width: 640px) {
  .env {
    padding: 2rem 1.5rem 5rem;
  }
}
.env-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  margin-bottom: 1.4rem;
}
.back {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.2s;
}
.back:hover {
  color: #f5c451;
}
.env-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.env-actions .btn {
  border-radius: 0.9rem;
  padding: 0.62rem 1rem;
  font-size: 0.82rem;
}
.btn-danger {
  color: #fff;
  background: linear-gradient(135deg, #ef4444, #b91c1c);
  box-shadow: 0 12px 26px -14px rgba(239, 68, 68, 0.8);
}
.btn-danger:hover:not(:disabled) {
  transform: translateY(-2px);
}

.env-grid {
  display: grid;
  gap: 1.2rem;
  align-items: start;
}
@media (min-width: 1024px) {
  .env-grid {
    grid-template-columns: 1.15fr 0.85fr;
  }
}

.preview-card {
  min-width: 0;
}
.preview-label {
  margin-bottom: 0.5rem;
  font-size: 0.68rem;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.4);
}
.preview-box {
  position: relative;
  height: clamp(28rem, 68vh, 44rem);
  overflow: hidden;
  border-radius: 1.4rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 40px 80px -50px rgba(0, 0, 0, 0.95);
}

.details {
  padding: 1.5rem 1.3rem;
  animation: rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
}
.details-title {
  font-size: 1.6rem;
  font-weight: 600;
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.details-code {
  margin-top: 0.35rem;
  font-size: 0.74rem;
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.45);
}
.details-code b {
  color: #f5c451;
  letter-spacing: 0.18em;
}
.facts {
  display: grid;
  gap: 0.6rem;
  margin: 1.2rem 0 0;
}
.facts div {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.8rem;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
  padding-bottom: 0.45rem;
}
.facts dt {
  flex: none;
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.4);
}
.facts dd {
  margin: 0;
  font-size: 0.84rem;
  text-align: right;
  color: rgba(255, 255, 255, 0.8);
}
.sub-title {
  margin: 1.3rem 0 0.6rem;
  font-size: 0.68rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(196, 181, 253, 0.7);
}
.text-line {
  margin: 0 0 0.45rem;
  font-size: 0.92rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.75);
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.dchip {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  padding: 0.22rem 0.6rem;
  font-size: 0.68rem;
  color: rgba(255, 255, 255, 0.6);
}

.state-card {
  display: grid;
  place-items: center;
  gap: 0.8rem;
  padding: 3rem 1.4rem;
  text-align: center;
}
.state-card p {
  font-size: 0.86rem;
  color: rgba(255, 255, 255, 0.5);
}
.spinner {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.15);
  border-top-color: #f5c451;
  animation: spin 0.9s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

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
  animation: fadeIn 0.2s ease both;
}
@keyframes fadeIn {
  from {
    opacity: 0;
  }
}
.modal {
  width: min(26rem, 100%);
  border-radius: 1.4rem;
  border: 1px solid rgba(239, 68, 68, 0.28);
  background: #12101f;
  padding: 1.4rem;
  box-shadow: 0 50px 100px -40px rgba(0, 0, 0, 0.95);
  animation: popIn 0.28s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes popIn {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.96);
  }
}
.confirm-title {
  font-size: 1rem;
  font-weight: 600;
}
.confirm-sub {
  margin: 0.3rem 0 1rem;
  font-size: 0.8rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.5);
}
.confirm-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}
.confirm-actions .btn {
  flex: 1 1 8rem;
  border-radius: 0.9rem;
  padding: 0.72rem 1rem;
  font-size: 0.86rem;
}
</style>
