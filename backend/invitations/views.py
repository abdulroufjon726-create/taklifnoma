import logging

from django.conf import settings
from django.db import connection
from django.db.models import F
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .models import Invitation
from .serializers import InvitationCreateSerializer, InvitationSerializer

logger = logging.getLogger(__name__)


def _schema_state():
    """Jadval va ustunlar joyidami — 500 sababini ko'rsatish uchun."""
    try:
        tables = set(connection.introspection.table_names())
    except Exception as exc:
        return {"error": str(exc).replace("\n", " ")[:200]}
    state = {"table": "invitations_invitation" in tables}
    if state["table"]:
        try:
            with connection.cursor() as cursor:
                desc = connection.introspection.get_table_description(cursor, "invitations_invitation")
            state["columns"] = sorted(col.name for col in desc)
        except Exception as exc:
            state["columns_error"] = str(exc).replace("\n", " ")[:200]
    return state


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Yengil health-check: servis va baza tirikmi (Render health probe)."""
    engine = str(settings.DATABASES["default"].get("ENGINE", "")).rsplit(".", 1)[-1]
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        logger.exception("Health check failed")
        return Response(
            {"status": "error", "database": "down", "engine": engine},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    body = {"status": "ok", "database": "ok", "engine": engine, "schema": _schema_state()}
    fallback = getattr(settings, "DB_FALLBACK_REASON", "")
    if fallback:
        body["fallback"] = True
        body["fallback_reason"] = fallback
    migration_error = getattr(settings, "MIGRATION_ERROR", "")
    if migration_error:
        body["migration_error"] = migration_error
    return Response(body)


@api_view(["POST"])
@permission_classes([AllowAny])
def invitation_create(request):
    """
    Create a new invitation and return its unique code.
    NOTE: there is intentionally no GET list endpoint — invitations are
    reachable only via their exact code (privacy requirement).
    """
    serializer = InvitationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    invitation = serializer.save()
    return Response(
        InvitationSerializer(invitation).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def invitation_detail(request, code):
    """Fetch one invitation by its exact code (case-insensitive, dashes ignored)."""
    normalized = "".join(ch for ch in code.upper() if ch.isalnum())
    if len(normalized) != 8:
        raise NotFound("Bunday kodli taklifnoma topilmadi.")
    try:
        invitation = Invitation.objects.get(code=normalized)
    except Invitation.DoesNotExist:
        raise NotFound("Bunday kodli taklifnoma topilmadi.")

    # Atomar oshirish: bir vaqtda ochgan mehmonlar hisobni yo'qotmaydi.
    Invitation.objects.filter(pk=invitation.pk).update(views=F("views") + 1)
    invitation.views += 1
    return Response(InvitationSerializer(invitation).data)
