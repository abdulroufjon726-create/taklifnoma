import secrets

from django.contrib.auth.models import User
from django.db import models


def generate_token() -> str:
    return secrets.token_urlsafe(32)


class AuthToken(models.Model):
    """Google orqali kirgan foydalanuvchi uchun uzoq muddatli API kaliti.

    Brauzer tokenni localStorage'da saqlaydi va har so'rovda
    `Authorization: Bearer <key>` sarlavhasi bilan yuboradi.
    """

    key = models.CharField(max_length=64, unique=True, default=generate_token, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_tokens")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.key[:6]}…"

    @classmethod
    def issue(cls, user):
        return cls.objects.create(user=user)
