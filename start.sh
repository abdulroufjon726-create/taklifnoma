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

echo "=== SOCKS5 TCP TEST ==="
if timeout 3 sh -c 'echo -ne "\x05\x01\x00" | nc 127.0.0.1 1055 | head -c 2' 2>/dev/null | od -An -tx1; then
  echo "SOCKS5 test completed"
else
  echo "SOCKS5 test failed"
fi

# PostgreSQL uchun TCP ko'prik
gost \
  -L=tcp://127.0.0.1:15432/100.66.226.26:5432 \
  -F=socks5://127.0.0.1:1055 &

# Django
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}"
