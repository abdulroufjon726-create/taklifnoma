
#!/bin/sh
set -eu

: "${TS_AUTHKEY:?TS_AUTHKEY environment variable is required}"

mkdir -p /var/lib/tailscale /var/run/tailscale

echo "=== TAILSCALED ISHGA TUSHMOQDA ==="

tailscaled \
  --tun=userspace-networking \
  --socks5-server=127.0.0.1:1055 \
  --statedir=/var/lib/tailscale \
  --socket=/var/run/tailscale/tailscaled.sock &

# Socket yaratilishini kutish
tries=0
until [ -S /var/run/tailscale/tailscaled.sock ]; do
  tries=$((tries + 1))
  if [ "$tries" -gt 30 ]; then
    echo "XATO: Tailscale socket 30 soniyada yaratilmagan"
    exit 1
  fi
  sleep 1
done

echo "=== TAILSCALE SOCKET TAYYOR ==="
echo "=== TAILSCALE UP BOSHLANDI ==="

tailscale --socket=/var/run/tailscale/tailscaled.sock up \
  --auth-key="$TS_AUTHKEY" \
  --hostname=render-taklifnoma

echo "=== TAILSCALE MUVAFFAQIYATLI ULANDI ==="

tailscale --socket=/var/run/tailscale/tailscaled.sock status

echo "=== GOST ISHGA TUSHMOQDA ==="

gost \
  -L=tcp://127.0.0.1:15432/100.66.226.26:5432 \
  -F=socks5://127.0.0.1:1055 &

echo "=== DJANGO ISHGA TUSHMOQDA ==="

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}"
