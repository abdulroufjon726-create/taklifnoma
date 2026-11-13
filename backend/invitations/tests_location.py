"""Manzil (xarita) koordinatalari uchun testlar."""

import datetime

from django.utils import timezone
from django.test import TestCase

from .models import Invitation
from .serializers import InvitationCreateSerializer, InvitationSerializer

BASE = {
    "first_name": "Aziz",
    "to_name": "Mehmonlar",
    "from_name": "Bizdan",
    "event_at": "2027-05-01T15:00:00Z",
    "place": "Chilonzor, Toshkent",
    "theme": "gold",
    "texts": [],
    "fonts": {},
}


class InvitationLocationSerializerTests(TestCase):
    def test_coordinates_are_accepted_and_saved(self):
        serializer = InvitationCreateSerializer(
            data={**BASE, "place_lat": 41.2857, "place_lng": 69.2035}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        invitation = serializer.save()
        self.assertAlmostEqual(invitation.place_lat, 41.2857)
        self.assertAlmostEqual(invitation.place_lng, 69.2035)

    def test_coordinates_are_optional(self):
        serializer = InvitationCreateSerializer(data=BASE)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        invitation = serializer.save()
        self.assertIsNone(invitation.place_lat)
        self.assertIsNone(invitation.place_lng)

    def test_out_of_range_coordinates_are_rejected(self):
        for payload, field in (
            ({"place_lat": 120, "place_lng": 69}, "place_lat"),
            ({"place_lat": 41, "place_lng": 300}, "place_lng"),
        ):
            serializer = InvitationCreateSerializer(data={**BASE, **payload})
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    def test_public_payload_exposes_coordinates(self):
        invitation = Invitation.objects.create(
            first_name="Aziz",
            to_name="Mehmonlar",
            from_name="Bizdan",
            event_at=timezone.now() + datetime.timedelta(days=5),
            place="Chilonzor",
            place_lat=41.2,
            place_lng=69.2,
        )
        data = InvitationSerializer(invitation).data
        self.assertAlmostEqual(data["place_lat"], 41.2)
        self.assertAlmostEqual(data["place_lng"], 69.2)
        self.assertEqual(data["place"], "Chilonzor")
