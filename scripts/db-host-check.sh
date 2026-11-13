#!/bin/sh
# Prod bazasi turadigan kompyuterda ishga tushiring (Tailscale IP 100.66.226.26).
# Faqat o'qiydi — hech narsani o'zgartirmaydi.
set -u

echo "== 1. Tailscale =="
if command -v tailscale >/dev/null 2>&1; then
  tailscale status | head -5
  echo "IPv4: $(tailscale ip -4 2>/dev/null | head -1)"
else
  echo "tailscale topilmadi (Windows: C:\\Program Files\\Tailscale\\tailscale.exe)"
fi

echo
echo "== 2. Postgres =="
if command -v pg_isready >/dev/null 2>&1; then
  pg_isready -h 127.0.0.1 -p 5432
else
  echo "pg_isready topilmadi — Docker yoki xizmat holatini tekshiring"
fi

echo
echo "== 3. Tinglayotgan portlar =="
# Linux/macOS
(netstat -an 2>/dev/null || true) | grep -E "[:.]5432[[:space:]]" | head -3 || true

echo
echo "== 4. Docker (agar baza konteynerda bo'lsa) =="
if command -v docker >/dev/null 2>&1; then
  docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}' 2>/dev/null | grep -i postgres || echo "postgres konteyneri topilmadi"
else
  echo "docker yo'q"
fi

echo
echo "== 5. Kompyuter uxlab qolmasligi =="
echo "Windows: Settings → System → Power & sleep → Sleep = Never"
echo "macOS:   caffeinate -i &   (yoki Energy Saver sozlamalari)"
echo "Linux:   systemctl mask sleep.target suspend.target (ehtiyotkorlik bilan)"

echo
echo "Tayyor bo'lsa Render'da Restart qiling va tekshiring:"
echo "  curl -s https://taklifnoma-1.onrender.com/api/health/"
