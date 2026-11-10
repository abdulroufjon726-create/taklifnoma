"""
WSGI config for the Taklifnoma project.

Bepul hostingda (Render) baza bo'sh konteyner bilan qayta ko'tarilishi yoki
birinchi marta ulanishingiz mumkin — bunday holatda API "no such table" bilan
500 qaytaradi. Shu sababli ishga tushishda asosiy jadval bor-yo'qligini
tekshiramiz va bo'lmasa migratsiyalarni bir marta qo'llaymiz (fayl-lock bilan —
parallel worker'lar bir vaqtda migrate qilmaydi).

Sxema allaqachon mavjud bo'lsa, bu tekshiruv bir yengil so'rov bilan tugaydi.
`DJANGO_AUTO_MIGRATE=0` bilan butunlay o'chirish mumkin — u holda migratsiyani
`python manage.py migrate` (render.yaml startCommand) bajaradi.
"""

import logging
import os
import tempfile
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

logger = logging.getLogger("config.wsgi")


def _ensure_schema() -> None:
    """Jadval yo'q bo'lsa — migratsiyalarni qo'llaydi."""
    if os.environ.get("DJANGO_AUTO_MIGRATE", "1") != "1":
        return

    try:
        from django.db import connection

        existing = set(connection.introspection.table_names())
    except Exception:
        logger.exception("Schema check failed")
        return

    if "invitations_invitation" in existing:
        return

    lock_path = Path(tempfile.gettempdir()) / "taklifnoma-migrate.lock"
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        # Boshqa worker allaqachon migrate qilmoqda
        return
    except OSError:
        fd = None

    try:
        from django.core.management import call_command

        logger.warning("Empty database detected - applying migrations")
        call_command("migrate", interactive=False, verbosity=0)
    except Exception:
        logger.exception("Automatic migration failed")
    finally:
        if fd is not None:
            os.close(fd)
            try:
                lock_path.unlink()
            except OSError:
                pass


try:
    import django

    django.setup()
    _ensure_schema()
except Exception:  # pragma: no cover - hech qachon serverni yiqitmaymiz
    logger.exception("WSGI bootstrap failed")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
