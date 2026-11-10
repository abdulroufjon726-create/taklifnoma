#!/bin/sh
set -eu

: "${TS_AUTHKEY:?TS_AUTHKEY is required}"

mkdir -p /var/lib/tailscale /var/run/tailscale

tailscaled \
  --tun=userspace-networking \
  --socks5-server=127.0.0.1:1055 \
  --statedir=/var/lib/tailscale \
  --socket=/var/run/tailscale/tailscaled.sock &

# Socket tayyor bo'lishini kutish
until [ -S /var/run/tailscale/tailscaled.sock ]; do
  sleep 1
done

# Tailscale tarmog'iga ulanish
tailscale --socket=/var/run/tailscale/tailscaled.sock up \
  --auth-key="$TS_AUTHKEY" \
  --hostname=render-taklifnoma

# PostgreSQL TCP ko'prigi
gost \
  -L=tcp://127.0.0.1:15432/100.66.226.26:5432 \
  -F=socks5://127.0.0.1:1055 &

# Django server
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}"
