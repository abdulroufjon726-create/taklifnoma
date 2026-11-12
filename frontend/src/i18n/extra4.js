/* Xarita / manzil oqimi uchun matnlar (uz, ru, en). */

const uz = {
  map: {
    searchPh: 'Manzilni yozing yoki xaritadan belgilang',
    find: 'Topish',
    myLocation: 'Joylashuvim',
    hint: 'Xaritaga bosing yoki manzilni yozib "Topish"ni bosing.',
    notFound: "Manzil topilmadi — nomini boshqacha yozib ko'ring.",
    noNetwork: "Xaritaga ulanib bo'lmadi. Internetni tekshiring.",
    noGeo: "Brauzer joylashuvni qo'llab-quvvatlamaydi.",
    locating: 'Joylashuv aniqlanmoqda...',
    geoDenied: "Joylashuvga ruxsat berilmadi. Brauzer sozlamalaridan ruxsat bering.",
    route: "Yo'lni ko'rsatish",
    openGoogle: 'Google Maps',
    routeHint: "Yo'lni ko'rish uchun \"Yo'lni ko'rsatish\"ni bosing.",
    venue: 'Tadbir joyi',
    you: 'Siz shu yerdasiz',
    noRoute: "Yo'l topilmadi — Google Maps'da ko'ring.",
    routeSummary: '{km} km · taxminan {min} daqiqa',
    close: 'Yopish',
    title: 'Manzil',
  },
  profile: {
    setPwTitle: "Google bilan kirgansiz — email bilan ham kirish uchun parol o'rnating.",
    setPwPh: 'Yangi parol (kamida 8 belgi)',
    setPwBtn: 'Parolni saqlash',
    setPwDone: "Parol o'rnatildi. Endi email va parol bilan ham kirishingiz mumkin.",
    setPwErr: "Parol kamida 8 belgidan iborat bo'lsin.",
  },
}

const ru = {
  map: {
    searchPh: 'Введите адрес или отметьте на карте',
    find: 'Найти',
    myLocation: 'Моё местоположение',
    hint: 'Нажмите на карту или введите адрес и нажмите «Найти».',
    notFound: 'Адрес не найден — попробуйте другое название.',
    noNetwork: 'Не удалось загрузить карту. Проверьте интернет.',
    noGeo: 'Браузер не поддерживает геолокацию.',
    locating: 'Определяем местоположение...',
    geoDenied: 'Доступ к геолокации запрещён. Разрешите его в настройках браузера.',
    route: 'Показать маршрут',
    openGoogle: 'Google Maps',
    routeHint: 'Нажмите «Показать маршрут», чтобы увидеть дорогу.',
    venue: 'Место события',
    you: 'Вы здесь',
    noRoute: 'Маршрут не найден — откройте Google Maps.',
    routeSummary: '{km} км · примерно {min} мин',
    close: 'Закрыть',
    title: 'Адрес',
  },
  profile: {
    setPwTitle: 'Вы вошли через Google — задайте пароль, чтобы входить по email.',
    setPwPh: 'Новый пароль (минимум 8 символов)',
    setPwBtn: 'Сохранить пароль',
    setPwDone: 'Пароль задан. Теперь можно входить по email и паролю.',
    setPwErr: 'Пароль должен быть не короче 8 символов.',
  },
}

const en = {
  map: {
    searchPh: 'Type an address or pick a point on the map',
    find: 'Find',
    myLocation: 'My location',
    hint: 'Tap the map, or type an address and press Find.',
    notFound: 'Address not found — try a different name.',
    noNetwork: 'Could not reach the map. Check your connection.',
    noGeo: 'This browser does not support geolocation.',
    locating: 'Locating you...',
    geoDenied: 'Location permission was denied. Allow it in your browser settings.',
    route: 'Show route',
    openGoogle: 'Google Maps',
    routeHint: 'Press "Show route" to see the way there.',
    venue: 'Event venue',
    you: 'You are here',
    noRoute: 'No route found — open Google Maps instead.',
    routeSummary: '{km} km · about {min} min',
    close: 'Close',
    title: 'Location',
  },
  profile: {
    setPwTitle: 'You signed in with Google — set a password to also sign in with email.',
    setPwPh: 'New password (at least 8 characters)',
    setPwBtn: 'Save password',
    setPwDone: 'Password set. You can now sign in with email and password too.',
    setPwErr: 'Password must be at least 8 characters.',
  },
}

export const extra4 = { uz, ru, en }
