"""Google bilan kirish oqimining testlari.

Google'ning haqiqiy serverlariga murojaat qilinmaydi: token va userinfo
javoblari mock qilinadi. Shu tufayli kalitlar hali qo'yilmagan bo'lsa ham
oqim to'g'ri ishlashini tekshirish mumkin.
"""

import json
import urllib.parse
from unittest import mock

from django.contrib.auth.models import User
from django.core import signing
from django.test import TestCase, override_settings

from .models import AuthToken
from .views import STATE_SALT, _allowed_origin


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, *args):
        return json.dumps(self.payload).encode()

    def close(self):
        pass


def fake_urlopen(request, timeout=None):
    url = request.full_url if hasattr(request, "full_url") else str(request)
    if "oauth2.googleapis.com/token" in url:
        return FakeResponse({"access_token": "ya29.fake-token"})
    return FakeResponse(
        {
            "email": "goog@test.uz",
            "email_verified": True,
            "given_name": "Goog",
            "family_name": "User",
        }
    )


@override_settings(GOOGLE_CLIENT_ID="client-123.apps.googleusercontent.com", GOOGLE_CLIENT_SECRET="secret")
class GoogleStartTests(TestCase):
    def test_start_sends_user_to_google_with_configured_client(self):
        res = self.client.get(
            "/api/auth/google/start/",
            {"next": "/envelopes", "origin": "http://localhost:5173"},
        )
        self.assertEqual(res.status_code, 302)
        location = res["Location"]
        self.assertTrue(location.startswith("https://accounts.google.com/o/oauth2/v2/auth?"))
        params = urllib.parse.parse_qs(urllib.parse.urlparse(location).query)
        self.assertEqual(params["client_id"], ["client-123.apps.googleusercontent.com"])
        self.assertIn("/api/auth/google/callback/", params["redirect_uri"][0])
        self.assertIn("state", params)
        self.assertEqual(params["scope"], ["openid email profile"])

    def test_next_cannot_leave_the_site(self):
        res = self.client.get(
            "/api/auth/google/start/",
            {"next": "https://evil.example/steal", "origin": "http://localhost:5173"},
        )
        state = urllib.parse.parse_qs(urllib.parse.urlparse(res["Location"]).query)["state"][0]
        self.assertEqual(signing.loads(state, salt=STATE_SALT)["next"], "/create")

    @override_settings(GOOGLE_CLIENT_ID="", GOOGLE_CLIENT_SECRET="")
    def test_start_without_keys_returns_to_frontend_with_error(self):
        res = self.client.get(
            "/api/auth/google/start/",
            {"next": "/create", "origin": "http://localhost:5173"},
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], "http://localhost:5173/?auth_error=google_not_configured")


class OriginWhitelistTests(TestCase):
    def test_only_known_frontends_are_accepted(self):
        self.assertEqual(_allowed_origin("http://localhost:5173"), "http://localhost:5173")
        self.assertEqual(_allowed_origin("http://127.0.0.1:5173"), "http://127.0.0.1:5173")
        self.assertEqual(
            _allowed_origin("https://taklifnoma-007.vercel.app"),
            "https://taklifnoma-007.vercel.app",
        )

    def test_foreign_and_malformed_origins_are_rejected(self):
        for origin in (
            "https://evil.example",
            "https://taklifnoma-007.vercel.app.evil.example",
            "javascript:alert(1)",
            "/relative",
            "",
            None,
        ):
            self.assertEqual(_allowed_origin(origin), "", origin)


@override_settings(GOOGLE_CLIENT_ID="client-123.apps.googleusercontent.com", GOOGLE_CLIENT_SECRET="secret")
class GoogleCallbackTests(TestCase):
    def _state(self, next_path="/envelopes", base="http://localhost:5173"):
        return signing.dumps({"next": next_path, "base": base}, salt=STATE_SALT)

    def test_callback_creates_user_and_issues_token(self):
        with mock.patch("accounts.views.urllib.request.urlopen", side_effect=fake_urlopen):
            res = self.client.get(
                "/api/auth/google/callback/",
                {"code": "auth-code", "state": self._state()},
            )

        self.assertEqual(res.status_code, 302)
        location = res["Location"]
        self.assertTrue(location.startswith("http://localhost:5173/auth?"), location)
        params = urllib.parse.parse_qs(urllib.parse.urlparse(location).query)
        self.assertEqual(params["next"], ["/envelopes"])

        user = User.objects.get(username="goog@test.uz")
        self.assertFalse(user.has_usable_password())
        token = AuthToken.objects.get(key=params["token"][0])
        self.assertEqual(token.user_id, user.id)

    def test_callback_links_existing_email_account(self):
        existing = User.objects.create_user(
            username="goog@test.uz", email="goog@test.uz", password="parol12345"
        )
        with mock.patch("accounts.views.urllib.request.urlopen", side_effect=fake_urlopen):
            res = self.client.get(
                "/api/auth/google/callback/",
                {"code": "auth-code", "state": self._state()},
            )

        self.assertEqual(res.status_code, 302)
        self.assertEqual(User.objects.filter(username="goog@test.uz").count(), 1)
        existing.refresh_from_db()
        # Email/parol bilan kirish yo'qolmaydi
        self.assertTrue(existing.has_usable_password())

    def test_callback_rejects_unverified_email(self):
        def unverified(request, timeout=None):
            url = request.full_url if hasattr(request, "full_url") else str(request)
            if "oauth2.googleapis.com/token" in url:
                return FakeResponse({"access_token": "ya29.fake-token"})
            return FakeResponse({"email": "goog@test.uz", "email_verified": False})

        with mock.patch("accounts.views.urllib.request.urlopen", side_effect=unverified):
            res = self.client.get(
                "/api/auth/google/callback/",
                {"code": "auth-code", "state": self._state()},
            )

        self.assertEqual(res.status_code, 302)
        self.assertIn("auth_error=google_email", res["Location"])
        self.assertFalse(User.objects.filter(username="goog@test.uz").exists())

    def test_callback_without_keys_does_not_create_anything(self):
        with override_settings(GOOGLE_CLIENT_ID="", GOOGLE_CLIENT_SECRET=""):
            res = self.client.get(
                "/api/auth/google/callback/",
                {"code": "auth-code", "state": self._state()},
            )
        self.assertEqual(res.status_code, 302)
        self.assertIn("auth_error=google_not_configured", res["Location"])
        self.assertEqual(User.objects.count(), 0)
