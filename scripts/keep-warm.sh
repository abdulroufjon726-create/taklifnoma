#!/usr/bin/env bash
# Taklifnoma backend'ini uyg'oq ushlab turadigan pinger (Linux/macOS).
#
# Render bepul instansiyasi 15 daqiqa harakatsizlikdan keyin uxlaydi. Bu skript
# har 4 daqiqada /api/health/ ga ping yuboradi (u bazaga SELECT 1 qiladi, shu
# bilan Postgres ham uyg'oq qoladi).
#
# Ishlatish:
#   1) Bir marta:  ./scripts/keep-warm.sh --once
#   2) Doimiy:    ./scripts/keep-warm.sh
#   3) cron:      */4 * * * * /path/taklifnoma/scripts/keep-warm.sh --once
#   4) systemd:   systemd-run --user --unit=taklifnoma-keep-warm \
#                   --on-active=0 --timer-property=AccuracySec=1s \
#                   /path/taklifnoma/scripts/keep-warm.sh
set -euo pipefail

URL="${KEEP_WARM_URL:-https://taklifnoma-1.onrender.com/api/health/}"
INTERVAL="${KEEP_WARM_INTERVAL:-240}"
LOG="${KEEP_WARM_LOG:-$(dirname "$0")/../keep-warm.log}"

ping_once() {
  local code start took note
  start=$(date +%s)
  note=$(curl -sS --max-time 45 -o /tmp/keep-warm.json -w '%{http_code}' "$URL" 2>/dev/null || echo 000)
  code="$note"
  took=$(( $(date +%s) - start ))
  note=$(tr -d '\n' < /tmp/keep-warm.json 2>/dev/null | cut -c1-90 || true)
  printf '%s  HTTP %-3s %4ss  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$code" "$took" "$note" | tee -a "$LOG"
  [ "$code" = "200" ]
}

if [ "${1:-}" = "--once" ]; then
  ping_once || { sleep 20; ping_once; }
  exit $?
fi

echo "keep-warm: $URL har ${INTERVAL}s ping qilinadi. To'xtatish: Ctrl+C"
while true; do
  ping_once || { sleep 15; ping_once || true; }
  sleep "$INTERVAL"
done
