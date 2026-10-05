from django.apps import AppConfig


class GuestbookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "guestbook"

    def ready(self) -> None:
        from . import checks  # noqa: F401  (registers system checks)
