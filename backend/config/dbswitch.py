"""Startupda migratsiyalarni xavfsiz qo'llash.

Baza bitta va o'zgarmas (Postgres yoki lokal SQLite). Qolgani:

  * fayl-lock bilan `migrate` — parallel worker'lar bir vaqtda migratsiya
    qilmaydi (eskirgan lock 5 daqiqadan keyin avtomatik tozalanadi);
  * baza vaqtincha yopiq bo'lsa (telefon/Tailscale hali ko'tarilmagan),
    bir necha marta qayta uriniladi;
  * oxirgi xato `LAST_ERROR` ga yoziladi (health-check ishlatishi mumkin).
"""

import logging
import os
import tempfile
import time
from pathlib import Path

logger = logging.getLogger(__name__)

MIGRATE_LOCK_PATH = Path(tempfile.gettempdir()) / "taklifnoma-migrate.lock"
STALE_LOCK_SECONDS = 300
LAST_ERROR: str | None = None


def _acquire_lock(deadline: float):
    while time.monotonic() < deadline:
        try:
            return os.open(MIGRATE_LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                age = time.time() - MIGRATE_LOCK_PATH.stat().st_mtime
                if age > STALE_LOCK_SECONDS:
                    MIGRATE_LOCK_PATH.unlink()
                    continue
            except OSError:
                pass
            time.sleep(1)
        except OSError:
            return None
    return None


def apply_migrations(timeout: float = 120.0, attempts: int = 5) -> bool:
    """Startupdagi fayl-lock bilan migratsiyalarni qo'llaydi."""
    global LAST_ERROR
    if os.environ.get("DJANGO_AUTO_MIGRATE", "1") != "1":
        return False

    from django.core.management import call_command
    from django.db import OperationalError, connections

    fd = _acquire_lock(time.monotonic() + timeout)
    if fd is None:
        logger.warning("Migratsiya lock'i olinmadi - migrate o'tkazib yuborildi")
        return False

    try:
        for attempt in range(1, attempts + 1):
            try:
                call_command("migrate", interactive=False, verbosity=0)
                LAST_ERROR = None
                logger.warning("Database migrations applied")
                return True
            except OperationalError as exc:
                # Baza hali tayyor emas: ulanishni yopib, biroz kutib qayta urinamiz
                LAST_ERROR = str(exc)
                connections.close_all()
                if attempt == attempts:
                    logger.exception("Automatic migration failed")
                    raise
                wait = min(5 * attempt, 20)
                logger.warning("Baza tayyor emas (urinish %s/%s), %ss kutilmoqda", attempt, attempts, wait)
                time.sleep(wait)
            except Exception as exc:
                LAST_ERROR = str(exc)
                logger.exception("Automatic migration failed")
                raise
    finally:
        os.close(fd)
        try:
            MIGRATE_LOCK_PATH.unlink()
        except OSError:
            pass
