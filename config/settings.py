import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parent.parent


# Development settings.
# These values must be replaced with environment variables before deployment.

SECRET_KEY = (
    "django-insecure-6+@_5wx#jxs@!zgqvj*(5ox$f=qk_0="
    "41w-g@1nhdtd(koj%nj"
)

DEBUG = True

ALLOWED_HOSTS: list[str] = []


# Application definition

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
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
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


# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation

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


# Internationalization

LANGUAGE_CODE = "sv-se"

TIME_ZONE = "Europe/Stockholm"

USE_I18N = True

USE_TZ = True


# Static files

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Uploaded media

MEDIA_URL = "media/"

MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Guestbook configuration

GUESTBOOK_TITLE = "Simon 30 år"

GUESTBOOK_STARTS_AT = datetime(
    2026,
    8,
    1,
    18,
    0,
    tzinfo=ZoneInfo("Europe/Stockholm"),
)

GUESTBOOK_ENDS_AT = datetime(
    2026,
    8,
    2,
    2,
    0,
    tzinfo=ZoneInfo("Europe/Stockholm"),
)

GUESTBOOK_ACCESS_KEY = os.environ.get(
    "GUESTBOOK_ACCESS_KEY",
    "local-development-key",
)
