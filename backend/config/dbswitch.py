"""
Postgres tiklansa — SQLite fallback'dan avtomatik qaytish.

Ishga tushishda Postgres yetib bo'lmasa (Tailscale tunnel yopiq, baza o'chgan),
settings.py SQLite'ga o'tadi. Baza keyin qaytsa, servisni qayta ishga tushirmasdan
ham Postgres'ga qaytish kerak — buni shu middleware 30 soniyada bir marta
tekshiradi. Migratsiya muvaffaqiyatsiz bo'lsa, SQLite'da qolamiz.
"""

import logging
import time

from django.conf import settings
from django.db import connections

logger = logging.getLogger(__name__)

RETRY_EVERY_SECONDS = 30.0
_last_try = 0.0


def _reset_default_connection() -> None:
    """Joriy thread'dagi ulanishlarni yopib, konfiguratsiya keshini tozalaydi."""
    try:
        connections.close_all()
    except Exception:
        logger.exception("Closing database connections failed")
    try:
        del connections["default"]
    except Exception:
        pass
    if "settings" in connections.__dict__:
        del connections.__dict__["settings"]


def postgres_ready(timeout: int = 5) -> bool:
    cfg = getattr(settings, "POSTGRES_DB_CONFIG", None)
    if not cfg:
        return False
    try:
        import psycopg
    except Exception as exc:
        logger.warning("psycopg mavjud emas: %s", exc)
        return False
    options = cfg.get("OPTIONS") or {}
    try:
        conn = psycopg.connect(
            host=cfg.get("HOST") or "",
            port=cfg.get("PORT") or "5432",
            dbname=cfg.get("NAME") or "",
            user=cfg.get("USER") or "",
            password=cfg.get("PASSWORD") or "",
            connect_timeout=max(1, int(timeout)),
            sslmode=options.get("sslmode", "prefer"),
        )
        conn.close()
        return True
    except Exception as exc:
        logger.info("Postgres hali javob bermayapti: %s", str(exc).replace("\n", " ")[:200])
        return False


def switch_to_postgres() -> bool:
    """Postgres'ga o'tadi; migratsiya yiqilsa SQLite'da qoladi."""
    from django.core.management import call_command

    cfg = getattr(settings, "POSTGRES_DB_CONFIG", None)
    sqlite_cfg = getattr(settings, "SQLITE_DB_CONFIG", None)
    if not cfg or not sqlite_cfg:
        return False

    _reset_default_connection()
    settings.DATABASES["default"] = cfg
    try:
        call_command("migrate", interactive=False, verbosity=0)
    except Exception:
        logger.exception("Postgres'da migratsiya bajarilmadi - SQLite'da qolamiz")
        _reset_default_connection()
        settings.DATABASES["default"] = sqlite_cfg
        return False

    settings.DB_FALLBACK_REASON = ""
    logger.warning("Postgres qaytdi - SQLite fallback'dan Postgres'ga o'tildi")
    return True


def maybe_recover(force: bool = False) -> bool:
    """Fallback holatida bo'lsak, Postgres'ni qayta tekshiradi (throttle bilan)."""
    global _last_try

    if not getattr(settings, "DB_FALLBACK_REASON", ""):
        return False

    now = time.monotonic()
    if not force and now - _last_try < RETRY_EVERY_SECONDS:
        return False
    _last_try = now

    if not postgres_ready():
        return False
    return switch_to_postgres()


class PostgresRecoveryMiddleware:
    """Har so'rovda (30 soniyada bir marta) bazani qayta ulashga urinadi."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            maybe_recover()
        except Exception:
            logger.exception("Bazani qayta ulash tekshiruvi yiqildi")
        return self.get_response(request)
