/* ==========================================================================
   Bo'limlar (home / qanday boshlash / ro'yxatdan o'tish / konvertlar) uchun
   to'liq navigatsiya lug'ati.
   ========================================================================== */

const uz = {
  nav: {
    home: 'Bosh sahifa',
    howTo: 'Qanday boshlash',
    register: "Ro'yxatdan o'tish",
    envelopes: 'Mening taklifnomalarim',
    create: 'Yaratish',
    account: 'Hisob',
    login: 'Kirish',
  },
  start: {
    kicker: 'Uch qadam',
    title: 'Qanday boshlash',
    sub: "Taklifnoma yaratish uchun uchta oddiy qadam — bir daqiqada tayyor.",
    s1t: "Ro'yxatdan o'ting",
    s1d: "Email bilan yoki Google orqali kiring — taklifnomalaringiz hisobingizda saqlanadi.",
    s2t: "Ma'lumot va dizaynni tanlang",
    s2d: "Ism, sana, joy, so'zlar, shrift va effektlarni jonli ko'ring.",
    s3t: 'Kod bilan ulashing',
    s3d: 'Havolani yuboring — mehmonlar kod orqali ham ochishi mumkin.',
    cta: "Ro'yxatdan o'tish",
    ctaLogged: 'Yangi taklifnoma yaratish',
    codeLink: 'Kod bilan kirish',
    faq: 'Savol tug\'ilsa',
    q1: 'Taklifnoma bepulmi?',
    a1: "Ha, yaratish va ulashish bepul.",
    q2: 'Tahrirlash mumkinmi?',
    a2: "Ha — «Mening taklifnomalarim» bo'limida istalgan konvertni tahrirlaysiz.",
    q3: "Telefonda ochiladimi?",
    a3: "Ha, eng oddiy telefonlarda ham qotmasdan ochiladi.",
  },
  legacy: {
    badge: 'Bu qurilmada',
    hint: "Login'dan oldin yaratilgan taklifnomalar shu qurilmada saqlanadi va hisobingizga avtomatik bog'lanadi.",
  },
  loginExtra: {
    tooMany: "Juda ko'p urinish. 15 daqiqadan keyin qayta urinib ko'ring.",
    expired: "Sessiya muddati tugadi — qayta kiring.",
    registerKicker: "Ro'yxatdan o'tish",
    loginKicker: 'Kirish',
  },
}

const ru = {
  nav: {
    home: 'Главная',
    howTo: 'Как начать',
    register: 'Регистрация',
    envelopes: 'Мои приглашения',
    create: 'Создать',
    account: 'Аккаунт',
    login: 'Войти',
  },
  start: {
    kicker: 'Три шага',
    title: 'Как начать',
    sub: 'Три простых шага — приглашение готово за минуту.',
    s1t: 'Зарегистрируйтесь',
    s1d: 'Войдите по email или через Google — приглашения сохранятся в аккаунте.',
    s2t: 'Выберите данные и дизайн',
    s2d: 'Имена, дата, место, слова, шрифты и эффекты с живым просмотром.',
    s3t: 'Поделитесь кодом',
    s3d: 'Отправьте ссылку — гости смогут открыть и по коду.',
    cta: 'Зарегистрироваться',
    ctaLogged: 'Создать приглашение',
    codeLink: 'Вход по коду',
    faq: 'Частые вопросы',
    q1: 'Это бесплатно?',
    a1: 'Да, создание и отправка бесплатны.',
    q2: 'Можно редактировать?',
    a2: 'Да — в разделе «Мои приглашения» можно изменить любой конверт.',
    q3: 'Открывается на телефоне?',
    a3: 'Да, открывается даже на слабых телефонах.',
  },
  legacy: {
    badge: 'На этом устройстве',
    hint: 'Приглашения, созданные до входа, хранятся на этом устройстве и привязываются к аккаунту автоматически.',
  },
  loginExtra: {
    tooMany: 'Слишком много попыток. Попробуйте через 15 минут.',
    expired: 'Сессия истекла — войдите снова.',
    registerKicker: 'Регистрация',
    loginKicker: 'Вход',
  },
}

const en = {
  nav: {
    home: 'Home',
    howTo: 'How to start',
    register: 'Sign up',
    envelopes: 'My invitations',
    create: 'Create',
    account: 'Account',
    login: 'Sign in',
  },
  start: {
    kicker: 'Three steps',
    title: 'How to start',
    sub: 'Three simple steps — ready in a minute.',
    s1t: 'Create an account',
    s1d: 'Sign in with email or Google — your invitations are saved to your account.',
    s2t: 'Pick content and design',
    s2d: 'Names, date, place, words, fonts and effects with a live preview.',
    s3t: 'Share the code',
    s3d: 'Send the link — guests can also open it with the code.',
    cta: 'Sign up',
    ctaLogged: 'Create an invitation',
    codeLink: 'Enter a code',
    faq: 'Questions',
    q1: 'Is it free?',
    a1: 'Yes, creating and sharing is free.',
    q2: 'Can I edit it?',
    a2: 'Yes — edit any envelope from “My invitations”.',
    q3: 'Does it open on a phone?',
    a3: 'Yes, it opens smoothly even on low-end phones.',
  },
  legacy: {
    badge: 'On this device',
    hint: 'Invitations created before signing in stay on this device and are linked to your account automatically.',
  },
  loginExtra: {
    tooMany: 'Too many attempts. Try again in 15 minutes.',
    expired: 'Your session expired — please sign in again.',
    registerKicker: 'Sign up',
    loginKicker: 'Sign in',
  },
}

export const extra3 = { uz, ru, en }
