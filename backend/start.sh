#!/bin/sh
set -eu

# Prod bazasi ikki xil bo'lishi mumkin:
#   1) Tailscale orqali shaxsiy kompyuterdagi Postgres
#      (DATABASE_URL ...@127.0.0.1:15432, gost ko'prigi orqali)
#   2) Managed Postgres — Neon / Render / Supabase (to'g'ridan-to'g'ri ulanadi)
#
# Tunnel faqat 1-holatda ko'tariladi. Shu tufayli managed bazaga o'tish uchun
# kod emas, faqat DATABASE_URL ni almashtirish kifoya (TS_AUTHKEY kerak emas).

case "${DATABASE_URL:-}" in
  *@127.0.0.1:* | *@localhost:* | *@127.0.0.1/* | *@localhost/*) needs_tunnel=1 ;;
  *) needs_tunnel=0 ;;
esac

if [ "$needs_tunnel" = 1 ]; then
  : "${TS_AUTHKEY:?TS_AUTHKEY environment variable is required for the Tailscale tunnel}"

  mkdir -p /var/lib/tailscale /var/run/tailscale

  # Tailscale userspace networking
  tailscaled \
    --tun=userspace-networking \
    --socks5-server=127.0.0.1:1055 \
    --statedir=/var/lib/tailscale \
    --socket=/var/run/tailscale/tailscaled.sock &

  # Tailscale ishga tushishini kutish (abadiy osilib qolmasin)
  tries=0
  until tailscale --socket=/var/run/tailscale/tailscaled.sock status >/dev/null 2>&1; do
    tries=$((tries + 1))
    if [ "$tries" -gt 30 ]; then
      echo "tailscaled 30 soniyada ishga tushmadi" >&2
      exit 1
    fi
    sleep 1
  done

  # Tailnetga ulanish (auth key eskirgan bo'lsa shu qadam yiqiladi)
  tailscale --socket=/var/run/tailscale/tailscaled.sock up \
    --auth-key="$TS_AUTHKEY" \
    --hostname=render-taklifnoma

  # PostgreSQL uchun TCP ko'prik
  gost \
    -L=tcp://127.0.0.1:15432/100.66.226.26:5432 \
    -F=socks5://127.0.0.1:1055 &
else
  echo "DATABASE_URL managed Postgres'ni ko'rsatyapti — Tailscale tunnel kerak emas"
fi

# Django
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}"
