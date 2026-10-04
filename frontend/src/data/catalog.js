/* ==========================================================================
   Katalog: temalar, effektlar, animatsiyalar, default matnlar
   ========================================================================== */

export const EVENT_TYPES = [
  { id: 'toy', label: "To'y", icon: 'mdi:ring' },
  { id: 'niqob', label: 'Niqob to‘yi', icon: 'ph:feather' },
  { id: 'tugilgan_kun', label: "Tug'ilgan kun", icon: 'ph:cake' },
  { id: 'suvruq', label: 'Suvruq', icon: 'ph:champagne' },
  { id: 'bayram', label: 'Bayram', icon: 'ph:confetti' },
  { id: 'korxona', label: 'Korxona ochilishi', icon: 'ph:buildings' },
  { id: 'boshqa', label: 'Boshqa', icon: 'ph:sparkle' },
]

export const EVENT_LABELS = Object.fromEntries(EVENT_TYPES.map((e) => [e.id, e.label]))

/* ==========================================================================
   Bayramlar / tadbir turlari — har biri uchun tayyor dizayn preseti
   (tema, effektlar, animatsiyalar, tayyor so'zlar, ba'zilari uchun sana)
   ========================================================================== */
export const HOLIDAYS = [
  {
    id: 'toy',
    label: "To'y",
    icon: 'mdi:ring',
    hint: 'Klassik oltin uslub',
    event_type: 'toy',
    preset: {
      theme: 'gold',
      ambient_effects: ['aurora', 'bokeh'],
      particle_effects: ['confetti', 'hearts', 'petals'],
      text_anim: 'fadeUp',
      card_anim: 'scaleIn',
      to_name: "Barcha do'stlarimizga",
      from_name: 'Bizdan',
      texts: [
        'Hurmatli mehmonlar!',
        'Bizning baxtimizga quvonch qo‘shing!',
        'Keling, birga nishonlaymiz!',
      ],
    },
  },
  {
    id: 'tugilgan_kun',
    label: "Tug'ilgan kun",
    icon: 'ph:cake',
    hint: 'Quvonchli va yorqin',
    event_type: 'tugilgan_kun',
    preset: {
      theme: 'rose',
      ambient_effects: ['bokeh', 'rays'],
      particle_effects: ['balloons', 'confetti', 'hearts'],
      text_anim: 'bounce',
      card_anim: 'elastic',
      to_name: 'Quvonchli tabriklaymiz!',
      from_name: 'Sizni sevuvchilar',
      texts: [
        "Tug'ilgan kuningiz muborak bo'lsin!",
        "Sizga sog'lik, baxt va katta yutuqlar tilaymiz!",
        'Har kuningiz bayramga o‘xshasin!',
      ],
    },
  },
  {
    id: 'oqituvchilar_kuni',
    label: "O'qituvchilar kuni",
    icon: 'ph:chalkboard-teacher',
    hint: 'Har yili 1-oktabr',
    event_type: 'bayram',
    date: { month: 10, day: 1 },
    preset: {
      theme: 'ocean',
      ambient_effects: ['rays', 'bokeh'],
      particle_effects: ['stars', 'glitter'],
      text_anim: 'fadeUp',
      card_anim: 'slideUp',
      to_name: 'Hurmatli o‘qituvchilarimizga',
      from_name: 'Sizning shogirdlaringiz',
      texts: [
        'Ustozlar kuni muborak bo‘lsin!',
        'Mehnatingiz samarali, sog‘ligingiz joyida bo‘lsin!',
        'Bilim bergan har bir so‘zingiz uchun rahmat!',
        'Siz bilan har doim faxrlanamiz.',
      ],
    },
  },
  {
    id: 'ramazon',
    label: 'Ramazon',
    icon: 'ph:moon-stars',
    hint: 'Ro‘za oyi — sana tanlanadi',
    event_type: 'bayram',
    preset: {
      theme: 'emerald',
      ambient_effects: ['smoke', 'aurora'],
      particle_effects: ['stars', 'glitter'],
      text_anim: 'blur',
      card_anim: 'zoomBlur',
      to_name: 'Barcha musulmon birodarlarimizga',
      from_name: 'Sizdan hurmat bilan',
      texts: [
        'Ramazon oyi muborak bo‘lsin!',
        'Ro‘zangiz qabul, ibodatlaringiz muttasil bo‘lsin!',
        'Shu oyda yuraklaringiz tinch, dasturxonlaringiz barakali bo‘lsin.',
      ],
    },
  },
  {
    id: 'eid_fitr',
    label: 'EID Bayrami',
    icon: 'ph:confetti',
    hint: 'Ro‘za hayiti',
    event_type: 'bayram',
    preset: {
      theme: 'gold',
      ambient_effects: ['rays', 'bokeh'],
      particle_effects: ['fireworks', 'stars', 'confetti'],
      text_anim: 'bounce',
      card_anim: 'elastic',
      to_name: 'Barcha yaqinlarimizga',
      from_name: 'Hayit bilan tabriklab',
      texts: [
        'Ro‘za hayitingiz muborak bo‘lsin!',
        'Bayram kuningiz qutlug‘ va xayrli bo‘lsin!',
        'Qilingan ibodatlar qabul bo‘lsin!',
      ],
    },
  },
  {
    id: 'qurbon_hayit',
    label: 'Qurbon hayit',
    icon: 'mdi:sheep',
    hint: 'Qurbon hayiti — sana tanlanadi',
    event_type: 'bayram',
    preset: {
      theme: 'emerald',
      ambient_effects: ['spotlight', 'aurora'],
      particle_effects: ['stars', 'fireworks', 'confetti'],
      text_anim: 'fadeUp',
      card_anim: 'dropIn',
      to_name: 'Barcha yaqinlarimizga',
      from_name: 'Hayit bilan',
      texts: [
        'Qurbon hayitingiz muborak bo‘lsin!',
        'Qilingan qurbonlaringiz Alloh tomonidan qabul bo‘lsin!',
        'Bayramingiz xayrli, rizqingiz barakali bo‘lsin!',
      ],
    },
  },
  {
    id: 'mustaqillik',
    label: 'Mustaqillik kuni',
    icon: 'ph:flag-banner',
    hint: 'Har yili 1-sentabr',
    event_type: 'bayram',
    date: { month: 9, day: 1 },
    preset: {
      theme: 'ocean',
      ambient_effects: ['rays', 'waves'],
      particle_effects: ['confetti', 'fireworks', 'stars'],
      text_anim: 'flip',
      card_anim: 'dropIn',
      to_name: 'Aziz vatandoshlar!',
      from_name: 'Oila va do‘stlar',
      texts: ['Mustaqilligimiz muborak bo‘lsin!', 'Vatan tinch, xalq obod bo‘lsin!'],
    },
  },
  {
    id: 'boshqa',
    label: 'Boshqa',
    icon: 'ph:sparkle',
    hint: 'O‘z uslubingizni tanlang',
    event_type: 'boshqa',
    preset: {
      theme: 'violet',
      ambient_effects: ['aurora', 'bokeh'],
      particle_effects: ['confetti', 'stars'],
      text_anim: 'fadeUp',
      card_anim: 'scaleIn',
      to_name: 'Hurmatli mehmonlar!',
      from_name: 'Bizdan',
      texts: ['Sizni kutamiz!', 'Quvonchli damlarda uchrashamiz!'],
    },
  },
]

export const HOLIDAY_LABELS = Object.fromEntries(HOLIDAYS.map((h) => [h.id, h.label]))

export function holidayById(id) {
  return HOLIDAYS.find((h) => h.id === id) || null
}

/** Berilgan oy-kundan keyingi kelgusi sana (yil o'tib ketgan bo'lsa — keyingi yil) */
export function nextOccurrence(month, day, after = new Date()) {
  const y = after.getFullYear()
  let d = new Date(y, month - 1, day, 18, 0, 0, 0)
  if (d.getTime() < after.getTime()) d = new Date(y + 1, month - 1, day, 18, 0, 0, 0)
  return d
}

export const THEMES = [
  {
    id: 'gold',
    name: 'Oltin kecha',
    bg1: '#14100a',
    bg2: '#241b09',
    bg3: '#4a3712',
    accent: '#f5c451',
    accent2: '#ffe9a8',
    txt: '#fdf7e8',
    muted: 'rgba(253,247,232,0.7)',
    swatch: ['#14100a', '#f5c451', '#ffe9a8'],
    palette: ['#f5c451', '#ffe9a8', '#fff7df', '#e8b93c', '#ff9db4'],
  },
  {
    id: 'rose',
    name: 'Atirgul',
    bg1: '#2a0713',
    bg2: '#4a0f24',
    bg3: '#7d1f3f',
    accent: '#ff9db4',
    accent2: '#ffd3de',
    txt: '#fff3f6',
    muted: 'rgba(255,243,246,0.7)',
    swatch: ['#2a0713', '#ff9db4', '#ffd3de'],
    palette: ['#ff9db4', '#ffd3de', '#ff6f91', '#ffffff', '#f5c451'],
  },
  {
    id: 'ocean',
    name: 'Moviy dengiz',
    bg1: '#03172b',
    bg2: '#062a44',
    bg3: '#0b4a6b',
    accent: '#5ed7ff',
    accent2: '#b7ecff',
    txt: '#eefaff',
    muted: 'rgba(238,250,255,0.7)',
    swatch: ['#03172b', '#5ed7ff', '#b7ecff'],
    palette: ['#5ed7ff', '#b7ecff', '#7dd3fc', '#ffffff', '#a78bfa'],
  },
  {
    id: 'violet',
    name: 'Binafsha tun',
    bg1: '#150a2c',
    bg2: '#28104f',
    bg3: '#4a1d8a',
    accent: '#c084fc',
    accent2: '#f0abfc',
    txt: '#f7f0ff',
    muted: 'rgba(247,240,255,0.7)',
    swatch: ['#150a2c', '#c084fc', '#f0abfc'],
    palette: ['#c084fc', '#f0abfc', '#a78bfa', '#ffffff', '#f5c451'],
  },
  {
    id: 'emerald',
    name: 'Zumrad',
    bg1: '#04231c',
    bg2: '#083b2e',
    bg3: '#0d5c45',
    accent: '#5eead4',
    accent2: '#a7f3d0',
    txt: '#effffb',
    muted: 'rgba(239,255,251,0.7)',
    swatch: ['#04231c', '#5eead4', '#a7f3d0'],
    palette: ['#5eead4', '#a7f3d0', '#ffffff', '#99f6e4', '#f5c451'],
  },
  {
    id: 'noir',
    name: 'Qora-oq',
    bg1: '#08080a',
    bg2: '#141417',
    bg3: '#2a2a30',
    accent: '#ffffff',
    accent2: '#d4d4d8',
    txt: '#ffffff',
    muted: 'rgba(255,255,255,0.65)',
    swatch: ['#08080a', '#8a8a92', '#ffffff'],
    palette: ['#ffffff', '#d4d4d8', '#a3a3ab', '#f5c451', '#c084fc'],
  },
]

/* Fon (ambient) effektlari — bir nechtasini birga tanlash mumkin */
export const AMBIENT_EFFECTS = [
  { id: 'aurora', label: 'Aurora', icon: 'ph:shooting-star' },
  { id: 'waves', label: 'To‘lqinlar', icon: 'ph:waves' },
  { id: 'spotlight', label: 'Projektor nuri', icon: 'ph:flashlight' },
  { id: 'bokeh', label: 'Bokeh nuqtalar', icon: 'ph:dots-three-circle' },
  { id: 'rays', label: 'Aylanuvchi nurlar', icon: 'ph:sun-dim' },
  { id: 'smoke', label: 'Sirli tuman', icon: 'ph:cloud-fog' },
]

/* Harakatli zarrachalar — canvas effektlari, ko‘p tanlash mumkin */
export const PARTICLE_EFFECTS = [
  { id: 'confetti', label: 'Konfetalar', icon: 'ph:confetti' },
  { id: 'hearts', label: 'Yurakchalar', icon: 'ph:heart' },
  { id: 'snow', label: 'Qor g‘unchalari', icon: 'ph:snowflake' },
  { id: 'stars', label: 'Yulduzlar', icon: 'ph:star' },
  { id: 'bubbles', label: 'Pufakchalar', icon: 'lucide:bubbles' },
  { id: 'petals', label: 'Atirgul barglari', icon: 'ph:flower' },
  { id: 'fireworks', label: 'Havoyi olovlar', icon: 'icon-park:fireworks' },
  { id: 'balloons', label: 'Uchuvchi sharlar', icon: 'ph:balloon' },
  { id: 'glitter', label: 'Tikranuvchi tufraq', icon: 'ph:star-four' },
  { id: 'rain', label: 'Romantik yomg‘ir', icon: 'ph:cloud-rain' },
]

/* Matn animatsiyalari — bitta tanlanadi */
export const TEXT_ANIMS = [
  { id: 'fadeUp', label: 'Ixcham ko‘tarilish', icon: 'ph:bird' },
  { id: 'typewriter', label: 'Chop etiluvchi', icon: 'ph:keyboard' },
  { id: 'neon', label: 'Neon yonishi', icon: 'ph:lightbulb' },
  { id: 'glitch', label: 'Glitch', icon: 'ph:television' },
  { id: 'rainbow', label: 'Kamalak ranglar', icon: 'ph:rainbow' },
  { id: 'bounce', label: 'Harflar sakraydi', icon: 'ph:tennis-ball' },
  { id: 'flip', label: 'Aylanib ochiladi', icon: 'ph:arrows-clockwise' },
  { id: 'blur', label: 'Xiralikdan tiniqlashuv', icon: 'ph:circle-half' },
]

/* Karta ochilish animatsiyalari — bitta tanlanadi */
export const CARD_ANIMS = [
  { id: 'scaleIn', label: 'Kattalashib', icon: 'ph:magnifying-glass-plus' },
  { id: 'slideUp', label: 'Pastdan ko‘tarilish', icon: 'ph:arrow-up' },
  { id: 'flipIn', label: 'RotateX ochilish', icon: 'ph:cards' },
  { id: 'zoomBlur', label: 'Ravishdan', icon: 'ph:camera' },
  { id: 'dropIn', label: 'Tushib kelib', icon: 'ph:parachute' },
  { id: 'elastic', label: 'Elastik', icon: 'ph:arrows-left-right' },
]

/* Default (tayyor) matnlar — tanlay qo'shing yoki o'zingiz yozing */
export const DEFAULT_TEXTS = [
  'Hurmatli mehmonlar!',
  'Bizning baxtimizga quvonch qo‘shing!',
  'Keling, birga nishonlaymiz!',
  'Sizni kutamiz!',
  'Barcha yaqinlarimizni kutamiz!',
  'Unutilmas oqsham bo‘lsin!',
  'Hayotimizning eng shirali lahzasida bizni yolg‘iz qoldirmang.',
  'Quvonchli damlarda uchrashamiz!',
  'Meherbun yuraklar bilan kutamiz.',
  'Sizsiz bu bayram to‘liq bo‘lmaydi.',
  'Nafis dasturxonimizda biz bilan bo‘ling.',
  'Bir lahza baxt uchun — butun umr xotira uchun!',
]

export const MAX_TEXTS = 6

/* --------------------------------------------------------------- */
/* Sanani o'zbekcha formatlash                                      */
/* --------------------------------------------------------------- */
const MONTHS = [
  'yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
  'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr',
]
const WEEKDAYS = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanaba']

export function formatDateUz(value) {
  const d = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const day = d.getDate()
  const month = MONTHS[d.getMonth()]
  const year = d.getFullYear()
  const wd = WEEKDAYS[d.getDay()]
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${day}-${month} ${year}-y, ${wd} · ${hh}:${mm}`
}

export function themeById(id) {
  return THEMES.find((t) => t.id === id) || THEMES[0]
}

/** XXXX-XXXX ko'rinishidagi kod */
export function prettyCode(code) {
  const raw = (code || '').replace(/[^a-z0-9]/gi, '').toUpperCase()
  return raw.length > 4 ? `${raw.slice(0, 4)}-${raw.slice(4)}` : raw
}
