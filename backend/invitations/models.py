import secrets

from django.contrib.auth.models import User
from django.db import models

# Unambiguous alphabet: no 0/O and 1/I — easy to read aloud / retype.
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 8


def generate_edit_key() -> str:
    """Tahrirlash kaliti — kodni bilgan mehmon taklifnomani o'zgartira olmasin."""
    return secrets.token_urlsafe(24)


def generate_code() -> str:
    """Generate a unique, human-friendly invitation code."""
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        if not Invitation.objects.filter(code=code).exists():
            return code


class Invitation(models.Model):
    """
    A single invitation. The `code` is the only way to reach it —
    there is no public listing, so nobody can browse other people's
    invitations (privacy requirement).
    """

    EVENT_TYPES = [
        ("toy", "To'y"),
        ("niqob", "Niqob to'yi"),
        ("tugilgan_kun", "Tug'ilgan kun"),
        ("suvruq", "Suvruq"),
        ("bayram", "Bayram"),
        ("korxona", "Korxona ochilishi"),
        ("boshqa", "Boshqa"),
    ]

    code = models.CharField(max_length=8, unique=True, editable=False, db_index=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default="toy")
    # Bayram / tadbir kategoriyasi (to'y, o'qituvchilar kuni, ramazon, ...)
    # Free-form slug so future categories never break stored data.
    category = models.CharField(max_length=30, blank=True, default="")

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80, blank=True)
    from_name = models.CharField(max_length=120, default="Bizdan")
    to_name = models.CharField(max_length=120, default="Barcha yaqinlarimizga")

    event_at = models.DateTimeField()
    place = models.CharField(max_length=200, blank=True, default="")
    # Xaritada belgilangan nuqta (ixtiyoriy). Bo'sh bo'lsa faqat matn ko'rsatiladi.
    place_lat = models.FloatField(null=True, blank=True)
    place_lng = models.FloatField(null=True, blank=True)

    theme = models.CharField(max_length=30, default="gold")
    ambient_effects = models.JSONField(default=list, blank=True)
    particle_effects = models.JSONField(default=list, blank=True)
    text_anim = models.CharField(max_length=30, default="fadeUp")
    card_anim = models.CharField(max_length=30, default="scaleIn")

    texts = models.JSONField(default=list, blank=True)  # selected default + custom texts
    # Har bir matn uchun shrift: {"salute": id, "names": id, "from": id, "texts": [id, ...]}
    fonts = models.JSONField(default=dict, blank=True)

    # Taklifnoma egasi (Google bilan kirgan foydalanuvchi). Eski taklifnomalarda
    # bo'sh bo'ladi — ular faqat edit_key orqali tahrirlanadi.
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="invitations",
        null=True,
        blank=True,
    )

    # Faqat yaratuvchida saqlanadi; taklifnomani tahrirlash uchun talab qilinadi
    edit_key = models.CharField(max_length=43, unique=True, default=generate_edit_key, editable=False)

    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.code} — {self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code()
        super().save(*args, **kwargs)
