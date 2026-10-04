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
            "views",
            "created_at",
        ]
