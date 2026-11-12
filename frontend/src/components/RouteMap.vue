<template>
  <div class="rmap">
    <div class="rmap-bar">
      <button type="button" class="btn btn-ghost rmap-btn" :disabled="busy" @click="routeFromMe">
        <AppIcon name="ph:navigation-arrow" />
        {{ busy ? t('map.locating') : t('map.route') }}
      </button>
      <a class="btn btn-ghost rmap-btn" :href="googleUrl" target="_blank" rel="noopener">
        <AppIcon name="ph:map-pin" />
        {{ t('map.openGoogle') }}
      </a>
    </div>
    <div ref="el" class="rmap-canvas"></div>
    <p class="rmap-hint">{{ summary || t('map.routeHint') }}</p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import AppIcon from './AppIcon.vue'
import { useI18n } from '../i18n/index.js'

const props = defineProps({
  lat: { type: Number, required: true },
  lng: { type: Number, required: true },
  label: { type: String, default: '' },
})

const { t } = useI18n()
const el = ref(null)
const busy = ref(false)
const summary = ref('')

const venue = () => [props.lat, props.lng]
const googleUrl = computed(
  () =>
    `https://www.google.com/maps/dir/?api=1&destination=${props.lat},${props.lng}` +
    (props.label ? `&destination_place_id=&travelmode=driving` : ''),
)

let map = null
let routeLine = null
let meMarker = null

function drawVenue() {
  const [lat, lng] = venue()
  L.circleMarker([lat, lng], {
    radius: 9,
    color: '#f5c451',
    weight: 3,
    fillColor: '#f5c451',
    fillOpacity: 0.4,
  })
    .addTo(map)
    .bindPopup(props.label || t('map.venue'))
}

async function routeFromMe() {
  if (!navigator.geolocation) {
    summary.value = t('map.noGeo')
    return
  }
  busy.value = true
  summary.value = t('map.locating')
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const from = [pos.coords.latitude, pos.coords.longitude]
      if (meMarker) map.removeLayer(meMarker)
      meMarker = L.circleMarker(from, {
        radius: 8,
        color: '#8b5cf6',
        weight: 3,
        fillColor: '#8b5cf6',
        fillOpacity: 0.45,
      })
        .addTo(map)
        .bindPopup(t('map.you'))

      try {
        const url =
          `https://router.project-osrm.org/route/v1/driving/` +
          `${from[1]},${from[0]};${props.lng},${props.lat}` +
          `?overview=full&geometries=geojson`
        const res = await fetch(url)
        const data = res.ok ? await res.json() : null
        const route = data && data.routes && data.routes[0]
        if (!route) {
          summary.value = t('map.noRoute')
          return
        }
        if (routeLine) map.removeLayer(routeLine)
        routeLine = L.geoJSON(route.geometry, {
          style: { color: '#f5c451', weight: 4, opacity: 0.85 },
        }).addTo(map)
        map.fitBounds(routeLine.getBounds(), { padding: [24, 24] })
        const km = (route.distance / 1000).toFixed(route.distance > 10000 ? 0 : 1)
        const min = Math.max(1, Math.round(route.duration / 60))
        summary.value = t('map.routeSummary', { km, min })
      } catch {
        summary.value = t('map.noRoute')
      } finally {
        busy.value = false
      }
    },
    () => {
      summary.value = t('map.geoDenied')
      busy.value = false
    },
    { enableHighAccuracy: true, timeout: 12000 },
  )
}

onMounted(() => {
  map = L.map(el.value, { zoomControl: true }).setView(venue(), 14)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap',
  }).addTo(map)
  drawVenue()
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})
</script>

<style scoped>
.rmap {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.9rem;
  padding: 0.6rem;
  background: rgba(255, 255, 255, 0.03);
}
.rmap-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.rmap-btn {
  height: 2.25rem;
  padding: 0 0.7rem;
  font-size: 0.78rem;
  text-decoration: none;
}
.rmap-canvas {
  height: 240px;
  margin-top: 0.5rem;
  border-radius: 0.7rem;
  overflow: hidden;
  background: #12111c;
}
.rmap-hint {
  margin: 0.4rem 0 0;
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.5);
}
</style>
