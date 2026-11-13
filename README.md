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
| BD       | PostgreSQL (prod) / SQLite (lokal)   |

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

## Deploy (production cloud)

| Qatlam   | Xizmat  | Holat |
| -------- | ------- | ----- |
| Frontend | Vercel  | ✅ https://taklifnoma-007.vercel.app |
| Backend  | Render  | ✅ https://taklifnoma-1.onrender.com |
| Repo     | GitHub (private) | https://github.com/abdulroufjon726-create/taklifnoma |

### Backend → Render (blueprint)

1. [render.com/dashboard](https://render.com/dashboard) → **New +** → **Blueprint**
2. `abdulroufjon726-create/taklifnoma` repo'ni tanlang (GitHub ulanishi so'raladi)
3. `render.yaml` avtomatik o'qiladi: Python xizmati, `migrate` + `collectstatic` +
   `gunicorn` — hech narsa qo'lda sozlash shart emas
4. Xizmat URL'i: **https://taklifnoma-1.onrender.com**
   (`frontend/vercel.json` va `frontend/src/api.js` shu manzilga sozlangan)

Render env variantlari (xizmat → Environment):

- `DJANGO_SECRET_KEY` — blueprint avtomatik generatsiya qiladi
- `DJANGO_ALLOWED_HOSTS` — `taklifnoma-1.onrender.com,.onrender.com`
- `DJANGO_CORS_ORIGINS` — agar aniq domenga qisqartirilsa: `https://taklifnoma-007.vercel.app`
  (hozir bo'sh → hamma manzilga ruxsat, ochiq API kod orqali himoyalangan)
- `DATABASE_URL` — **majburiy (prod)**: Postgres (Render Postgres / Neon / Supabase,
  pooled URL). Berilmasa faqat SQLite ishlatiladi va u prod'da mos emas.
  **Diqqat:** avvalgi "Postgres ishlamasa SQLite'ga jimgina o'tish" olib tashlandi —
  endi Postgres bo'lmasa `GET /api/health/` **503** qaytaradi va Render deploy'i
  "unhealthy" bo'lib ko'rinadi (ma'lumot yo'qolmaydi, muammo darhol bilinadi).

> Servis har ko'tarilishida `python manage.py migrate --noinput` bajariladi;
> qo'shimcha himoya sifatida `config/wsgi.py` bo'sh bazani aniqlab, migratsiyani
> o'zi ham qo'llaydi (Docker/`start.sh` bilan ishga tushganda ham). Shu tufayli
> bo'sh baza bilan API 500 bermaydi. Tirikligini `GET /api/health/` orqali
> tekshirish mumkin. Kerak bo'lsa `DJANGO_AUTO_MIGRATE=0` bilan o'chiriladi.

### Google bilan kirishni yoqish

Kod tayyor: kalitlar qo'yilishi bilan login sahifasidagi "Google bilan davom etish"
tugmasi avtomatik ishlaydi (sozlanmagan bo'lsa tugma o'chirilgan holatda turadi va
email/parol ishlatiladi). Kerak bo'lgani — Google Cloud'dan bitta OAuth client:

1. [console.cloud.google.com](https://console.cloud.google.com) → loyiha yaratish
2. **APIs & Services → OAuth consent screen** → External → nom va emailni to'ldirish
   (Testing rejimida qoldirsangiz, sinov foydalanuvchilarini qo'shishni unutmang)
3. **Credentials → Create credentials → OAuth client ID → Web application**
4. **Authorized redirect URIs** ga aynan shu manzilni yozing:
   `https://taklifnoma-1.onrender.com/api/auth/google/callback/`
   (aniq manzilni `GET /api/auth/config/` javobidagi `redirect_uri` dan ham olish mumkin)
5. Render → **taklifnoma-api** → Environment bo'limiga qo'shing:
   - `GOOGLE_CLIENT_ID` — `xxxx.apps.googleusercontent.com`
   - `GOOGLE_CLIENT_SECRET` — `xxxx`
   - ixtiyoriy: `FRONTEND_URL` = `https://taklifnoma-007.vercel.app`
6. Saqlang (Render o'zi qayta ishga tushiradi) → `GET /api/auth/config/`
   `{"google": true, "redirect_uri": "..."}` qaytarishi kerak; shundan keyin tugma ishlaydi.

> Kalitlarni `backend/.env` ga ham yozish mumkin (git'ga qo'shilmaydi).
> Oqim testlari Google serveriga murojaat qilmasdan ishlaydi:
> `cd backend && python manage.py test accounts`.

### Frontend → Vercel

Loyiha nomi **taklifnoma**, asosiy domen **taklifnoma-007.vercel.app**.

```bash
cd frontend
vercel deploy --prod --yes
```

`vercel.json` build paytida `VITE_API_BASE_URL` ni Render backend manziliga
o'rnatadi — frontend API'ga **to'g'ridan-to'g'ri** (CORS ochiq) ulanadi,
`/api` proksisiz. Env o'rnatilmasa ham `src/api.js` dagi zaxira manzil
ishlatiladi. Barcha yo'llar → `index.html` (SPA history mode).

> **Izoh:** agar `vercel deploy` `readyState: BLOCKED` bilan tugasa, bu git
> kontekstidagi deploy bilan bog'liq muammo — frontend'ni `.git`'siz katalogdan
> (masalan `git archive` yoki nusxa orqali) deploy qiling: ishlagan usul.

## API

| Metod | Endpoint                  | Vazifasi                                          |
| ----- | ------------------------- | ------------------------------------------------- |
| GET   | `/api/health/`            | Servis va baza holati (`200 ok` / `503`)           |
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
- **Ikonkalar**: barcha emoji stikerlar o'rniga **Iconify** ikonkalari (Phosphor/MDI/Lucide) —
  52 ta ikona `frontend/src/data/icons.json` ichida **lokal** saqlanadi, runtime'da
  API'ga so'rov yo'q → yuklanish tez va yengil.
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
