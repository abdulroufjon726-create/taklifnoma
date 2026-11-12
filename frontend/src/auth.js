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

// api.js 401 ko'rsa shu hodisani yuboradi — UI darhol "chiqqan" holatga o'tadi.
if (typeof window !== 'undefined') {
  window.addEventListener('taklifnoma:auth-expired', signOutLocal)
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

/* ---- Email + parol bilan kirish ---------------------------------------- */
export const authConfig = reactive({ google: false, loaded: false })

export async function loadAuthConfig(force = false) {
  if (authConfig.loaded && !force) return authConfig
  try {
    const res = await fetch(`${API_BASE}/api/auth/config/`, { cache: 'no-store' })
    const data = await readJson(res)
    authConfig.google = Boolean(data && data.google)
  } catch {
    authConfig.google = false
  }
  authConfig.loaded = true
  return authConfig
}

async function authPost(path, payload) {
  let res
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      cache: 'no-store',
    })
  } catch {
    const err = new Error('network')
    err.code = 'network'
    throw err
  }
  const data = await readJson(res)
  if (!res.ok) {
    const err = new Error((data && data.detail) || 'auth failed')
    err.code = (data && data.code) || 'default'
    err.status = res.status
    throw err
  }
  saveToken(data.token)
  auth.user = data.user
  return data.user
}

export function passwordLogin(email, password) {
  return authPost('/api/auth/login/', { email, password })
}

export function registerAccount(name, email, password) {
  return authPost('/api/auth/register/', { name, email, password })
}

/** Google bilan kirgan hisobga parol o'rnatish (keyin email bilan ham kirish mumkin). */
export async function setPassword(password) {
  const res = await fetch(`${API_BASE}/api/auth/password/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${auth.token}`,
    },
    body: JSON.stringify({ password }),
    cache: 'no-store',
  })
  const data = await readJson(res)
  if (!res.ok) {
    const err = new Error((data && data.detail) || 'password failed')
    err.code = (data && data.code) || 'default'
    err.status = res.status
    throw err
  }
  auth.user = data
  return data
}
