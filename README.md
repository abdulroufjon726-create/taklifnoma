# 💌 Taklifnoma — Onlayn taklifnoma yasovchi

Foydalanuvchi o'z taklifnomasini onlayn yasaydi: ism-familiya, kimdan-kimga, qachonlig'i,
aniq taymer (kun/soat/daqiqa/soniya), ko'p sonli effekt va animatsiyalar.
Tayyor taklifnoma **maxfiy 8 belgili kod** orqali ochiladi — login sahifasiga o'xshash
sahifaga kod yoziladi va aynan o'sha taklifnoma ochiladi.

## Texnologiyalar

| Qatlam   | Texnologiya                          |
| -------- | ------------------------------------ |
| Frontend | Vue 3, Vite, Tailwind CSS 4, Vue Router |
| Backend  | Python, Django 6, Django REST Framework |
| BD       | SQLite                               |

## Ishga tushirish (development)

### 1. Backend (Django) — port 8000

```bash
cd backend
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

### 2. Frontend (Vite) — port 5173

```bash
cd frontend
npm install
npm run dev
```

Keyin brauzerda **http://localhost:5173** ochiladi.
(Vite `/api` so'rovlarini avtomatik ravishda Django'ga uzatadi.)

## Production

```bash
cd frontend && npm run build     # dist/ papkaga yig'iladi
cd ../backend && python manage.py runserver 127.0.0.1:8000
```

Build'dan keyin butun ilova **http://127.0.0.1:8000** da ishlaydi:
Django API bilan birga frontend'ning `index.html` va `assets/` fayllarini ham beradi.

## API

| Metod | Endpoint                  | Vazifasi                                          |
| ----- | ------------------------- | ------------------------------------------------- |
| POST  | `/api/invitations/`       | Yangi taklifnoma yasash → `{code: "XXXXXXXX"}`    |
| GET   | `/api/invitations/<code>/`| Kod bo'yicha taklifnomani olish (katta-kichik farqsiz) |

Yasashda `category` (bayram kategoriyasi) va `event_type` maydonlari ham yuboriladi.

## Maxfiylik ta'minoti

- **Ro'yxat/ro'yxatdan o'tish yo'q** — `GET /api/invitations/` (ro'yxat) **405** qaytaradi:
  taklifnomalarni ro'yxatini ko'rishning yo'li yo'q.
- Noto'g'ri kod → **404** ("topilmadi") — boshqa taklifnomaga kirishning iloji yo'q.
- Kod 8 belgidan iborat (32 ta belgi: 0/O, 1/I chiqarilgan) — taxmin qilish deyarli mumkin emas.
- DRF anonim rate-limit (120 so'rov/daqqa) kodni terib o'rgatishdan himoya qiladi.
- **Bitta kodni 1, 2, 3 va undan ortiq odam** cheklanmasdan ko'ra oladi — ko'rishlar soniga
  cheklov yo'q, faqat `views` hisoblagichi bor.

## Imkoniyatlar

- **8 ta bayram / tadbir turi**: To'y, Tug'ilgan kun, **O'qituvchilar kuni**,
  **Ramazon**, **EID Bayrami**, **Qurbon hayit**, Mustaqillik kuni, Boshqa. Har birini bosganingizda
  **tayyor dizayn preseti** qo'llanadi: tema, fon/harakatli effektlar, animatsiyalar va bayramga mos
  matnlar. Qat'iy sanali bayramlarda (1-oktabr, 1-sentabr) sana **avtomatik to'ldiriladi** — keyingi
  keladigan sanaga. Foydalanuvchi o'zi o'zgartirgan matn/sana preset bosib ketmaydi.
  Kategoriya backendga saqlanadi.

- **Yasovchi paneli**: tadbir turi, ism/familiya, kimdan-kimga, joy, sana+vaqt,
  tayyor (default) matnlar yoki o'z matni, 6 ta dizayn temasi, jonli ko'rinish.
- **Effekt va animatsiyalar** (bir nechtasini birga tanlash mumkin):
  - 6 ta fon effekti: aurora, to'lqinlar, projektor nuri, bokeh, aylanuvchi nurlar, tuman
  - 10 ta harakatli effekt (canvas): konfetalar, yurakchalar, qor, yulduzlar, pufakchalar,
    atirgul barglari, havoyi olovlar, sharlar, porlash, yomg'ir
  - 8 ta matn animatsiyasi: ixcham, chop etiluvchi (typewriter), neon, glitch, kamalak,
    harflar sakraydi, aylanuvchi, xiralikdan tiniqlashuv
  - 6 ta karta ochilish animatsiyasi
  - **Standart animatsiyalar doim yoqilgan**: yumshoq suzish, taymer nuri, yulduzcha titrashi
- **Taklifnoma sahifasi**: to'liq ekran, **scrollsiz** — barcha o'lchamlarga mos (container
  query), soniyagacha aniq taymer, tadbir boshlanganda tabrik.
- **Ulashish**: kod + havola + QR nusxa olish; kirish sahifasida noto'g'ri kod uchun
  xatolik va silkinish animatsiyasi.

## Struktura

```
backend/
  config/          # Django sozlamalari, URL'lar (SPA fallback bilan)
  invitations/     # modellari, API, admin
frontend/
  src/
    views/         # BuilderView, EnterView, InvitationView
    components/    # InvitationStage, Countdown, AnimatedText, ParticleCanvas...
    effects/       # canvas zarrachalar dvigateli (10 effekt)
    data/          # katalog: temalar, effektlar, animatsiyalar, default matnlar
    assets/        # dizayn tizimi (Tailwind + animatsiyalar)
```
