/* ==========================================================================
   Foydalanuvchining o'z taklifnomalari — shu qurilmada saqlanadi.
   Har bir yozuvda tahrirlash kaliti bo'ladi, shuning uchun egasi
   taklifnomani qayta ochib o'zgartira oladi.
   ========================================================================== */

const KEY = 'taklifnoma:mine'
const MAX = 30

export function listMine() {
  try {
    const raw = localStorage.getItem(KEY)
    const arr = raw ? JSON.parse(raw) : []
    return Array.isArray(arr) ? arr.filter((e) => e && e.code) : []
  } catch {
    return []
  }
}

function persist(list) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list.slice(0, MAX)))
  } catch {
    /* xotira to'lgan — jim o'tamiz */
  }
}

export function saveMine(entry) {
  if (!entry || !entry.code) return
  const list = listMine().filter((e) => e.code !== entry.code)
  list.unshift(entry)
  persist(list)
}

export function getMine(code) {
  const clean = String(code || '').replace(/[^a-z0-9]/gi, '').toUpperCase()
  return listMine().find((e) => e.code === clean) || null
}

export function removeMine(code) {
  persist(listMine().filter((e) => e.code !== code))
}
