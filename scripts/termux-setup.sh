#!/data/data/com.termux/files/usr/bin/bash
# Termux'ni (Redmi Note 9) har 5 daqiqada ping yuboradigan qilib sozlash.
# Bu skript PHONE ichida, Termux terminalida bir marta ishga tushiriladi:
#
#   bash termux-setup.sh
#
# Nima qiladi:
#   1) paketlar: curl, cronie, termux-services, termux-api
#   2) ~/keep-warm.sh yozadi (pinger)
#   3) crontab'ga "*/5 * * * *" qo'shadi (takrorlanmaydi)
#   4) crond'ni termux-services orqali yoqadi
#   5) Termux:Boot uchun avtomatik start skriptini yozadi
#   6) bir marta sinov ping yuboradi
set -uo pipefail

HOME_DIR="${HOME:-/data/data/com.termux/files/home}"
PINGER="$HOME_DIR/keep-warm.sh"
LOG="$HOME_DIR/keep-warm.log"
CRON_LOG="$HOME_DIR/keep-warm.cron.log"
SV_DIR="$PREFIX/var/service/crond"

echo "== 1/5 paketlar =="
pkg update -y >/dev/null 2>&1 || true
pkg install -y curl cronie termux-services termux-api || {
  echo "xato: paketlarni o'rnatib bo'lmadi (internetni tekshiring)"; exit 1; }

echo "== 2/5 pinger: $PINGER =="
cat > "$PINGER" <<'PINGER_EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -uo pipefail
URL="${KEEP_WARM_URL:-https://taklifnoma-1.onrender.com/api/health/}"
LOG="${KEEP_WARM_LOG:-$HOME/keep-warm.log}"
log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }
ping_once() {
  local code took
  took=$(date +%s)
  code=$(curl -sS -H 'X-Keep-Warm: phone' --max-time 45 -o "$TMPDIR/keep-warm.json" -w '%{http_code}' "$URL" 2>/dev/null) || code="000"
  took=$(( $(date +%s) - took ))
  log "HTTP $code  ${took}s  $(tr -d '\n' < "$TMPDIR/keep-warm.json" 2>/dev/null | cut -c1-80)"
  [ "$code" = "200" ]
}
if ping_once; then exit 0; fi
sleep 15
ping_once
exit $?
PINGER_EOF
chmod +x "$PINGER"

echo "== 3/5 crontab =="
CRON_LINE="*/5 * * * * $PINGER >> $CRON_LOG 2>&1"
: > "$HOME_DIR/.crontab"
crontab -l 2>/dev/null | grep -v 'keep-warm' > "$HOME_DIR/.crontab" || true
printf '%s\n' "$CRON_LINE" >> "$HOME_DIR/.crontab"
crontab "$HOME_DIR/.crontab"

echo "== 4/5 crond =="
mkdir -p "$SV_DIR/log"
ln -sf "$PREFIX/share/termux-services/svlogger" "$SV_DIR/log/run" 2>/dev/null || true
sv-enable crond 2>/dev/null || true
sv up crond 2>/dev/null || true
sleep 1
sv status crond 2>/dev/null || echo "ogohlantirish: crond holatini o'qib bo'lmadi"

echo "== 5/6 qayta yuklashda avtomatik start (Termux:Boot) =="
mkdir -p "$HOME_DIR/.termux/boot"
cat > "$HOME_DIR/.termux/boot/keep-warm" <<BOOT_EOF
#!/data/data/com.termux/files/usr/bin/sh
# Telefon qayta yuklanganda: CPU uyg'oq ushlanadi va crond ko'tariladi.
termux-wake-lock 2>/dev/null || true
sv-enable crond 2>/dev/null || true
sv up crond 2>/dev/null || true
BOOT_EOF
chmod +x "$HOME_DIR/.termux/boot/keep-warm"

# CPU uyg'oq ushlasin (Android doze Termux'ni o'ldirmasin)
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock 2>/dev/null || true

echo "== 6/6 sinov ping =="
if "$PINGER"; then echo "OK: ping muvaffaqiyatli"; else echo "ogohlantirish: ping 200 qaytarmadi"; fi
echo
echo "crontab:"; crontab -l
echo
echo "Tayyor. Keyingi pinglar har 5 daqiqada → $LOG"
echo "  Holat:     tail -n 5 $LOG"
echo "  Cron log:  tail -n 5 $CRON_LOG"
echo
echo "MUHIM (aks holda Android Termux'ni o'chiradi):"
echo "  • Sozlamalar → Ilovalar → Termux → Batareya → \"Cheklovsiz\""
echo "  • Termux'da bir marta: termux-wake-lock"
echo "  • Qayta yuklashda avtomatik start: Termux:Boot + ~/.termux/boot/keep-warm"
