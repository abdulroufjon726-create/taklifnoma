# Prod baza: tiklash va managed Postgres'ga o'tish

## Hozirgi holat (nima uchun 503)

```
Brauzer → Vercel (frontend) → Render Web Service (Django, free)
                                     │
                                     ├─ tailscaled (userspace, TS_AUTHKEY bilan)
                                     └─ gost 127.0.0.1:15432 → 100.66.226.26:5432
                                                                  │
                                                     shaxsiy kompyuterdagi Postgres
```

`DATABASE_URL` ichida `127.0.0.1:15432` turadi, ya'ni Django Render konteyneridagi
`gost` ko'prigi orqali **uydagi kompyuter**dagi Postgres'ga ulanadi. O'sha kompyuter
o'chsa, uxlasa, Tailscale uzilsa yoki `TS_AUTHKEY` eskirsa — `/api/health/` 503,
qolgan API'lar 500 qaytaradi.

Diagnostika belgisi:

```json
{"status":"error","database":"down",
 "migration_error":"connection failed: connection to server at \"127.0.0.1\", port 15432 failed: server closed the connection unexpectedly"}
```

- `127.0.0.1:15432` — konteyner ichidagi `gost` ko'prigi.
- `server closed the connection unexpectedly` — ko'prik tirik, lekin orqa tomon
  (Tailscale → 100.66.226.26:5432) javob bermayapti.

---

## 1. Tez tiklash (bazasi turgan kompyuterda)

Bazasi turadigan kompyuterda (Tailscale IP `100.66.226.26`) quyidagilarni tekshiring:

```bash
# 1) Tailscale tirikmi va IP o'sha ekanmi
tailscale status
tailscale ip -4                 # 100.66.226.26 chiqishi kerak

# 2) Postgres ishlayaptimi va 5432 da tinglayaptimi
pg_isready -h 127.0.0.1 -p 5432
# Docker'da bo'lsa:
docker ps --filter ancestor=postgres
docker logs --tail 30 <postgres-konteyner>

# 3) Kompyuter uxlab qolmasin (Windows: Power & sleep → Never; macOS: caffeinate)
# 4) Lokal tarmoqdan tashqi ulanishga ruxsat (pg_hba.conf listen_addresses)
```

Bazaga **boshqa** kompyuterdan sinov (Render'dan mustaqil tekshiruv):

```bash
psql "postgresql://USER:PASSWORD@100.66.226.26:5432/DBNAME?sslmode=prefer" -c "select 1"
```

Keyin Render'da tunnelni qayta ko'tarish:

1. **Render → taklifnoma-api → Manual Deploy → Restart service** (yoki `git push` —
   `autoDeploy: true`).
2. Loglarda `tailscale ... up` xatosiz o'tganini ko'ring:
   `Render → Logs` → `tailscaled`, `gost`, `Booting worker`.
3. Tekshirish:

```bash
curl -s https://taklifnoma-1.onrender.com/api/health/     # {"status":"ok",...}
```

### Eng ko'p uchraydigan sabab: `TS_AUTHKEY` eskirdi

Render bepul instansiya uxlaganda konteyner qayta ko'tariladi va Tailscale'ga
**yangi auth key** bilan kiradi. Kalit bir martalik yoki muddati o'tgan bo'lsa,
`tailscale up` yiqiladi (yoki tailnet'ga kirmaydi) → baza yo'q.

Yechim: Tailscale admin → **Settings → Keys → Generate auth key**
(belgilar: *Reusable*, *Ephemeral* emas, expiry 90 kun) → nusxasini Render →
`taklifnoma-api` → **Environment → `TS_AUTHKEY`** ga qo'yish → **Save** (avtomatik
qayta deploy bo'ladi).

> Bu qadam har 90 kunda takrorlanadi. Shu sababli pastdagi 3-bo'lim (managed
> Postgres) uzoq muddatda ancha arzon — bir marta sozlanadi va unutiladi.

### Tunnel ishlamayotganini qanday aniqlash

Render loglarida:

```
tailscaled: ... state: NeedsLogin
```

yoki

```
gost: ... dial tcp 100.66.226.26:5432: i/o timeout
```

— birinchi holat `TS_AUTHKEY`, ikkinchisi bazasi turgan kompyuter/Tailscale
muammosi.

---

## 2. Kod tomoni allaqachon tayyor

`backend/start.sh` endi tunnelni **faqat kerak bo'lganda** ko'taradi:

```sh
case "${DATABASE_URL:-}" in
  *@127.0.0.1:* | *@localhost:*) needs_tunnel=1 ;;
  *) needs_tunnel=0 ;;
esac
```

Ya'ni `DATABASE_URL` managed bazaga o'tsa, `tailscaled`/`gost` umuman ishga
tushmaydi va `TS_AUTHKEY` talab qilinmaydi — boshqa kod o'zgartirish kerak emas.
`config/settings.py` ham `DATABASE_URL` bo'lmasa ishlamaydi (SQLite fallback yo'q),
`/api/health/` esa baza turmasa 503 qaytaradi — ya'ni deploy "yashil" bo'lib,
aslida buzuq bo'lib qolmaydi.

---

## 3. Managed Postgres'ga o'tish (Neon misolida)

Natija: baza 24/7 ishlaydi, uydagi kompyuterga bog'liq bo'lmaydi, API latency
1–2 s dan ~100–300 ms ga tushadi, `TS_AUTHKEY` muammosi yo'qoladi.

### 3.1. Baza yaratish

1. [neon.com](https://neon.com) → **New Project** (region: Frankfurt yoki
   Render bilan bir xil regionga yaqinrog'ini tanlang).
2. **Connect** → *Pooled connection* satrini oling:
   `postgresql://user:pass@ep-xxx-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require`
3. Parolni xavfsiz joyda saqlang (chatga yozmang).

> Muqobil: **Render Postgres** (bir xil dashboard, ichki tarmoqda tez) yoki
> **Supabase**. Muhimi — `postgresql://...` va `sslmode=require`.

### 3.2. Render'ga ulash

1. Render → `taklifnoma-api` → **Environment**:
   - `DATABASE_URL` = Neon pooled satri
   - `TS_AUTHKEY` ni **o'chirib tashlang** (endi kerak emas)
   - ixtiyoriy: `DJANGO_DB_CONNECT_TIMEOUT=10` (default shu)
2. **Manual Deploy** → loglarda:
   ```
   DATABASE_URL managed Postgres'ni ko'rsatyapti — Tailscale tunnel kerak emas
   Applying migrations... OK
   ```
3. `curl -s https://taklifnoma-1.onrender.com/api/health/` →
   `{"status":"ok","database":"up","engine":"postgresql",...}`

### 3.3. Eski ma'lumotlarni ko'chirish

Bazasi turgan kompyuterda (eski baza ishlab turgan paytda):

```bash
# 1) Eski bazadan dump (schema + data)
pg_dump "postgresql://USER:PASS@127.0.0.1:5432/DBNAME" \
  --no-owner --no-privileges -Fc -f taklifnoma.dump

# 2) Yangi bazaga yuklash
pg_restore --no-owner --no-privileges \
  -d "postgresql://USER:PASS@ep-xxx-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require" \
  taklifnoma.dump
```

Muhim: dump → restore orasida yangi yozuvlar kelib qolmasligi uchun saytni
qisqa vaqtga to'xtatish (yoki `maintenance` rejimi) tavsiya etiladi.

### 3.4. Tekshirish ro'yxati

- [ ] `/api/health/` → 200, `"database":"up"`
- [ ] Ro'yxatdan o'tish / email+parol bilan kirish ishlaydi
- [ ] `POST /api/invitations/` bilan yangi taklifnoma yaratiladi va ochiladi
- [ ] `PATCH`/`DELETE` faqat egasida ishlaydi (403 boshqalarga)
- [ ] Render'da `TS_AUTHKEY` yo'q, loglarda `tailscaled` umuman yo'q
- [ ] Eski kompyuter o'chirilgandan keyin ham sayt ishlaydi

### 3.5. Orqaga qaytish (rollback)

Muammo chiqsa: Render → Environment → `DATABASE_URL` ni eski
`...@127.0.0.1:15432/...` ga qaytarish, `TS_AUTHKEY` ni tiklash, Manual Deploy.
Eski baza o'chirilmagan bo'lsa, ma'lumot joyida qoladi (dump faylini ham saqlang).

### 3.6. Tozalash

- Bazasi turgan kompyuterda Postgres'ni o'chirish shart emas — avval bir hafta
  kuzatib, keyin o'chirish mumkin.
- Render → `TS_AUTHKEY` o'chirilganini tasdiqlang.
- Neon bepul tarifi uxlab qolishi mumkin (5 daqiqa harakatsizlik), lekin
  uyg'onish <1 s bo'ladi; `.github/workflows/keepalive.yml` har 10 daqiqada
  `/api/health/` ni urib, bazani ham uyg'oq tutadi.

---

## 4. Narx / chegaralar

| | hozir (uydagi baza) | Neon free | Render Postgres |
|---|---|---|---|
| Narx | 0 | 0 | bepul tarif bor (muddatli) |
| 24/7 | yo'q (kompyuter o'chsa — sayt o'chadi) | ha | ha |
| Latency | 1–2 s (tunnel) | ~100–300 ms | eng past (ichki tarmoq) |
| Xavfsizlik | tunnel + auth key | TLS | TLS |
| Backup | qo'lda | avtomatik (cheklangan) | bor |

---

## 5. Foydali buyruqlar

```bash
# Prod health (baza holati bilan)
curl -s https://taklifnoma-1.onrender.com/api/health/ | python -m json.tool

# Lokal: baza bilan ishlash
cd backend && python manage.py migrate
cd backend && python manage.py test accounts invitations

# Tunnelni lokal tekshirish (bazasi turgan kompyuterda)
./scripts/db-host-check.sh
```
