"""So'rovdan foydalanuvchini aniqlash (Bearer yoki X-Auth-Token)."""

from datetime import timedelta

from django.utils import timezone

from .models import TOKEN_TTL_DAYS, AuthToken

TOUCH_INTERVAL = timedelta(hours=1)


def token_from_request(request) -> str:
    raw = (request.headers.get("Authorization") or "").strip()
    if raw.lower().startswith("bearer "):
        return raw[7:].strip()
    return (request.headers.get("X-Auth-Token") or "").strip()


def user_from_request(request):
    key = token_from_request(request)
    if not key:
        return None
    token = AuthToken.objects.select_related("user").filter(key=key).first()
    if not token:
        return None

    now = timezone.now()
    # Muddati o'tgan token qabul qilinmaydi va o'chiriladi
    if token.created_at < now - timedelta(days=TOKEN_TTL_DAYS):
        token.delete()
        return None

    # "Oxirgi foydalanish" vaqtini har so'rovda emas, soatiga bir marta yozamiz
    if not token.last_used_at or now - token.last_used_at > TOUCH_INTERVAL:
        AuthToken.objects.filter(pk=token.pk).update(last_used_at=now)

    return token.user
