import json
import logging
import os
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth.models import User
from django.core import signing
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .auth import user_from_request
from .models import AuthToken

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


def _base(origin: str | None) -> str:
    """Qaytish manzili: FRONTEND_URL berilgan bo'lsa — o'sha, aks holda
    brauzer yuborgan origin (state ichida imzolangan holda saqlanadi)."""
    configured = os.environ.get("FRONTEND_URL", "").strip()
    if configured:
        return configured.rstrip("/")
    if isinstance(origin, str) and origin.startswith(("http://", "https://")):
        return origin.rstrip("/")
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


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_config(request):
    """Frontend Google tugmasini ko'rsatishi uchun: sozlanganmi?"""
    return Response({"google": bool(getattr(settings, "GOOGLE_CLIENT_ID", ""))})
