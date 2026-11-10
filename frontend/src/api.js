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

const API_BASE = detectBase()
const TIMEOUT_MS = 30000

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
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
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

/** Kod bo'yicha keshdagi taklifnoma (bo'lsa — tarmoqsiz ochiladi). */
export function getCachedInvitation(code) {
  return cacheGet(normalizeCode(code))
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
  return data
}

/** Backendni "uyg'otish" uchun yengil fon so'rovi (xato bo'lsa jim o'tadi). */
export function warmUp() {
  try {
    request('/api/health/', { method: 'GET' }).catch(() => {})
  } catch {
    /* ignore */
  }
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
