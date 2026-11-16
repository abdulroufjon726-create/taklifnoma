#!/usr/bin/env bash
# Frontend'ni prodga chiqarish.
#
# Vercel loyihasida Root Directory = "frontend". Shu sababli deploy HAR DOIM
# repo ildizidan ishga tushishi kerak: frontend/ ichidan `vercel deploy`
# qilinsa CLI faqat o'sha papkani yuklaydi va Vercel "The specified Root
# Directory "frontend" does not exist" xatosi bilan yiqiladi (build 601ms da
# Error bo'lib qoladi). Bu skript qaysi papkadan chaqirilsa ham ildizga o'tadi.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f frontend/package.json ] || [ ! -f vercel.json ]; then
  echo "xato: repo ildizida emas (frontend/ yoki vercel.json topilmadi)" >&2
  exit 1
fi

echo "→ build (frontend/)"
(cd frontend && npm run build)

echo "→ deploy (repo ildizidan)"
exec npx --no-install vercel deploy --prod --yes "$@"
