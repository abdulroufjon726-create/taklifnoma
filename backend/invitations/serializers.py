from rest_framework import serializers

from .models import Invitation


class InvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
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
        ]

    def validate_first_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Ismni kiriting.")
        return value

    def validate_event_at(self, value):
        if value is None:
            raise serializers.ValidationError("Tadbir vaqtini kiriting.")
        return value

    def validate_category(self, value):
        value = (value or "").strip()
        if len(value) > 30:
            raise serializers.ValidationError("Kategoriya nomi juda uzun.")
        return value

    def validate_texts(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Matnlar ro'yxat bo'lishi kerak.")
        cleaned = []
        for item in value[:20]:
            if not isinstance(item, str):
                continue
            item = item.strip()
            if item:
                cleaned.append(item[:300])
        return cleaned

    def validate_fonts(self, value):
        """Har bir matn uchun shrift tanlovi: {"salute", "names", "from", "texts"}."""
        if value in (None, ""):
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Shriftlar obyekt bo'lishi kerak.")
        allowed = {"cormorant", "playfair", "lora", "montserrat", "vibes"}

        def clean(font_id):
            return font_id if isinstance(font_id, str) and font_id in allowed else ""

        texts = value.get("texts") or []
        if not isinstance(texts, list):
            texts = []
        return {
            "salute": clean(value.get("salute")),
            "names": clean(value.get("names")),
            "from": clean(value.get("from")),
            "texts": [clean(t) for t in texts[:20]],
        }

    def validate(self, attrs):
        for key in ("ambient_effects", "particle_effects"):
            value = attrs.get(key) or []
            if not isinstance(value, list) or len(value) > 12:
                raise serializers.ValidationError({key: "Noto'g'ri effektlar ro'yxati."})
        return attrs


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
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
        ]
