#!/bin/sh
set -eu

: "${TS_AUTHKEY:?TS_AUTHKEY environment variable is required}"

mkdir -p /var/lib/tailscale /var/run/tailscale

# Tailscale userspace networking
tailscaled \
  --tun=userspace-networking \
  --socks5-server=127.0.0.1:1055 \
  --statedir=/var/lib/tailscale \
  --socket=/var/run/tailscale/tailscaled.sock &

# Tailscale ishga tushishini kutish
until tailscale --socket=/var/run/tailscale/tailscaled.sock status >/dev/null 2>&1; do
  sleep 1
done

# Tailnetga ulanish
tailscale --socket=/var/run/tailscale/tailscaled.sock up \
  --auth-key="$TS_AUTHKEY" \
  --hostname=render-taklifnoma

# PostgreSQL uchun TCP ko'prik
gost \
  -L=tcp://127.0.0.1:15432/100.66.226.26:5432 \
  -F=socks5://127.0.0.1:1055 &

# Django
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}"
