"""PATCH/DELETE huquqlari: begona hisob 403, egasi va edit_key ishlaydi."""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from accounts.models import AuthToken

from .models import Invitation


class InvitationPermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@test.uz", "owner@test.uz", "x")
        self.stranger = User.objects.create_user("stranger@test.uz", "stranger@test.uz", "x")
        self.invitation = Invitation.objects.create(
            first_name="Aziz",
            to_name="Mehmonlar",
            from_name="Bizdan",
            event_at=timezone.now() + datetime.timedelta(days=5),
            owner=self.owner,
        )
        self.url = f"/api/invitations/{self.invitation.code}/"
        self.owner_token = AuthToken.issue(self.owner).key
        self.stranger_token = AuthToken.issue(self.stranger).key

    def patch(self, payload, token="", edit_key=""):
        headers = {}
        if token:
            headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        if edit_key:
            headers["HTTP_X_EDIT_KEY"] = edit_key
        return self.client.patch(
            self.url, data=payload, content_type="application/json", **headers
        )

    def test_stranger_patch_is_forbidden_and_changes_nothing(self):
        res = self.patch({"first_name": "Buzildi"}, token=self.stranger_token)
        self.assertEqual(res.status_code, 403)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.first_name, "Aziz")

    def test_stranger_delete_is_forbidden_and_keeps_invitation(self):
        res = self.client.delete(self.url, HTTP_AUTHORIZATION=f"Bearer {self.stranger_token}")
        self.assertEqual(res.status_code, 403)
        self.assertTrue(Invitation.objects.filter(pk=self.invitation.pk).exists())

    def test_anonymous_patch_and_delete_are_forbidden(self):
        self.assertEqual(self.patch({"first_name": "Buzildi"}).status_code, 403)
        self.assertEqual(self.client.delete(self.url).status_code, 403)

    def test_wrong_edit_key_is_forbidden(self):
        res = self.patch({"first_name": "Buzildi"}, edit_key="not-the-key")
        self.assertEqual(res.status_code, 403)

    def test_owner_can_patch(self):
        res = self.patch({"first_name": "Yangi"}, token=self.owner_token)
        self.assertEqual(res.status_code, 200)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.first_name, "Yangi")
        self.assertEqual(res.json()["code"], self.invitation.code)

    def test_correct_edit_key_works_without_login(self):
        res = self.patch({"first_name": "Kalit"}, edit_key=self.invitation.edit_key)
        self.assertEqual(res.status_code, 200)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.first_name, "Kalit")

    def test_owner_can_delete(self):
        res = self.client.delete(self.url, HTTP_AUTHORIZATION=f"Bearer {self.owner_token}")
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Invitation.objects.filter(pk=self.invitation.pk).exists())
