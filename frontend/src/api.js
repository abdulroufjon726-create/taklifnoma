/* API yordamchisi — Django backend bilan muloqot */

/*
 * Backend manzili:
 *  - VITE_API_BASE_URL berilsa — o'shanisi ishlatiladi (Vercel build env).
 *  - Lokal (localhost) yoki backend o'zi SPA'ni bersa (onrender.com) —
 *    nisbiy "/api" (Vite proksi / bir xil origin).
 *  - Boshqa holatda (masalan Vercel) — to'g'ridan-to'g'ri Render backend.
 * Shu tufayli env o'rnatilmasa ham sayt ishlayveradi.
 */
export const REMOTE_API_BASE = 'https://taklifnoma-1.onrender.com'

function detectBase() {
  const env = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '')
  if (env) return env
  if (typeof window === 'undefined') return REMOTE_API_BASE

  const host = window.location.hostname
  const isLocal =
    host === 'localhost' ||
    host === '127.0.0.1' ||
    host === '[::1]' ||
    host.endsWith('.local')
  const isBackendHost = host.endsWith('.onrender.com')
  return isLocal || isBackendHost ? '' : REMOTE_API_BASE
}

export const API_BASE = detectBase()
const TIMEOUT_MS = 30000
const TOKEN_KEY = 'taklifnoma:token'

/* Kirish tokeni — Google login'dan keyin saqlanadi */
export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

export function setToken(value) {
  try {
    if (value) localStorage.setItem(TOKEN_KEY, value)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    /* ignore */
  }
}

function extractDetail(data) {
  if (!data) return null
  if (typeof data.detail === 'string') return data.detail
  // DRF field errors: { field: ["msg"] }
  for (const key of Object.keys(data)) {
    const v = data[key]
    if (Array.isArray(v) && typeof v[0] === 'string') return `${key}: ${v[0]}`
    if (typeof v === 'string') return v
  }
  return null
}

function networkError(cause) {
  const err = new Error("Serverga ulanib bo'lmadi. Internetni tekshirib, qayta urinib ko'ring.")
  err.status = 0
  err.code = 'network'
  err.cause = cause
  return err
}

async function request(path, options = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)
  const headers = { ...(options.headers || {}) }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
      // Render bepul tarif "uxlab qolgan" bo'lsa, brauzer keshini chetlab o'tamiz
      cache: options.cache || 'no-store',
    })
    return res
  } finally {
    clearTimeout(timer)
  }
}

async function parse(res) {
  let data = null
  try {
    data = await res.json()
  } catch {
    data = null
  }
  if (!res.ok) {
    const err = new Error(extractDetail(data) || 'Serverda xatolik yuz berdi')
    err.status = res.status
    err.data = data
    // Sessiya tugagan (token eskirgan/o'chirilgan) — eski tokenni darhol tashlaymiz,
    // aks holda /login sahifasi uni ko'rib qayta /envelopes'ga qaytarib yuboradi.
    if (res.status === 401 && getToken()) {
      setToken('')
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('taklifnoma:auth-expired'))
      }
    }
    throw err
  }
  return data
}


/* ---- Kesh: bitta taklifnoma ikki marta so'ralmasin -------------------- */
const CACHE_TTL = 5 * 60 * 1000
const CACHE_MAX = 24
const cache = new Map()

function normalizeCode(code) {
  return String(code || '').replace(/[^a-z0-9]/gi, '').toUpperCase()
}

function cacheGet(code) {
  const hit = cache.get(code)
  if (!hit) return null
  if (Date.now() - hit.at > CACHE_TTL) {
    cache.delete(code)
    return null
  }
  return hit.data
}

function cacheSet(data) {
  if (!data || !data.code) return
  cache.set(data.code, { data, at: Date.now() })
  if (cache.size > CACHE_MAX) {
    // eng eski yozuvni olib tashlaymiz
    const oldest = [...cache.entries()].sort((a, b) => a[1].at - b[1].at)[0]
    if (oldest) cache.delete(oldest[0])
  }
}

/* ---- Doimiy kesh: havola qayta ochilganda darhol ko'rinadi ------------- */
const LS_TTL = 24 * 60 * 60 * 1000
const LS_PREFIX = 'taklifnoma:inv:'

function lsGet(code) {
  try {
    const raw = localStorage.getItem(LS_PREFIX + code)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed || !parsed.data || Date.now() - parsed.at > LS_TTL) return null
    return parsed.data
  } catch {
    return null
  }
}

function lsSet(data) {
  if (!data || !data.code) return
  try {
    localStorage.setItem(LS_PREFIX + data.code, JSON.stringify({ data, at: Date.now() }))
  } catch {
    /* xotira to'lgan bo'lsa jim o'tamiz */
  }
}

/* ---- Muddati o'tgan keshni tozalash -----------------------------------
   Kesh yozuvlari localStorage'da qolib ketmasin: eskirgan taklifnoma yoki
   ro'yxat nusxasi keyingi ochilishda ko'rinib qolmasligi uchun har soatda
   bir marta TTL'i o'tgan yozuvlarni o'chiramiz. */
const PRUNE_KEY = 'taklifnoma:prune'
const PRUNE_EVERY = 60 * 60 * 1000
const PRUNE_RULES = [
  [LS_PREFIX, LS_TTL], // taklifnoma:inv:<KOD>
  ['taklifnoma:list:', 6 * 60 * 60 * 1000], // hisob ro'yxati keshi
]

export function pruneCaches() {
  try {
    if (Date.now() - Number(localStorage.getItem(PRUNE_KEY) || 0) < PRUNE_EVERY) return 0
    localStorage.setItem(PRUNE_KEY, String(Date.now()))

    let removed = 0
    for (let i = localStorage.length - 1; i >= 0; i -= 1) {
      const key = localStorage.key(i)
      const rule = key && PRUNE_RULES.find(([prefix]) => key.startsWith(prefix))
      if (!rule) continue
      let at = 0
      try {
        at = Number(JSON.parse(localStorage.getItem(key) || '{}').at) || 0
      } catch {
        at = 0
      }
      if (!at || Date.now() - at > rule[1]) {
        localStorage.removeItem(key)
        removed += 1
      }
    }
    return removed
  } catch {
    return 0
  }
}

/** Kod bo'yicha keshdagi taklifnoma (bo'lsa — tarmoqsiz ochiladi). */
export function getCachedInvitation(code) {
  const clean = normalizeCode(code)
  return cacheGet(clean) || lsGet(clean)
}

export async function createInvitation(payload) {
  let res
  try {
    res = await request('/api/invitations/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch (e) {
    if (e.name === 'AbortError') {
      const err = new Error('Server javob bermadi. Bir ozdan so‘ng qayta urinib ko‘ring.')
      err.status = 0
      err.code = 'timeout'
      throw err
    }
    throw networkError(e)
  }
  const data = await parse(res)
  cacheSet(data)
  return data
}

export async function fetchInvitation(code, { fresh = false } = {}) {
  const clean = normalizeCode(code)
  if (!clean) throw Object.assign(new Error('Kod kiritilmagan'), { status: 404 })
  if (!fresh) {
    const cached = cacheGet(clean)
    if (cached) return cached
  }

  let res
  // Render bepul tarifda birinchi so'rov uyg'onish bilan kechikishi mumkin —
  // GET xavfsiz, shuning uchun bitta qayta urinish qilamiz.
  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      res = await request(`/api/invitations/${encodeURIComponent(clean)}/`)
      break
    } catch (e) {
      if (e.name === 'AbortError') {
        if (attempt === 1) {
          const err = new Error('Server javob bermadi. Bir ozdan so‘ng qayta urinib ko‘ring.')
          err.status = 0
          err.code = 'timeout'
          throw err
        }
      } else if (attempt === 1) {
        throw networkError(e)
      }
      await new Promise((r) => setTimeout(r, 900))
    }
  }

  const data = await parse(res)
  cacheSet(data)
  lsSet(data)
  return data
}

/**
 * Mavjud taklifnomani tahrirlash (faqat yaratuvchida saqlangan kalit bilan).
 * Kalit serverga X-Edit-Key sarlavhasi orqali yuboriladi.
 */
export async function updateInvitation(code, editKey, payload) {
  const clean = normalizeCode(code)
  if (!clean) throw Object.assign(new Error('Kod kiritilmagan'), { status: 404 })
  let res
  try {
    res = await request(`/api/invitations/${encodeURIComponent(clean)}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', 'X-Edit-Key': editKey },
      body: JSON.stringify(payload),
    })
  } catch (e) {
    if (e.name === 'AbortError') {
      const err = new Error('Server javob bermadi. Bir ozdan so‘ng qayta urinib ko‘ring.')
      err.status = 0
      err.code = 'timeout'
      throw err
    }
    throw networkError(e)
  }
  const data = await parse(res)
  cacheSet(data)
  lsSet(data)
  return data
}

/** Backendni "uyg'otish" uchun yengil fon so'rovi (xato bo'lsa jim o'tadi).
    Render bepul tarifi uxlab qolishi mumkin — lekin har sahifada qayta
    urinmaymiz: 5 daqiqada bir marta yetarli. */
const WARM_KEY = 'taklifnoma:warm'
const WARM_TTL = 5 * 60 * 1000

export function warmUp() {
  try {
    const at = Number(localStorage.getItem(WARM_KEY) || 0)
    if (Date.now() - at < WARM_TTL) return
    localStorage.setItem(WARM_KEY, String(Date.now()))
  } catch {
    /* localStorage yo'q — baribir davom etamiz */
  }
  request('/api/health/', { method: 'GET' }).catch(() => {})
}

export function shareUrl(code) {
  const clean = normalizeCode(code)
  return `${window.location.origin}/i/${clean}`
}

export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    try {
      const ta = document.createElement('textarea')
      ta.value = text
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.select()
      const ok = document.execCommand('copy')
      document.body.removeChild(ta)
      return ok
    } catch {
      return false
    }
  }
}

/* ---- Hisob: egasining taklifnomalari ---------------------------------- */

/** Kirgan foydalanuvchining barcha taklifnomalari.
    Render uxlab qolgan bo'lsa birinchi so'rov uzilishi mumkin — GET
    xavfsiz, shuning uchun bitta qayta urinamiz (ikkinchisi tez keladi). */
export async function fetchMyInvitations() {
  for (let attempt = 0; ; attempt += 1) {
    try {
      const data = await parse(await request('/api/invitations/mine/'))
      return data.results || []
    } catch (e) {
      const soft = e.name === 'AbortError' || e.name === 'TypeError'
      if (!soft || attempt >= 1) {
        if (e.name === 'AbortError') {
          throw Object.assign(new Error("Server javob bermadi. Qayta urinib ko'ring."), {
            status: 0,
            code: 'timeout',
          })
        }
        throw e.name === 'TypeError' ? networkError(e) : e
      }
      await new Promise((r) => setTimeout(r, 800))
    }
  }
}

/** Taklifnomani o'chirish (faqat egasi). */
export async function deleteInvitation(code, editKey = '') {
  const clean = normalizeCode(code)
  if (!clean) throw Object.assign(new Error('Kod kiritilmagan'), { status: 404 })
  const headers = editKey ? { 'X-Edit-Key': editKey } : {}
  let res
  try {
    res = await request(`/api/invitations/${encodeURIComponent(clean)}/`, { method: 'DELETE', headers })
  } catch (e) {
    if (e.name === 'AbortError') {
      const err = new Error("Server javob bermadi. Qayta urinib ko'ring.")
      err.status = 0
      err.code = 'timeout'
      throw err
    }
    throw networkError(e)
  }
  if (res.status === 204) {
    cache.delete(clean)
    try {
      localStorage.removeItem(`taklifnoma:inv:${clean}`)
    } catch {
      /* ignore */
    }
    return true
  }
  await parse(res)
  return false
}

/** Login'dan oldin yaratilgan (egasiz) taklifnomani hisobga bog'lash. */
export async function claimInvitation(code, editKey) {
  const clean = normalizeCode(code)
  if (!clean) throw Object.assign(new Error('Kod kiritilmagan'), { status: 404 })
  let res
  try {
    res = await request(`/api/invitations/${encodeURIComponent(clean)}/claim/`, {
      method: 'POST',
      headers: { 'X-Edit-Key': editKey || '' },
    })
  } catch (e) {
    throw networkError(e)
  }
  return parse(res)
}
