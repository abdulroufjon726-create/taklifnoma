"""
WSGI config for the Taklifnoma project.

Ishga tushishda sxema eskirgan yoki baza bo'sh bo'lishi mumkin — bunday holatda
API 500 qaytaradi. Shu sababli migratsiyalar startupda fayl-lock bilan
qo'llanadi (parallel worker'lar bir vaqtda migrate qilmaydi). Lock va
migratsiya mantig'i `config.dbswitch` da — Postgres'ga avtomatik qaytishda ham
o'sha ishlatiladi.

`DJANGO_AUTO_MIGRATE=0` bilan o'chirish mumkin — u holda migratsiyani
`python manage.py migrate` qo'lda bajariladi.
"""

import logging
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

logger = logging.getLogger("config.wsgi")


def _ensure_schema() -> None:
    from config import dbswitch

    try:
        dbswitch.apply_migrations()
        from django.conf import settings

        settings.MIGRATION_ERROR = ""
    except Exception as exc:
        logger.exception("Startup migration failed")
        try:
            from django.conf import settings

            settings.MIGRATION_ERROR = str(exc).replace("\n", " ")[:300]
        except Exception:
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
