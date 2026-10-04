from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .models import Invitation
from .serializers import InvitationCreateSerializer, InvitationSerializer


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

    Invitation.objects.filter(pk=invitation.pk).update(views=invitation.views + 1)
    invitation.views += 1
    return Response(InvitationSerializer(invitation).data)
