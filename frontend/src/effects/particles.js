/* ==========================================================================
   Canvas particle engine — taklifnoma uchun ko'p sonli effektlar.
   Bitta canvas, bitta RAF loop: tanlangan har bir effekt uchun
   "tizim" (system) ishlaydi. Effektlarni bir nechtasini birga yoqish mumkin.
   ========================================================================== */

const TAU = Math.PI * 2

const rnd = (a, b) => a + Math.random() * (b - a)
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)]

const CONFETTI_COLORS = [
  '#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#a78bfa',
  '#5eead4', '#f5c451', '#ffffff',
]
const HEART_COLORS = ['#ff6b8a', '#ff9db4', '#ffb3c6', '#ffd3de', '#f5c451', '#ffffff']
const PETAL_COLORS = ['#ffd3de', '#ff9db4', '#fff0f4', '#ffe9a8', '#ffffff', '#f0abfc']
const BALLOON_COLORS = ['#ff6b8a', '#48dbfb', '#a78bfa', '#f5c451', '#5eead4', '#f0abfc']
const SPARKLE_COLORS = ['#ffffff', '#ffe9a8', '#d8b4fe', '#a5f3fc', '#fbcfe8']

/* ---------------------------------------------------------------- helpers */

function heartPath(ctx, x, y, s) {
  ctx.beginPath()
  ctx.moveTo(x, y + s * 0.35)
  ctx.bezierCurveTo(x, y - s * 0.1, x - s * 0.5, y - s * 0.45, x - s, y + s * 0.05)
  ctx.bezierCurveTo(x - s * 1.55, y + s * 0.55, x - s * 0.25, y + s * 1.15, x, y + s * 1.5)
  ctx.bezierCurveTo(x + s * 0.25, y + s * 1.15, x + s * 1.55, y + s * 0.55, x + s, y + s * 0.05)
  ctx.bezierCurveTo(x + s * 0.5, y - s * 0.45, x, y - s * 0.1, x, y + s * 0.35)
  ctx.closePath()
}

function starPath(ctx, x, y, r) {
  const k = r * 0.3
  ctx.beginPath()
  ctx.moveTo(x, y - r)
  ctx.quadraticCurveTo(x + k, y - k, x + r, y)
  ctx.quadraticCurveTo(x + k, y + k, x, y + r)
  ctx.quadraticCurveTo(x - k, y + k, x - r, y)
  ctx.quadraticCurveTo(x - k, y - k, x, y - r)
  ctx.closePath()
}

/* ------------------------------------------------------------- effektlar */

export const PARTICLE_DEFS = {
  /* 🎊 Konfetalar */
  confetti: {
    rate: 13,
    max: 120,
    make(w, h) {
      return {
        x: rnd(-20, w + 20),
        y: rnd(-50, -8),
        vx: rnd(-12, 12),
        vy: rnd(30, 70),
        w: rnd(4, 8),
        h: rnd(6, 11),
        rot: rnd(0, TAU),
        vr: rnd(-3.2, 3.2),
        phase: rnd(0, TAU),
        t: 0,
        color: pick([...CONFETTI_COLORS]),
      }
    },
    update(p, dt, w, h) {
      p.t += dt
      p.x += (p.vx + Math.sin(p.t * 2.1 + p.phase) * 20) * dt
      p.y += p.vy * dt
      p.rot += p.vr * dt
      return p.y < h + 40 && p.x > -80 && p.x < w + 80
    },
    draw(ctx, p) {
      ctx.save()
      ctx.translate(p.x, p.y)
      ctx.rotate(p.rot)
      ctx.scale(1, Math.max(0.22, Math.abs(Math.cos(p.t * 6 + p.phase))))
      ctx.globalAlpha = 0.95
      ctx.fillStyle = p.color
      ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h)
      ctx.restore()
    },
  },

  /* 💖 Yurakchalar (pastdan tepaga uchadi) */
  hearts: {
    rate: 3.4,
    max: 32,
    make(w, h) {
      return {
        x: rnd(0, w),
        y: h + rnd(10, 70),
        vy: -rnd(14, 32),
        s: rnd(5, 14),
        sway: rnd(0, TAU),
        swaySp: rnd(0.8, 1.8),
        rot: rnd(-0.25, 0.25),
        color: pick(HEART_COLORS),
        alpha: rnd(0.6, 0.95),
      }
    },
    update(p, dt, w) {
      p.y += p.vy * dt
      p.sway += p.swaySp * dt
      p.x += Math.sin(p.sway) * 20 * dt
      return p.y > -70 && p.x > -60 && p.x < w + 60
    },
    draw(ctx, p) {
      ctx.save()
      ctx.globalAlpha = p.alpha
      ctx.translate(0, 0)
      ctx.rotate(p.rot + Math.sin(p.sway) * 0.12)
      ctx.fillStyle = p.color
      heartPath(ctx, p.x, p.y - p.s * 0.5, p.s)
      ctx.fill()
      ctx.restore()
    },
  },

  /* 🌨️ Qor g'unchalari */
  snow: {
    rate: 10,
    max: 88,
    make(w, h) {
      return {
        x: rnd(0, w),
        y: rnd(-30, -6),
        vy: rnd(6, 22),
        r: rnd(1.2, 3.8),
        sway: rnd(0, TAU),
        swaySp: rnd(0.5, 1.4),
        alpha: rnd(0.25, 0.9),
      }
    },
    update(p, dt, w) {
      p.y += p.vy * dt
      p.sway += p.swaySp * dt
      p.x += Math.sin(p.sway) * 15 * dt
      return p.y < h + 12 && p.x > -20 && p.x < w + 20
    },
    draw(ctx, p) {
      ctx.save()
      ctx.globalAlpha = p.alpha
      ctx.fillStyle = '#ffffff'
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, TAU)
      ctx.fill()
      ctx.restore()
    },
  },

  /* ⭐ Yulduzlar (joyni egallab, porlaydi) */
  stars: {
    rate: 3.2,
    max: 54,
    make(w, h, pal) {
      return {
        x: rnd(0, w),
        y: rnd(0, h),
        r: rnd(1.5, 3.6),
        t: rnd(0, 6.3),
        sp: rnd(1.2, 3.2),
        color: pick(['#ffffff', ...pal]),
      }
    },
    update(p, dt) {
      p.t += dt
      return true
    },
    draw(ctx, p) {
      const a = 0.28 + 0.72 * Math.abs(Math.sin(p.t * p.sp))
      ctx.save()
      ctx.globalAlpha = a * 0.3
      ctx.fillStyle = p.color
      starPath(ctx, p.x, p.y, p.r * 2.1)
      ctx.fill()
      ctx.globalAlpha = a
      starPath(ctx, p.x, p.y, p.r)
      ctx.fill()
      ctx.restore()
    },
  },

  /* 🫧 Pufakchalar */
  bubbles: {
    rate: 4,
    max: 34,
    make(w, h, pal) {
      return {
        x: rnd(0, w),
        y: h + rnd(5, 60),
        vy: -rnd(10, 28),
        r: rnd(5, 17),
        sway: rnd(0, TAU),
        swaySp: rnd(0.6, 1.5),
        alpha: rnd(0.22, 0.5),
        color: pick(['#ffffff', ...pal]),
      }
    },
    update(p, dt, w) {
      p.y += p.vy * dt
      p.sway += p.swaySp * dt
      p.x += Math.sin(p.sway) * 20 * dt
      return p.y > -50 && p.x > -40 && p.x < w + 40
    },
    draw(ctx, p) {
      ctx.save()
      ctx.globalAlpha = p.alpha
      ctx.strokeStyle = p.color
      ctx.lineWidth = 1.4
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, TAU)
      ctx.stroke()
      ctx.globalAlpha = p.alpha * 1.6
      ctx.fillStyle = '#ffffff'
      ctx.beginPath()
      ctx.arc(p.x - p.r * 0.35, p.y - p.r * 0.35, Math.max(1, p.r * 0.16), 0, TAU)
      ctx.fill()
      ctx.restore()
    },
  },

  /* 🌸 Atirgul barglari */
  petals: {
    rate: 5.2,
    max: 46,
    make(w, h, pal) {
      return {
        x: rnd(-10, w + 10),
        y: rnd(-40, -8),
        vy: rnd(10, 28),
        rot: rnd(0, TAU),
        vr: rnd(-1.3, 1.3),
        s: rnd(6, 13),
        t: 0,
        phase: rnd(0, TAU),
        color: pick([...PETAL_COLORS, ...pal]),
      }
    },
    update(p, dt, w, h) {
      p.t += dt
      p.y += p.vy * dt
      p.x += Math.sin(p.t * 1.7 + p.phase) * 30 * dt
      p.rot += p.vr * dt
      return p.y < h + 30 && p.x > -50 && p.x < w + 50
    },
    draw(ctx, p) {
      ctx.save()
      ctx.translate(p.x, p.y)
      ctx.rotate(p.rot)
      ctx.scale(1, 0.55 + 0.45 * Math.sin(p.t * 3 + p.phase))
      ctx.globalAlpha = 0.88
      ctx.fillStyle = p.color
      ctx.beginPath()
      ctx.ellipse(0, 0, p.s * 0.55, p.s, 0, 0, TAU)
      ctx.fill()
      ctx.globalAlpha = 0.35
      ctx.strokeStyle = 'rgba(0,0,0,0.35)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(0, -p.s * 0.9)
      ctx.lineTo(0, p.s * 0.9)
      ctx.stroke()
      ctx.restore()
    },
  },

  /* 🎆 Havoyi olovlar (davriy portlashlar) */
  fireworks: {
    rate: 0.38,
    max: 240,
    spawn(sys, w, h, pal) {
      const cx = rnd(w * 0.1, w * 0.9)
      const cy = rnd(h * 0.07, h * 0.55)
      const color = pick([...pal, '#ffffff', '#ffd3de'])
      const n = Math.round(rnd(16, 28))
      for (let i = 0; i < n; i++) {
        const a = rnd(0, TAU)
        const spd = rnd(40, 155)
        sys.parts.push({
          x: cx,
          y: cy,
          px: cx,
          py: cy,
          vx: Math.cos(a) * spd,
          vy: Math.sin(a) * spd,
          life: 0,
          ttl: rnd(1.1, 2),
          r: rnd(1.2, 2.6),
          color,
        })
      }
    },
    update(p, dt) {
      p.life += dt
      p.px = p.x
      p.py = p.y
      p.vx *= 1 - 1.7 * dt
      p.vy = p.vy * (1 - 1.3 * dt) + 60 * dt
      p.x += p.vx * dt
      p.y += p.vy * dt
      return p.life < p.ttl
    },
    draw(ctx, p) {
      const k = Math.max(0, 1 - p.life / p.ttl)
      ctx.save()
      ctx.globalAlpha = k * 0.9
      ctx.strokeStyle = p.color
      ctx.lineWidth = p.r
      ctx.lineCap = 'round'
      ctx.beginPath()
      ctx.moveTo(p.px, p.py)
      ctx.lineTo(p.x, p.y)
      ctx.stroke()
      ctx.globalAlpha = k
      ctx.fillStyle = '#ffffff'
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r * 0.7, 0, TAU)
      ctx.fill()
      ctx.restore()
    },
  },

  /* 🎈 Uchuvchi sharlar */
  balloons: {
    rate: 0.85,
    max: 10,
    make(w, h, pal) {
      return {
        x: rnd(0, w),
        y: h + rnd(40, 150),
        vy: -rnd(12, 28),
        r: rnd(13, 26),
        sway: rnd(0, TAU),
        swaySp: rnd(0.55, 1.2),
        t: 0,
        color: pick([...BALLOON_COLORS, ...pal]),
        str: rnd(26, 58),
      }
    },
    update(p, dt, w) {
      p.t += dt
      p.y += p.vy * dt
      p.sway += p.swaySp * dt
      p.x += Math.sin(p.sway) * 30 * dt
      return p.y > -110 && p.x > -60 && p.x < w + 60
    },
    draw(ctx, p) {
      const sway = Math.sin(p.sway) * 0.16
      ctx.save()
      // arqon
      ctx.globalAlpha = 0.5
      ctx.strokeStyle = 'rgba(255,255,255,0.75)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(p.x, p.y + p.r * 1.18)
      ctx.quadraticCurveTo(
        p.x + Math.sin(p.sway * 1.7) * 10,
        p.y + p.r + p.str * 0.5,
        p.x + Math.sin(p.sway * 1.2) * 16,
        p.y + p.r + p.str,
      )
      ctx.stroke()
      // tanasi
      ctx.globalAlpha = 0.92
      ctx.fillStyle = p.color
      ctx.beginPath()
      ctx.ellipse(p.x, p.y, p.r * 0.85, p.r, sway, 0, TAU)
      ctx.fill()
      // yog'loq
      ctx.beginPath()
      ctx.moveTo(p.x - 3, p.y + p.r * 0.98)
      ctx.lineTo(p.x + 3, p.y + p.r * 0.98)
      ctx.lineTo(p.x, p.y + p.r * 1.2)
      ctx.closePath()
      ctx.fill()
      // yorug'lik
      ctx.globalAlpha = 0.4
      ctx.fillStyle = '#ffffff'
      ctx.beginPath()
      ctx.ellipse(p.x - p.r * 0.3, p.y - p.r * 0.35, p.r * 0.18, p.r * 0.3, -0.5, 0, TAU)
      ctx.fill()
      ctx.restore()
    },
  },

  /* 💫 Tikranuvchi tufraq */
  glitter: {
    rate: 11,
    max: 76,
    make(w, h, pal) {
      return {
        x: rnd(0, w),
        y: rnd(0, h),
        r: rnd(0.9, 2.6),
        life: 0,
        ttl: rnd(0.5, 1.4),
        rot: rnd(0, TAU),
        color: pick([...SPARKLE_COLORS, ...pal]),
      }
    },
    update(p, dt) {
      p.life += dt
      p.rot += dt * 1.5
      return p.life < p.ttl
    },
    draw(ctx, p) {
      const k = Math.sin(Math.PI * (p.life / p.ttl))
      ctx.save()
      ctx.translate(p.x, p.y)
      ctx.rotate(p.rot)
      ctx.globalAlpha = Math.max(0, k)
      ctx.strokeStyle = p.color
      ctx.lineWidth = 1.2
      ctx.beginPath()
      ctx.moveTo(-p.r * 2.4, 0)
      ctx.lineTo(p.r * 2.4, 0)
      ctx.moveTo(0, -p.r * 2.4)
      ctx.lineTo(0, p.r * 2.4)
      ctx.stroke()
      ctx.fillStyle = p.color
      ctx.beginPath()
      ctx.arc(0, 0, p.r * 0.75, 0, TAU)
      ctx.fill()
      ctx.restore()
    },
  },

  /* 🌧️ Romantik yomg'ir */
  rain: {
    rate: 30,
    max: 170,
    make(w, h, pal) {
      return {
        x: rnd(-30, w + 30),
        y: rnd(-60, -10),
        vy: rnd(200, 300),
        len: rnd(9, 20),
        alpha: rnd(0.12, 0.42),
        color: pick(['#cfe9ff', '#9fd7ff', '#ffffff', ...pal]),
      }
    },
    update(p, dt, w, h) {
      p.y += p.vy * dt
      p.x -= 55 * dt
      return p.y < h + 30 && p.x > -60
    },
    draw(ctx, p) {
      ctx.save()
      ctx.globalAlpha = p.alpha
      ctx.strokeStyle = p.color
      ctx.lineWidth = 1.3
      ctx.lineCap = 'round'
      ctx.beginPath()
      ctx.moveTo(p.x, p.y)
      ctx.lineTo(p.x + 1.6, p.y + p.len)
      ctx.stroke()
      ctx.restore()
    },
  },
}

/* ---------------------------------------------------------------- engine */

export function createParticleEngine(canvas) {
  const ctx = canvas.getContext('2d', { alpha: true })
  let w = 0
  let h = 0
  let raf = 0
  let last = 0
  let started = false
  let effects = []
  let palette = ['#ffffff']
  const systems = new Map()

  const reduceMotion =
    typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches

  function resize() {
    if (!canvas.isConnected) return
    const rect = canvas.getBoundingClientRect()
    if (rect.width < 2 || rect.height < 2) return
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    w = rect.width
    h = rect.height
    canvas.width = Math.round(w * dpr)
    canvas.height = Math.round(h * dpr)
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }

  function syncSystems() {
    const wanted = new Set(effects.filter((id) => PARTICLE_DEFS[id]))
    for (const key of [...systems.keys()]) {
      if (!wanted.has(key)) systems.delete(key)
    }
    for (const key of wanted) {
      if (!systems.has(key)) {
        systems.set(key, { def: PARTICLE_DEFS[key], parts: [], acc: 0, palette })
      }
    }
  }

  function clearAll() {
    for (const sys of systems.values()) sys.parts.length = 0
  }

  function frame(ts) {
    raf = requestAnimationFrame(frame)
    const dt = Math.min(0.05, (ts - last) / 1000 || 0.016)
    last = ts
    if (!w || !h) {
      resize()
      if (!w || !h) return
    }
    ctx.clearRect(0, 0, w, h)
    // ekran kichik bo'lsa — kamroq, katta bo'lsa — biroz ko'proq (yengil)
    const scale = Math.min(1.2, Math.max(0.4, (w * h) / (1280 * 720)))

    for (const sys of systems.values()) {
      const def = sys.def
      sys.acc += dt * def.rate * scale
      let guard = 0
      while (sys.acc >= 1 && guard++ < 30) {
        sys.acc -= 1
        if (sys.parts.length >= (def.max || 150)) break
        if (def.spawn) def.spawn(sys, w, h, sys.palette)
        else sys.parts.push(def.make(w, h, sys.palette))
      }
      if (sys.parts.length) {
        const alive = []
        for (const p of sys.parts) {
          if (def.update(p, dt, w, h)) {
            def.draw(ctx, p, sys.palette)
            alive.push(p)
          }
        }
        sys.parts = alive
      }
    }
  }

  return {
    setEffects(ids) {
      effects = Array.isArray(ids) ? [...ids] : []
      syncSystems()
    },
    setPalette(colors) {
      palette = Array.isArray(colors) && colors.length ? [...colors] : ['#ffffff']
      for (const sys of systems.values()) sys.palette = palette
      clearAll()
    },
    resize,
    start() {
      if (started || reduceMotion) return
      started = true
      resize()
      last = performance.now()
      raf = requestAnimationFrame(frame)
    },
    stop() {
      started = false
      cancelAnimationFrame(raf)
      raf = 0
      ctx && ctx.clearRect(0, 0, w, h)
    },
  }
}
