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
import time
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

logger = logging.getLogger("config.wsgi")


def _ensure_schema() -> None:
    """Migratsiyalarni qo'llaydi (bo'sh baza ham, eskirgan sxema ham)."""
    if os.environ.get("DJANGO_AUTO_MIGRATE", "1") != "1":
        return

    lock_path = Path(tempfile.gettempdir()) / "taklifnoma-migrate.lock"
    tried = 0
    while tried < 3:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            # Boshqa worker migrate qilmoqda — tugashini kutamiz
            if tried == 0:
                logger.warning("Waiting for another worker's migrations")
            tried += 1
            time.sleep(1)
            if tried == 3:
                return
        except OSError:
            fd = None
            break

    try:
        from django.conf import settings
        from django.core.management import call_command

        call_command("migrate", interactive=False, verbosity=0)
        logger.warning("Database migrations applied")
        settings.MIGRATION_ERROR = ""
    except Exception as exc:
        logger.exception("Automatic migration failed")
        try:
            from django.conf import settings

            settings.MIGRATION_ERROR = str(exc).replace("\n", " ")[:300]
        except Exception:
            pass
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

    from config import dbswitch

    dbswitch.start_watchdog()
except Exception:  # pragma: no cover - hech qachon serverni yiqitmaymiz
    logger.exception("WSGI bootstrap failed")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
