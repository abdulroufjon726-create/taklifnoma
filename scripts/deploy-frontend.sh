#!/usr/bin/env bash
# Frontend'ni prodga chiqarish.
#
# Vercel loyihasida Root Directory = "frontend", shuning uchun deploy HAR DOIM
# repo ildizidan ishga tushishi kerak: frontend/ ichidan `vercel deploy`
# qilinsa CLI faqat o'sha papkani yuklaydi va Vercel "The specified Root
# Directory "frontend" does not exist" xatosi bilan yiqiladi.
# Bu skript qaysi papkadan chaqirilsa ham ildizga o'tadi.
#
# Lokal build kerak emas — Vercel manba kodini o'zi yuklab, `npm run build`
# ni serverda bajaradi.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f frontend/package.json ] || [ ! -f backend/manage.py ]; then
  echo "xato: repo ildizida emas (frontend/package.json yoki backend/manage.py topilmadi)" >&2
  exit 1
fi

exec npx --no-install vercel deploy --prod --yes "$@"
