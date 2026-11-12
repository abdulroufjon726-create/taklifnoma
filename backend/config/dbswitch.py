"""
Postgres tiklansa — SQLite fallback'dan avtomatik qaytish (fon taymeri).

Ishga tushishda Postgres yetib bo'lmasa, settings.py SQLite'ga o'tadi. Baza keyin
qaytsa, servisni qayta ishga tushirmasdan ham Postgres'ga qaytish kerak. Buni fon
taymeri (daemon thread) har `DJANGO_DB_RECOVERY_INTERVAL` soniyada tekshiradi.

Xavfsizlik: almashtirish paytida so'rovlar `request_scope()` bilan qulflanadi.
Taymer barcha faol so'rovlar tugashini kutadi, keyin ulanishni almashtiradi —
shundan keyin hech bir thread SQLite'ga yozib qolmaydi. Har bir thread o'zining
keshlangan ulanishini ham tekshiradi (`ensure_current_connection`), chunki
Django ulanishlari thread-local.
"""

import contextlib
import logging
import os
import threading
import time

from django.conf import settings
from django.db import connections

logger = logging.getLogger(__name__)


def _interval():
    try:
        return max(5.0, float(os.environ.get("DJANGO_DB_RECOVERY_INTERVAL", "30")))
    except ValueError:
        return 30.0


_state = threading.Condition()
_active_requests = 0
_switching = False
_started = False
_start_lock = threading.Lock()


@contextlib.contextmanager
def request_scope():
    """Baza almashtirilayotganda kutadi va almashish tugamaguncha ushlab turadi."""
    global _active_requests
    with _state:
        while _switching:
            _state.wait()
        _active_requests += 1
    try:
        yield
    finally:
        with _state:
            _active_requests -= 1
            if _active_requests == 0:
                _state.notify_all()


def _identity(cfg):
    return (
        cfg.get("ENGINE"),
        str(cfg.get("NAME") or ""),
        cfg.get("HOST") or "",
        str(cfg.get("PORT") or ""),
    )


def _reset_thread_connection():
    """Joriy thread'ning keshlangan ulanishini va konfiguratsiya keshini tozalaydi."""
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


def ensure_current_connection():
    """Thread'da eski (SQLite) ulanish qolgan bo'lsa — tashlab yuboradi."""
    try:
        conn = connections["default"]
    except Exception:
        return
    try:
        current = _identity(conn.settings_dict)
    except Exception:
        current = None
    if current != _identity(settings.DATABASES["default"]):
        _reset_thread_connection()


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
    global _switching
    from django.core.management import call_command

    cfg = getattr(settings, "POSTGRES_DB_CONFIG", None)
    sqlite_cfg = getattr(settings, "SQLITE_DB_CONFIG", None)
    if not cfg or not sqlite_cfg:
        return False

    with _state:
        _switching = True
        while _active_requests:
            _state.wait()
    try:
        _reset_thread_connection()
        settings.DATABASES["default"] = cfg
        try:
            call_command("migrate", interactive=False, verbosity=0)
        except Exception:
            logger.exception("Postgres'da migratsiya bajarilmadi - SQLite'da qolamiz")
            _reset_thread_connection()
            settings.DATABASES["default"] = sqlite_cfg
            return False

        settings.DB_FALLBACK_REASON = ""
        logger.warning("Postgres qaytdi - SQLite fallback'dan Postgres'ga o'tildi")
        return True
    finally:
        with _state:
            _switching = False
            _state.notify_all()


def maybe_recover(force: bool = False) -> bool:
    """Fallback holatida bo'lsak, Postgres'ni qayta tekshiradi."""
    if not getattr(settings, "DB_FALLBACK_REASON", ""):
        return False
    if not postgres_ready():
        return False
    return switch_to_postgres()


def _watch_loop(interval):
    while True:
        try:
            maybe_recover()
        except Exception:
            logger.exception("Bazani qayta ulash tekshiruvi yiqildi")
        time.sleep(interval)


def start_watchdog() -> bool:
    """Fon taymerini bir marta ishga tushiradi (har worker jarayonida bitta)."""
    global _started
    with _start_lock:
        if _started:
            return False
        _started = True

    if not getattr(settings, "POSTGRES_DB_CONFIG", None):
        return False

    interval = _interval()
    thread = threading.Thread(target=_watch_loop, args=(interval,), name="db-recovery", daemon=True)
    thread.start()
    logger.info("Postgres recovery watchdog started (har %ss)", interval)
    return True


class DatabaseSyncMiddleware:
    """So'rovni baza almashishidan himoyalaydi va thread ulanishini yangilaydi."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with request_scope():
            ensure_current_connection()
            return self.get_response(request)
