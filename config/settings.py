import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

STOCKHOLM_TZ = ZoneInfo("Europe/Stockholm")


# ---------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------


def env_bool(
    name: str,
    *,
    default: bool = False,
) -> bool:
    value = os.environ.get(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def env_list(
    name: str,
    *,
    default: str = "",
) -> list[str]:
    return [
        item.strip()
        for item in os.environ.get(name, default).split(",")
        if item.strip()
    ]


def unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------

DEBUG = env_bool(
    "DEBUG",
    default=True,
)

TESTING = "test" in sys.argv

RAILWAY_PUBLIC_DOMAIN = os.environ.get(
    "RAILWAY_PUBLIC_DOMAIN",
    "",
).strip()


# ---------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------

if DEBUG:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "django-insecure-local-development-key",
    )
else:
    SECRET_KEY = os.environ["SECRET_KEY"]


ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
)

if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

ALLOWED_HOSTS = unique(ALLOWED_HOSTS)


CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
)

if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(
        f"https://{RAILWAY_PUBLIC_DOMAIN}"
    )

CSRF_TRUSTED_ORIGINS = unique(
    CSRF_TRUSTED_ORIGINS
)


if not DEBUG:
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"


# ---------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "guestbook.apps.GuestbookConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django."
            "DjangoTemplates"
        ),
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors."
                    "request"
                ),
                (
                    "django.contrib.auth."
                    "context_processors.auth"
                ),
                (
                    "django.contrib.messages."
                    "context_processors.messages"
                ),
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


# ---------------------------------------------------------------------
# Database
#
# Local development:
#     No DATABASE_URL -> SQLite
#
# Railway:
#     DATABASE_URL -> PostgreSQL
# ---------------------------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=(
            f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
        ),
        conn_max_age=600,
        conn_health_checks=True,
    ),
}


# ---------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------

LANGUAGE_CODE = "sv-se"

TIME_ZONE = "Europe/Stockholm"

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


if DEBUG or TESTING:
    STATICFILES_BACKEND = (
        "django.contrib.staticfiles.storage."
        "StaticFilesStorage"
    )
else:
    STATICFILES_BACKEND = (
        "whitenoise.storage."
        "CompressedManifestStaticFilesStorage"
    )


STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": STATICFILES_BACKEND,
    },
}


# ---------------------------------------------------------------------
# Uploaded media
#
# Local development:
#     <project>/media/
#
# Railway with a volume:
#     RAILWAY_VOLUME_MOUNT_PATH
# ---------------------------------------------------------------------

MEDIA_URL = "/media/"

MEDIA_ROOT = Path(
    os.environ.get(
        "RAILWAY_VOLUME_MOUNT_PATH",
        BASE_DIR / "media",
    )
)


# ---------------------------------------------------------------------
# Default primary key field type
# ---------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------
# Guestbook configuration
# ---------------------------------------------------------------------

GUESTBOOK_TITLE = os.environ.get(
    "GUESTBOOK_TITLE",
    "Simons 30-årsfest",
)


GUESTBOOK_ACCESS_KEY = os.environ.get(
    "GUESTBOOK_ACCESS_KEY",
    "",
)


GUESTBOOK_STARTS_AT = datetime(
    2026,
    8,
    1,
    18,
    0,
    tzinfo=STOCKHOLM_TZ,
)


GUESTBOOK_ENDS_AT = datetime(
    2026,
    8,
    2,
    2,
    0,
    tzinfo=STOCKHOLM_TZ,
)


# ---------------------------------------------------------------------
# Guestbook lifecycle
# ---------------------------------------------------------------------

GUESTBOOK_JOIN_OPENS_AT = (
    GUESTBOOK_STARTS_AT
    - timedelta(hours=6)
)


GUESTBOOK_JOIN_CLOSES_AT = (
    GUESTBOOK_ENDS_AT
    + timedelta(hours=12)
)


GUESTBOOK_ENTRIES_CLOSE_AT = (
    GUESTBOOK_ENDS_AT
    + timedelta(days=1)
)


GUESTBOOK_CLOSES_AT = (
    GUESTBOOK_ENDS_AT
    + timedelta(days=7)
)


GUESTBOOK_GUEST_ACCESS_DURATION = timedelta(
    days=7,
)
