"""
Postgres tiklansa — SQLite fallback'dan avtomatik qaytish (fon taymeri).

Ishga tushishda Postgres yetib bo'lmasa, settings.py SQLite'ga o'tadi. Baza keyin
qaytsa, servisni qayta ishga tushirmasdan ham Postgres'ga qaytish kerak. Buni fon
taymeri (daemon thread) `DJANGO_DB_RECOVERY_INTERVAL` soniyada bir marta tekshiradi.

Xavfsizlik qoidalari:
  * `request_scope()` — switch faqat faol so'rovlar tugagach bajariladi.
  * Kutish cheklangan (`DJANGO_DB_SWITCH_TIMEOUT`, sukut 5s): so'rovlar
    tugamasa, switch bekor qilinadi va keyingi urinishga qoldiriladi.
  * Har bir thread o'z keshlangan ulanishini tekshiradi
    (`ensure_current_connection`) — Django ulanishlari thread-local.
  * Migratsiya startupdagi fayl-lock bilan bajariladi (parallel worker'lar
    bir vaqtda migrate qilmaydi).
  * SQLite'da yaratilgan taklifnomalar Postgres'ga ko'chiriladi (kod bo'yicha
    takrorlanmasdan).
"""

import contextlib
import logging
import os
import tempfile
import threading
import time
from pathlib import Path

from django.conf import settings
from django.db import connections

logger = logging.getLogger(__name__)

MIGRATE_LOCK_PATH = Path(tempfile.gettempdir()) / "taklifnoma-migrate.lock"
# So'rov hech qachon cheksiz kutmasin
REQUEST_WAIT_SECONDS = 30.0


def _interval():
    try:
        return max(5.0, float(os.environ.get("DJANGO_DB_RECOVERY_INTERVAL", "30")))
    except ValueError:
        return 30.0


def _switch_timeout():
    try:
        return max(1.0, float(os.environ.get("DJANGO_DB_SWITCH_TIMEOUT", "5")))
    except ValueError:
        return 5.0


_state = threading.Condition()
_active_requests = 0
_switching = False
_started = False
_start_lock = threading.Lock()


@contextlib.contextmanager
def request_scope():
    """Baza almashtirilayotganda kutadi va almashish tugamaguncha ushlab turadi."""
    global _active_requests
    deadline = time.monotonic() + REQUEST_WAIT_SECONDS
    with _state:
        while _switching:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            _state.wait(remaining)
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


def apply_migrations(timeout: float = 120.0) -> bool:
    """Startupdagi fayl-lock bilan migratsiyalarni qo'llaydi."""
    if os.environ.get("DJANGO_AUTO_MIGRATE", "1") != "1":
        return False

    from django.core.management import call_command

    fd = None
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            fd = os.open(MIGRATE_LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            time.sleep(1)
        except OSError:
            fd = None
            break

    if fd is None:
        logger.warning("Migratsiya lock'i olinmadi - migrate o'tkazib yuborildi")
        return False

    try:
        call_command("migrate", interactive=False, verbosity=0)
        logger.warning("Database migrations applied")
        return True
    except Exception:
        logger.exception("Automatic migration failed")
        raise
    finally:
        os.close(fd)
        try:
            MIGRATE_LOCK_PATH.unlink()
        except OSError:
            pass


def _read_sqlite_invitations():
    """Joriy (SQLite) bazadagi taklifnomalarni o'qib oladi."""
    if "sqlite" not in settings.DATABASES["default"].get("ENGINE", ""):
        return []
    try:
        from invitations.models import Invitation

        rows = list(Invitation.objects.values())
        logger.warning("SQLite'dan %s taklifnoma o'qildi - Postgres'ga ko'chiriladi", len(rows))
        return rows
    except Exception:
        logger.exception("SQLite taklifnomalarini o'qib bo'lmadi")
        return []


def _copy_invitations_to_postgres(rows):
    if not rows:
        return 0
    try:
        from invitations.models import Invitation

        objects = [Invitation(**row) for row in rows]
        Invitation.objects.bulk_create(objects, ignore_conflicts=True, batch_size=200)
        logger.warning("%s taklifnoma Postgres'ga ko'chirildi", len(objects))
        return len(objects)
    except Exception:
        logger.exception("Taklifnomalarni Postgres'ga ko'chirishda xatolik")
        return 0


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
    """Postgres'ga o'tadi; so'rovlar tugamasa yoki migratsiya yiqilsa SQLite'da qoladi."""
    global _switching
    cfg = getattr(settings, "POSTGRES_DB_CONFIG", None)
    sqlite_cfg = getattr(settings, "SQLITE_DB_CONFIG", None)
    if not cfg or not sqlite_cfg:
        return False

    # 1) Faol so'rovlar tugashini cheklangan vaqt kutamiz
    with _state:
        if _switching:
            return False
        _switching = True
        deadline = time.monotonic() + _switch_timeout()
        while _active_requests:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                _switching = False
                _state.notify_all()
                logger.warning(
                    "Switch keyinga qoldirildi: %s so'rov hali tugamagan", _active_requests
                )
                return False
            _state.wait(remaining)

    try:
        # 2) SQLite'dagi ma'lumotni eslab qolamiz (hali SQLite'da ishlayapmiz)
        rows = _read_sqlite_invitations()

        # 3) Ulanishni Postgres'ga almashtiramiz
        _reset_thread_connection()
        settings.DATABASES["default"] = cfg

        try:
            apply_migrations()
        except Exception:
            logger.exception("Postgres'da migratsiya bajarilmadi - SQLite'da qolamiz")
            _reset_thread_connection()
            settings.DATABASES["default"] = sqlite_cfg
            return False

        # 4) SQLite'da yaratilgan taklifnomalarni ko'chiramiz
        _copy_invitations_to_postgres(rows)

        settings.DB_FALLBACK_REASON = ""
        logger.warning("Postgres qaytdi - SQLite fallback'dan Postgres'ga o'tildi")
        return True
    finally:
        with _state:
            _switching = False
            _state.notify_all()


def maybe_recover(force: bool = False) -> bool:
    """Fallback holatida bo'lsak, Postgres'ni qayta tekshiradi."""
    if not getattr(settings, "DB_FALLBACK_ENABLED", False):
        return False
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

    if not getattr(settings, "DB_FALLBACK_ENABLED", False):
        logger.info("SQLite fallback o'chirilgan - db-recovery watchdog ishga tushmaydi")
        return False
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
