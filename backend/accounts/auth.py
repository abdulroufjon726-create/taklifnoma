"""So'rovdan foydalanuvchini aniqlash (Bearer yoki X-Auth-Token)."""

from .models import AuthToken


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
    return token.user if token else None
