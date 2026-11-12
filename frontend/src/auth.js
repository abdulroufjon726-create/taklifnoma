/* ==========================================================================
   Kirish holati (Google OAuth + token)
   Token localStorage'da saqlanadi, api.js har so'rovga qo'shadi.
   ========================================================================== */
import { computed, reactive } from 'vue'

import { API_BASE, getToken, setToken } from './api.js'

export const auth = reactive({
  token: getToken(),
  user: null,
  loading: false,
  error: '',
})

export const isLoggedIn = computed(() => Boolean(auth.token))

/** Google rozilik sahifasiga havola (backend orqali). */
export function signInUrl(next = '/create') {
  const target = next && next.startsWith('/') ? next : '/create'
  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  return `${API_BASE}/api/auth/google/start/?next=${encodeURIComponent(target)}&origin=${encodeURIComponent(origin)}`
}

export function signIn(next) {
  window.location.href = signInUrl(next)
}

export function saveToken(token) {
  setToken(token)
  auth.token = token || ''
}

export function signOutLocal() {
  setToken('')
  auth.token = ''
  auth.user = null
}

async function readJson(res) {
  try {
    return await res.json()
  } catch {
    return null
  }
}

/** Joriy foydalanuvchini yuklash (token bo'lmasa jim qaytadi). */
export async function loadMe() {
  if (!auth.token) {
    auth.user = null
    return null
  }
  auth.loading = true
  try {
    const res = await fetch(`${API_BASE}/api/auth/me/`, {
      headers: { Authorization: `Bearer ${auth.token}` },
      cache: 'no-store',
    })
    if (res.status === 401) {
      signOutLocal()
      return null
    }
    const data = await readJson(res)
    auth.user = res.ok ? data : null
    auth.error = res.ok ? '' : 'me'
    return auth.user
  } catch {
    auth.error = 'network'
    return null
  } finally {
    auth.loading = false
  }
}

export async function signOut() {
  const token = auth.token
  signOutLocal()
  if (!token) return
  try {
    await fetch(`${API_BASE}/api/auth/logout/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch {
    /* tarmoq bo'lmasa ham chiqamiz */
  }
}
