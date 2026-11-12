import json
import logging
import os
import re
import urllib.parse
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import signing
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .auth import user_from_request
from .models import AuthToken, LoginAttempt

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
STATE_SALT = "taklifnoma-oauth"


def _redirect_uri(request: str) -> str:
    configured = getattr(settings, "GOOGLE_REDIRECT_URI", "")
    if configured:
        return configured
    return request.build_absolute_uri(reverse("google-callback"))


# Google'dan keyin qaytishga ruxsat berilgan frontend domenlari.
# Ro'yxatga kirmagan origin (masalan hujumchining sayti) qabul qilinmaydi,
# aks holda kirish tokeni begona domenga yuborilib qolishi mumkin edi.
KNOWN_FRONTEND_HOSTS = {"taklifnoma-007.vercel.app"}
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "[::1]"}


def _allowed_origin(origin: str | None) -> str:
    """Origin'ni tekshiradi: faqat ma'lum frontend domenlari o'tadi."""
    if not isinstance(origin, str) or not origin:
        return ""
    parsed = urllib.parse.urlparse(origin)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in ("http", "https") or not host:
        return ""
    allowed = set(KNOWN_FRONTEND_HOSTS) | LOOPBACK_HOSTS
    for candidate in (
        list(getattr(settings, "CORS_ALLOWED_ORIGINS", []))
        + list(getattr(settings, "CSRF_TRUSTED_ORIGINS", []))
        + [getattr(settings, "FRONTEND_URL", "")]
    ):
        candidate_host = urllib.parse.urlparse(candidate or "").hostname
        if candidate_host:
            allowed.add(candidate_host.lower())
    if host not in allowed:
        logger.warning("Google OAuth: ruxsatsiz origin rad etildi: %s", origin)
        return ""
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _base(origin: str | None) -> str:
    """Qaytish manzili: FRONTEND_URL berilgan bo'lsa — o'sha, aks holda
    brauzer yuborgan (tekshirilgan) origin. state ichida imzolanadi."""
    configured = os.environ.get("FRONTEND_URL", "").strip()
    if configured:
        return configured.rstrip("/")
    checked = _allowed_origin(origin)
    if checked:
        return checked
    return (getattr(settings, "FRONTEND_URL", "") or "").rstrip("/")


def _frontend(path: str, base: str | None = None, **params) -> str:
    base = (base or _base(None)).rstrip("/")
    url = f"{base}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v})
    return url


def _safe_next(value) -> str:
    if isinstance(value, str) and value.startswith("/") and not value.startswith("//"):
        return value
    return "/create"


def _user_payload(user) -> dict:
    full = f"{user.first_name} {user.last_name}".strip()
    return {
        "id": user.id,
        "email": user.email,
        "name": full or user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "invitations": user.invitations.count(),
        "has_password": user.has_usable_password(),
    }


@api_view(["GET"])
@permission_classes([AllowAny])
def google_start(request):
    """Google rozilik sahifasiga yo'naltiradi."""
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    nxt = _safe_next(request.GET.get("next"))
    base = _base(request.GET.get("origin"))
    if not client_id:
        return HttpResponseRedirect(
            _frontend("/", base=base, auth_error="google_not_configured")
        )

    state = signing.dumps({"next": nxt, "base": base}, salt=STATE_SALT)
    params = {
        "client_id": client_id,
        "redirect_uri": _redirect_uri(request),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
        "access_type": "online",
    }
    return HttpResponseRedirect(f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}")


@api_view(["GET"])
@permission_classes([AllowAny])
def google_callback(request):
    """Google qaytargan kodni tokenga almashtiradi va frontendga qaytaradi."""
    if request.GET.get("error"):
        return HttpResponseRedirect(_frontend("/", auth_error=request.GET.get("error")))

    code = request.GET.get("code")
    try:
        state = signing.loads(request.GET.get("state", ""), salt=STATE_SALT, max_age=900)
    except Exception:
        state = {}
    nxt = _safe_next(state.get("next"))
    base = state.get("base") or _base(None)

    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
    if not code or not client_id or not client_secret:
        return HttpResponseRedirect(
            _frontend("/", base=base, auth_error="google_not_configured")
        )

    body = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": _redirect_uri(request),
            "grant_type": "authorization_code",
        }
    ).encode()
    try:
        token_req = urllib.request.Request(
            GOOGLE_TOKEN_URL,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(token_req, timeout=20) as resp:
            tokens = json.load(resp)
        access = tokens.get("access_token")
        if not access:
            raise ValueError("access_token yo'q")
        info_req = urllib.request.Request(
            GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access}"}
        )
        with urllib.request.urlopen(info_req, timeout=20) as resp:
            info = json.load(resp)
    except Exception:
        logger.exception("Google OAuth almashinuvi muvaffaqiyatsiz")
        return HttpResponseRedirect(_frontend("/", base=base, auth_error="google_failed"))

    email = (info.get("email") or "").strip().lower()
    if not email or info.get("email_verified") is False:
        return HttpResponseRedirect(_frontend("/", base=base, auth_error="google_email"))

    user, created = User.objects.get_or_create(username=email, defaults={"email": email})
    if created:
        user.set_unusable_password()
    user.email = email
    user.first_name = (info.get("given_name") or info.get("name") or "")[:150]
    user.last_name = (info.get("family_name") or "")[:150]
    user.is_active = True
    user.save()

    token = AuthToken.issue(user)
    return HttpResponseRedirect(
        _frontend("/auth", base=base, token=token.key, next=nxt)
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def me(request):
    user = user_from_request(request)
    if not user:
        return Response({"detail": "Kirish talab qilinadi."}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(_user_payload(user))


@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request):
    key = (request.headers.get("Authorization") or "").replace("Bearer ", "").strip()
    if not key:
        key = (request.headers.get("X-Auth-Token") or "").strip()
    if key:
        AuthToken.objects.filter(key=key).delete()
    return Response({"ok": True})


@api_view(["POST"])
@permission_classes([AllowAny])
def set_password(request):
    """Google bilan kirgan (paroli yo'q) foydalanuvchi parol o'rnatadi."""
    user = user_from_request(request)
    if not user:
        return Response(
            {"code": "unauthorized", "detail": "Kirish talab qilinadi."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    password = str(request.data.get("password", ""))
    if len(password) < 8:
        return Response(
            {"code": "weak_password", "detail": "Parol kamida 8 belgidan iborat bo'lsin."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user.set_password(password)
    user.save(update_fields=["password"])
    return Response(_user_payload(user))


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_config(request):
    """Frontend Google tugmasi uchun: sozlanganmi va qaysi redirect URI?"""
    google = bool(getattr(settings, "GOOGLE_CLIENT_ID", ""))
    body = {"google": google}
    if google:
        body["redirect_uri"] = _redirect_uri(request)
    else:
        # Sozlashda aynan shu manzil Google Console'ga yoziladi
        body["redirect_uri"] = _redirect_uri(request)
    return Response(body)


# ---- Email + parol bilan kirish -----------------------------------------
# Google kalitlari sozlanmagan bo'lsa ham sayt to'liq ishlashi uchun.
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Parol urinishlarini cheklash: 15 daqiqada 5 marta xato -> 429
LOGIN_WINDOW = timedelta(minutes=15)
LOGIN_MAX_FAILURES = 5
ATTEMPT_RETENTION = timedelta(days=2)


def _client_ip(request):
    forwarded = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()[:45] or None
    return (request.META.get("REMOTE_ADDR") or "").strip()[:45] or None


def _too_many_failures(identifier: str, ip: str | None) -> bool:
    since = timezone.now() - LOGIN_WINDOW
    fails = LoginAttempt.objects.filter(
        identifier=identifier, ok=False, created_at__gte=since
    )
    if ip:
        fails = fails.filter(Q(ip=ip) | Q(ip__isnull=True))
    return fails.count() >= LOGIN_MAX_FAILURES


def _prune_attempts():
    LoginAttempt.objects.filter(created_at__lt=timezone.now() - ATTEMPT_RETENTION).delete()


def _auth_payload(user):
    token = AuthToken.issue(user)
    return {"token": token.key, "user": _user_payload(user)}


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    email = str(request.data.get("email", "")).strip().lower()
    password = str(request.data.get("password", ""))
    name = str(request.data.get("name", "")).strip()[:150]

    if not EMAIL_RE.match(email):
        return Response(
            {"code": "invalid_email", "detail": "Email manzil noto'g'ri."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(password) < 8:
        return Response(
            {"code": "weak_password", "detail": "Parol kamida 8 belgidan iborat bo'lsin."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if User.objects.filter(username=email).exists():
        return Response(
            {"code": "email_taken", "detail": "Bu email allaqachon ro'yxatdan o'tgan."},
            status=status.HTTP_409_CONFLICT,
        )

    parts = name.split(" ", 1)
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=parts[0][:150],
        last_name=(parts[1] if len(parts) > 1 else "")[:150],
    )
    AuthToken.purge_expired()
    return Response(_auth_payload(user), status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_login(request):
    email = str(request.data.get("email", "")).strip().lower()
    password = str(request.data.get("password", ""))
    ip = _client_ip(request)

    if _too_many_failures(email, ip):
        return Response(
            {
                "code": "too_many_attempts",
                "detail": "Juda ko'p urinish. 15 daqiqadan keyin qayta urinib ko'ring.",
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    user = authenticate(request, username=email, password=password)
    if not user or not user.is_active:
        LoginAttempt.objects.create(identifier=email, ip=ip, ok=False)
        _prune_attempts()
        return Response(
            {"code": "bad_credentials", "detail": "Email yoki parol noto'g'ri."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Muvaffaqiyatli kirish — shu hisobning xato urinishlari tozalanadi
    LoginAttempt.objects.filter(identifier=email, ok=False).delete()
    AuthToken.purge_expired()
    return Response(_auth_payload(user))
