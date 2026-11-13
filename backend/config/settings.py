"""
Django settings for the Taklifnoma (online invitation) project.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-key-change-me-in-production-9f2a1c",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Render/Vercel uchun vergul bilan ajratilgan ro'yxat: "example.com,example2.com"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]

# Render health-check va loglar uchun aniq ko'rinadigan xatoliklar
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "{levelname} {asctime} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django.db.backends": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_DB_LOG_LEVEL", "WARNING"),
        },
    },
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "accounts",
    "invitations",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.dbswitch.DatabaseSyncMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# DATABASE_URL (Render/Neon Postgres) berilsa — faqat Postgres ishlatiladi,
# bo'lmasa (lokal ishlab chiqishda) SQLite.
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
# SQLite'ga avtomatik o'tish (fallback) butunlay o'chirilgan.
DB_FALLBACK_ENABLED = False
# Faqat diagnostika uchun: dbswitch yozishi mumkin, health endi ishlatmaydi.
DB_FALLBACK_REASON = ""


POSTGRES_DB_CONFIG = None
SQLITE_DB_CONFIG = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
}


def _sqlite_database():
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    from urllib.parse import parse_qs, unquote, urlparse

    _db = urlparse(DATABASE_URL)
    _query = parse_qs(_db.query)
    # sslmode'ni majburan "require" qilmaymiz: Tailscale/GOST orqali ulangan
    # lokal Postgres SSL'ni qo'llab-quvvatlamasligi mumkin (aqlli standart —
    # psycopg'ning "prefer"i: imkon bo'lsa SSL, bo'lmasa oddiy ulanish).
    # Agar URL'da ?sslmode=... berilgan bo'lsa — aynan o'shanisi ishlatiladi.
    _db_options = {}
    if "sslmode" in _query and _query["sslmode"]:
        _db_options["sslmode"] = _query["sslmode"][0]
    elif _db.hostname not in ("127.0.0.1", "localhost", "::1", None):
        _db_options["sslmode"] = "require"
    # Osilib qolmasin: baza yopiq bo'lsa health-check 5 soniyada javob beradi
    try:
        _db_options["connect_timeout"] = max(1, int(os.environ.get("DJANGO_DB_CONNECT_TIMEOUT", "5")))
    except ValueError:
        _db_options["connect_timeout"] = 5

    _pg = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(_db.path.lstrip("/")),
        "USER": unquote(_db.username or ""),
        "PASSWORD": unquote(_db.password or ""),
        "HOST": _db.hostname or "",
        "PORT": str(_db.port or 5432),
        "CONN_MAX_AGE": 60,
        "OPTIONS": _db_options,
    }
    # Eslatma: bu sozlamalar Postgres qaytganda avtomatik almashish uchun
    # config/dbswitch.py tomonidan ishlatiladi.
    POSTGRES_DB_CONFIG = _pg

    # MUHIM: SQLite'ga jimgina o'tish o'chirilgan.
    # Postgres bo'lmasa ilova ishlamaydi va /api/health/ 503 qaytaradi —
    # shunda deploy'da darhol ko'rinadi va taklifnomalar yo'qolmaydi.
    DATABASES = {"default": _pg}
else:
    DATABASES = _sqlite_database()

# Render kabi proxy ortida HTTPS'ni to'g'ri aniqlash uchun
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# CORS (Vite dev server runs on another port during development)
# ---------------------------------------------------------------------------
# ---- Google bilan kirish -------------------------------------------------
# Google Cloud Console → APIs & Services → Credentials → OAuth client (Web).
# Authorized redirect URI: https://<backend>/api/auth/google/callback/
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "").strip()
# Login tugagach qaytadigan frontend manzili (Vercel domeni)
# Bo'sh bo'lsa — Google qaytish manzili brauzer yuborgan (tekshirilgan) origin'dan
# olinadi, shuning uchun prod'da localhost'ga qaytib qolmaydi.
FRONTEND_URL = os.environ.get("FRONTEND_URL", "").strip()

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
# Vercel domenlari: DJANGO_CORS_ORIGINS="https://app.vercel.app,https://..." (vergul bilan)
_extra_origins = [
    o.strip().rstrip("/")
    for o in os.environ.get("DJANGO_CORS_ORIGINS", "").split(",")
    if o.strip()
]
CORS_ALLOWED_ORIGINS += _extra_origins
CSRF_TRUSTED_ORIGINS = list(_extra_origins) + ["https://taklifnoma-1.onrender.com"]
# Aniq domen kiritilmagan bo'lsa — hamma joyga ruxsat (ochiq API, kod orqali himoyalangan)
CORS_ALLOW_ALL_ORIGINS = not _extra_origins

# ---------------------------------------------------------------------------
# DRF — anonymous rate limiting helps protect invitation codes from
# brute-force guessing (privacy requirement).
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "120/min",
    },
}