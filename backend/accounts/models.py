import secrets
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Token 60 kundan keyin eskiradi, bitta hisobda eng ko'pi 8 ta faol token qoladi.
TOKEN_TTL_DAYS = 60
MAX_TOKENS_PER_USER = 8


def generate_token() -> str:
    return secrets.token_urlsafe(32)


class AuthToken(models.Model):
    """Kirgan foydalanuvchi uchun uzoq muddatli API kaliti.

    Brauzer tokenni localStorage'da saqlaydi va har so'rovda
    `Authorization: Bearer <key>` sarlavhasi bilan yuboradi.
    """

    key = models.CharField(max_length=64, unique=True, default=generate_token, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_tokens")
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.key[:6]}…"

    @property
    def expired(self) -> bool:
        return self.created_at < timezone.now() - timedelta(days=TOKEN_TTL_DAYS)

    @classmethod
    def issue(cls, user):
        """Yangi token beradi va shu hisobning eski tokenlarini tozalaydi."""
        now = timezone.now()
        cls.objects.filter(
            user=user, created_at__lt=now - timedelta(days=TOKEN_TTL_DAYS)
        ).delete()

        token = cls.objects.create(user=user, last_used_at=now)

        # Eng oxirgi MAX_TOKENS_PER_USER tasidan boshqasini o'chiramiz
        stale = list(
            cls.objects.filter(user=user)
            .order_by("-created_at")
            .values_list("id", flat=True)[MAX_TOKENS_PER_USER:]
        )
        if stale:
            cls.objects.filter(id__in=stale).delete()
        return token

    @classmethod
    def purge_expired(cls, days: int = TOKEN_TTL_DAYS) -> int:
        """Muddati o'tgan barcha tokenlarni o'chiradi (kunlik tozalash)."""
        cutoff = timezone.now() - timedelta(days=days)
        deleted, _ = cls.objects.filter(created_at__lt=cutoff).delete()
        return deleted


class LoginAttempt(models.Model):
    """Parol bilan kirish urinishlari — ketma-ket xatolarni cheklash uchun."""

    identifier = models.CharField(max_length=200, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    ok = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.identifier} {'ok' if self.ok else 'fail'}"
