"""Google hisobiga parol o'rnatish endpointining testlari."""

from django.contrib.auth.models import User
from django.test import TestCase

from .models import AuthToken


class SetPasswordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="g@test.uz", email="g@test.uz", password="unused-1234")
        self.user.set_unusable_password()
        self.user.save(update_fields=["password"])
        self.token = AuthToken.issue(self.user)

    def post(self, payload, token=True):
        headers = {}
        if token:
            headers["HTTP_AUTHORIZATION"] = f"Bearer {self.token.key}"
        return self.client.post(
            "/api/auth/password/",
            data=payload,
            content_type="application/json",
            **headers,
        )

    def test_requires_login(self):
        res = self.post({"password": "parol12345"}, token=False)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()["code"], "unauthorized")

    def test_rejects_short_password(self):
        res = self.post({"password": "123"})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], "weak_password")
        self.user.refresh_from_db()
        self.assertFalse(self.user.has_usable_password())

    def test_sets_password_and_reports_it(self):
        res = self.post({"password": "parol12345"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["has_password"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("parol12345"))

    def test_email_login_works_after_setting_password(self):
        self.post({"password": "parol12345"})
        res = self.client.post(
            "/api/auth/login/",
            data={"email": "g@test.uz", "password": "parol12345"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["token"])
