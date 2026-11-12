<template>
  <div class="pmap">
    <div class="pmap-bar">
      <input
        v-model="query"
        class="field pmap-q"
        type="text"
        maxlength="120"
        :placeholder="t('map.searchPh')"
        @keydown.enter.prevent="search"
      />
      <button type="button" class="btn btn-ghost pmap-btn" :disabled="busy" @click="search">
        {{ t('map.find') }}
      </button>
      <button type="button" class="btn btn-ghost pmap-btn" :disabled="busy" @click="locate">
        {{ t('map.myLocation') }}
      </button>
    </div>
    <div ref="el" class="pmap-canvas"></div>
    <p class="pmap-hint">{{ hint || t('map.hint') }}</p>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import { useI18n } from '../i18n/index.js'

const props = defineProps({
  lat: { type: Number, default: null },
  lng: { type: Number, default: null },
  place: { type: String, default: '' },
})
const emit = defineEmits(['update:lat', 'update:lng', 'update:place'])

const { t } = useI18n()
const el = ref(null)
const query = ref(props.place || '')
const hint = ref('')
const busy = ref(false)

const FALLBACK = [41.3111, 69.2797] // Toshkent
let map = null
let marker = null

function point() {
  return typeof props.lat === 'number' && typeof props.lng === 'number'
    ? [props.lat, props.lng]
    : null
}

function drawMarker(latlng, { emitChange = false } = {}) {
  if (!map) return
  if (!marker) {
    marker = L.circleMarker(latlng, {
      radius: 9,
      color: '#f5c451',
      weight: 3,
      fillColor: '#f5c451',
      fillOpacity: 0.35,
    }).addTo(map)
  } else {
    marker.setLatLng(latlng)
  }
  if (emitChange) {
    emit('update:lat', Number(latlng[0].toFixed(6)))
    emit('update:lng', Number(latlng[1].toFixed(6)))
  }
}

async function reverse(latlng) {
  try {
    const url =
      'https://nominatim.openstreetmap.org/reverse?format=jsonv2&accept-language=uz,ru,en' +
      `&lat=${latlng[0]}&lon=${latlng[1]}`
    const res = await fetch(url)
    if (!res.ok) return
    const data = await res.json()
    const name = data.display_name || ''
    if (name) {
      query.value = name.slice(0, 200)
      emit('update:place', query.value)
    }
  } catch {
    /* tarmoq bo'lmasa matn o'zgarmaydi */
  }
}

async function search() {
  const q = (query.value || '').trim()
  if (!q) return
  busy.value = true
  hint.value = ''
  try {
    const url =
      'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&accept-language=uz,ru,en' +
      `&q=${encodeURIComponent(q)}`
    const res = await fetch(url)
    const list = res.ok ? await res.json() : []
    if (!list.length) {
      hint.value = t('map.notFound')
      return
    }
    const hit = list[0]
    const latlng = [Number(hit.lat), Number(hit.lon)]
    map.flyTo(latlng, 15)
    drawMarker(latlng, { emitChange: true })
    query.value = (hit.display_name || q).slice(0, 200)
    emit('update:place', query.value)
  } catch {
    hint.value = t('map.noNetwork')
  } finally {
    busy.value = false
  }
}

function locate() {
  if (!navigator.geolocation) {
    hint.value = t('map.noGeo')
    return
  }
  busy.value = true
  hint.value = t('map.locating')
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const latlng = [pos.coords.latitude, pos.coords.longitude]
      map.flyTo(latlng, 16)
      drawMarker(latlng, { emitChange: true })
      reverse(latlng)
      hint.value = ''
      busy.value = false
    },
    () => {
      hint.value = t('map.geoDenied')
      busy.value = false
    },
    { enableHighAccuracy: true, timeout: 12000 },
  )
}

onMounted(() => {
  map = L.map(el.value, { zoomControl: true, attributionControl: true }).setView(
    point() || FALLBACK,
    point() ? 15 : 11,
  )
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap',
  }).addTo(map)
  if (point()) drawMarker(point())
  map.on('click', (e) => {
    drawMarker(e.latlng, { emitChange: true })
    reverse([e.latlng.lat, e.latlng.lng])
  })
})

watch(
  () => [props.lat, props.lng],
  () => {
    if (point()) drawMarker(point())
  },
)

onBeforeUnmount(() => {
  map?.remove()
  map = null
  marker = null
})
</script>

<style scoped>
.pmap {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.9rem;
  padding: 0.6rem;
  background: rgba(255, 255, 255, 0.03);
}
.pmap-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.pmap-q {
  flex: 1 1 12rem;
  min-width: 0;
  height: 2.25rem;
  font-size: 0.82rem;
}
.pmap-btn {
  height: 2.25rem;
  padding: 0 0.7rem;
  font-size: 0.78rem;
}
.pmap-canvas {
  height: 180px;
  margin-top: 0.5rem;
  border-radius: 0.7rem;
  overflow: hidden;
  background: #12111c;
}
.pmap-hint {
  margin: 0.4rem 0 0;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.45);
}
</style>
