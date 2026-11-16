#!/data/data/com.termux/files/usr/bin/bash
# Taklifnoma backend pingeri — Termux (Android) uchun.
#
# Render bepul instansiyasi 15 daqiqa harakatsizlikdan keyin uxlaydi. Bu skript
# har 5 daqiqada /api/health/ ga ping yuboradi; u bazaga SELECT 1 qiladi, shu
# bilan Postgres ham uyg'oq qoladi.
#
# Ishlatish:
#   ~/keep-warm.sh --once     # cron/JobScheduler uchun bir marta
#   ~/keep-warm.sh            # doimiy tsikl (terminal ochiq turganda)
#   ~/keep-warm.sh --status   # oxirgi 5 yozuvni ko'rsatadi
set -uo pipefail

URL="${KEEP_WARM_URL:-https://taklifnoma-1.onrender.com/api/health/}"
INTERVAL="${KEEP_WARM_INTERVAL:-300}"   # 5 daqiqa
LOG="${KEEP_WARM_LOG:-$HOME/keep-warm.log}"

log() {
  printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG"
}

ping_once() {
  local code took body
  took=$(date +%s)
  body=$(curl -sS -H 'X-Keep-Warm: phone' --max-time 45 -o "$TMPDIR/keep-warm.json" -w '%{http_code}' "$URL" 2>/dev/null) || body="000"
  code="$body"
  took=$(( $(date +%s) - took ))
  body=$(tr -d '\n' < "$TMPDIR/keep-warm.json" 2>/dev/null | cut -c1-80 || true)
  log "HTTP $code  ${took}s  $body"
  [ "$code" = "200" ]
}

case "${1:-}" in
  --status)
    if [ -f "$LOG" ]; then tail -n 5 "$LOG"; else echo "log hali yo'q: $LOG"; fi
    exit 0
    ;;
  --once)
    if ping_once; then exit 0; fi
    sleep 15
    ping_once
    exit $?
    ;;
esac

# Android'da CPU uxlab qolmasin (termux-api o'rnatilgan bo'lsa)
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock 2>/dev/null || true

log "keep-warm boshlandi: $URL har ${INTERVAL}s"
while true; do
  if ! ping_once; then
    sleep 15
    ping_once || true
  fi
  sleep "$INTERVAL"
done
