import logging
import secrets

from django.conf import settings
from django.db import connection
from django.db.models import F
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from accounts.auth import user_from_request

from .models import Invitation
from .serializers import InvitationCreateSerializer, InvitationSerializer

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Health-check: servis va baza tirikmi (Render health probe).

    Postgres sozlangan bo'lsa — faqat Postgres hisobga olinadi: u ishlamasa
    503 qaytadi (SQLite'ga jimgina o'tish yo'q), shuning uchun muammo deployda
    darhol ko'rinadi.
    """
    engine = str(settings.DATABASES["default"].get("ENGINE", "")).rsplit(".", 1)[-1]
    expects_postgres = bool(getattr(settings, "POSTGRES_DB_CONFIG", None))
    body = {
        "status": "ok",
        "database": "ok",
        "engine": engine,
        "expected": "postgresql" if expects_postgres else "sqlite",
    }
    migration_error = getattr(settings, "MIGRATION_ERROR", "")
    if migration_error:
        body["migration_error"] = migration_error

    if expects_postgres and engine != "postgresql":
        body.update(
            status="error",
            database="down",
            error="Postgres sozlangan, lekin ulanish ishlatilmayapti.",
        )
        return Response(body, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:
        logger.exception("Health check failed")
        body.update(
            status="error",
            database="down",
            error=" ".join(str(exc).split())[:300],
        )
        return Response(body, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(body)


@api_view(["POST"])
@permission_classes([AllowAny])
def invitation_create(request):
    """
    Create a new invitation and return its unique code.
    NOTE: there is intentionally no GET list endpoint — invitations are
    reachable only via their exact code (privacy requirement).
    """
    user = user_from_request(request)
    if not user:
        return Response(
            {"detail": "Taklifnoma yaratish uchun Google bilan kiring."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    serializer = InvitationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    invitation = serializer.save(owner=user)
    data = dict(InvitationSerializer(invitation).data)
    # Tahrirlash kaliti faqat yaratuvchiga qaytariladi (GET'da hech qachon)
    data["edit_key"] = invitation.edit_key
    return Response(data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def invitation_detail(request, code):
    """Kod bo'yicha taklifnoma. PATCH/DELETE — egasi yoki edit_key bilan."""
    normalized = "".join(ch for ch in code.upper() if ch.isalnum())
    if len(normalized) != 8:
        raise NotFound("Bunday kodli taklifnoma topilmadi.")
    try:
        invitation = Invitation.objects.get(code=normalized)
    except Invitation.DoesNotExist:
        raise NotFound("Bunday kodli taklifnoma topilmadi.")

    if request.method in ("PATCH", "DELETE"):
        user = user_from_request(request)
        is_owner = bool(user and invitation.owner_id == user.id)
        if not is_owner:
            key = request.headers.get("X-Edit-Key", "")
            if not key or not secrets.compare_digest(key, invitation.edit_key):
                return Response(
                    {"detail": "Bu taklifnomani o'zgartirish huquqi yo'q."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if request.method == "DELETE":
            invitation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = InvitationCreateSerializer(invitation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(InvitationSerializer(invitation).data)

    # Atomar oshirish: bir vaqtda ochgan mehmonlar hisobni yo'qotmaydi.
    Invitation.objects.filter(pk=invitation.pk).update(views=F("views") + 1)
    invitation.views += 1
    return Response(InvitationSerializer(invitation).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def invitation_mine(request):
    """Kirgan foydalanuvchining barcha taklifnomalari (yangi → eski)."""
    user = user_from_request(request)
    if not user:
        return Response(
            {"detail": "Kirish talab qilinadi."}, status=status.HTTP_401_UNAUTHORIZED
        )
    items = (
        Invitation.objects.filter(owner=user)
        .only(
            "code",
            "event_type",
            "category",
            "first_name",
            "last_name",
            "from_name",
            "to_name",
            "event_at",
            "place",
            "theme",
            "ambient_effects",
            "particle_effects",
            "text_anim",
            "card_anim",
            "texts",
            "fonts",
            "views",
            "created_at",
        )[:200]
    )
    data = InvitationSerializer(items, many=True).data
    return Response({"count": len(data), "results": data})


@api_view(["POST"])
@permission_classes([AllowAny])
def invitation_claim(request, code):
    """Login'dan oldin yaratilgan (egasiz) taklifnomani hisobga bog'lash.

    Faqat o'sha qurilmada saqlangan edit_key bilan — begona odam boshqa
    taklifnomani o'z hisobiga tortib ola olmaydi.
    """
    user = user_from_request(request)
    if not user:
        return Response({"detail": "Kirish talab qilinadi."}, status=status.HTTP_401_UNAUTHORIZED)

    normalized = "".join(ch for ch in code.upper() if ch.isalnum())
    if len(normalized) != 8:
        raise NotFound("Bunday kodli taklifnoma topilmadi.")
    try:
        invitation = Invitation.objects.get(code=normalized)
    except Invitation.DoesNotExist:
        raise NotFound("Bunday kodli taklifnoma topilmadi.")

    if invitation.owner_id == user.id:
        return Response(InvitationSerializer(invitation).data)
    if invitation.owner_id:
        return Response(
            {"detail": "Bu taklifnoma boshqa hisobga bog'langan."},
            status=status.HTTP_409_CONFLICT,
        )

    key = request.headers.get("X-Edit-Key", "")
    if not key or not secrets.compare_digest(key, invitation.edit_key):
        return Response(
            {"detail": "Tahrirlash kaliti noto'g'ri."},
            status=status.HTTP_403_FORBIDDEN,
        )

    invitation.owner = user
    invitation.save(update_fields=["owner"])
    return Response(InvitationSerializer(invitation).data)
