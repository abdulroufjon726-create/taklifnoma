"""Health-check testlari: Postgres bo'lmasa 503, jimgina SQLite'ga o'tish yo'q."""

from unittest import mock

from django.test import TestCase, override_settings


class HealthTests(TestCase):
    def test_health_ok_on_local_sqlite(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["database"], "ok")
        self.assertEqual(body["engine"], "sqlite3")
        self.assertEqual(body["expected"], "sqlite")
        self.assertNotIn("fallback", body)

    @override_settings(
        POSTGRES_DB_CONFIG={"ENGINE": "django.db.backends.postgresql", "NAME": "x"}
    )
    def test_health_fails_when_postgres_configured_but_unused(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 503)
        body = res.json()
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["database"], "down")
        self.assertEqual(body["expected"], "postgresql")
        self.assertIn("error", body)

    def test_health_fails_when_database_query_breaks(self):
        with mock.patch("invitations.views.connection.cursor", side_effect=RuntimeError("baza yopiq")):
            res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 503)
        body = res.json()
        self.assertEqual(body["database"], "down")
        self.assertIn("baza yopiq", body["error"])
