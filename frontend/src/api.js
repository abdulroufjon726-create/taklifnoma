/* API yordamchisi — Django backend bilan muloqot */

/*
 * Production (Vercel): bo'sh bo'lsa — vercel.json dagi /api rewrite orqali
 * Render backend'ga proksi bo'ladi. To'g'ridan-to'g'ri ulanish uchun
 * VITE_API_BASE_URL (masalan https://taklifnoma-api.onrender.com) o'rnatiladi.
 */
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')

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

export async function createInvitation(payload) {
  const res = await fetch(`${API_BASE}/api/invitations/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return parse(res)
}

export async function fetchInvitation(code) {
  const clean = String(code || '').replace(/[^a-z0-9]/gi, '').toUpperCase()
  const res = await fetch(`${API_BASE}/api/invitations/${encodeURIComponent(clean)}/`)
  return parse(res)
}

export function shareUrl(code) {
  const clean = String(code || '').replace(/[^a-z0-9]/gi, '').toUpperCase()
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
