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


def env_int(
    name: str,
    *,
    default: int,
) -> int:
    value = os.environ.get(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError as error:
        raise ValueError(
            f"{name} must be an integer."
        ) from error


def env_list(
    name: str,
    *,
    default: str = "",
) -> list[str]:
    return [
        item.strip()
        for item in os.environ.get(
            name,
            default,
        ).split(",")
        if item.strip()
    ]


def unique(
    items: list[str],
) -> list[str]:
    return list(
        dict.fromkeys(items)
    )


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
    ALLOWED_HOSTS.append(
        RAILWAY_PUBLIC_DOMAIN,
    )

ALLOWED_HOSTS = unique(
    ALLOWED_HOSTS,
)


CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
)

if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(
        f"https://{RAILWAY_PUBLIC_DOMAIN}",
    )

CSRF_TRUSTED_ORIGINS = unique(
    CSRF_TRUSTED_ORIGINS,
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
# This remains file-system based for now.
#
# Local:
#     <project>/media/
#
# Railway volume:
#     RAILWAY_VOLUME_MOUNT_PATH
#
# Object storage will replace the default storage backend later.
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

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# ---------------------------------------------------------------------
# Guestbook identity
# ---------------------------------------------------------------------

GUESTBOOK_TITLE = os.environ.get(
    "GUESTBOOK_TITLE",
    "Simons 30-årsfest",
)


GUESTBOOK_ACCESS_KEY = os.environ.get(
    "GUESTBOOK_ACCESS_KEY",
    "",
).strip()


# ---------------------------------------------------------------------
# Guestbook event schedule
#
# Only the event boundaries and phase durations are configured.
#
# CLOSED:
#     moment < PRE_START
#
# PRE:
#     PRE_START <= moment < STARTS_AT
#
# LIVE:
#     STARTS_AT <= moment < ENDS_AT
#
# POST:
#     ENDS_AT <= moment < POST_END
#
# ARCHIVED:
#     POST_END <= moment
# ---------------------------------------------------------------------

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

GUESTBOOK_PRE_DURATION = timedelta(
    days=10,
)

GUESTBOOK_POST_DURATION = timedelta(
    hours=24,
)


# ---------------------------------------------------------------------
# Guestbook development controls
#
# GUESTBOOK_DEV_PHASE only has an effect while DEBUG=True.
#
# Supported values:
#     closed
#     pre
#     live
#     post
#     archived
#
# GUESTBOOK_BYPASS_SCHEDULE forces LIVE. Keep it disabled in
# production; it exists as a temporary deployment/testing switch.
# ---------------------------------------------------------------------

GUESTBOOK_DEV_PHASE = os.environ.get(
    "GUESTBOOK_DEV_PHASE",
    "",
).strip().lower()


GUESTBOOK_BYPASS_SCHEDULE = env_bool(
    "GUESTBOOK_BYPASS_SCHEDULE",
    default=False,
)


# ---------------------------------------------------------------------
# Guest access
# ---------------------------------------------------------------------

GUESTBOOK_GUEST_ACCESS_DURATION = timedelta(
    days=30,
)


# ---------------------------------------------------------------------
# Upload limits
#
# Limits are enforced by PostUploadForm.
# Request-level limits provide an additional outer boundary.
# ---------------------------------------------------------------------

GUESTBOOK_MAX_IMAGES_PER_POST = env_int(
    "GUESTBOOK_MAX_IMAGES_PER_POST",
    default=20,
)

GUESTBOOK_MAX_IMAGE_BYTES = env_int(
    "GUESTBOOK_MAX_IMAGE_BYTES",
    default=15 * 1024 * 1024,
)

GUESTBOOK_MAX_REQUEST_BYTES = env_int(
    "GUESTBOOK_MAX_REQUEST_BYTES",
    default=250 * 1024 * 1024,
)


DATA_UPLOAD_MAX_MEMORY_SIZE = (
    GUESTBOOK_MAX_REQUEST_BYTES
)

FILE_UPLOAD_MAX_MEMORY_SIZE = (
    5 * 1024 * 1024
)
