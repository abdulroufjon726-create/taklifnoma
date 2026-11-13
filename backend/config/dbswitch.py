"""Startupda migratsiyalarni xavfsiz qo'llash.

Baza bitta va o'zgarmas (Postgres yoki lokal SQLite). Ilgari mavjud bo'lgan
SQLite fallback, fon watchdog va avtomatik baza almashish mantiqlari butunlay
olib tashlangan. Qolgani:

  * fayl-lock bilan `migrate` — parallel worker'lar bir vaqtda migratsiya
    qilmaydi;
  * xato `settings.MIGRATION_ERROR` ga yoziladi, /api/health/ uni ko'rsatadi.
"""

import logging
import os
import tempfile
import time
from pathlib import Path

logger = logging.getLogger(__name__)

MIGRATE_LOCK_PATH = Path(tempfile.gettempdir()) / "taklifnoma-migrate.lock"


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
