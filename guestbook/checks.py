from typing import Any

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.checks import Error, register

from .lifecycle import configured_schedule
from .themes import THEME_NAME_PATTERN, theme_stylesheet


@register()
def check_theme(
    app_configs: Any = None,
    **kwargs: Any,
) -> list[Error]:
    """
    Refuse to start when the configured theme does not exist.
    """
    theme = settings.GUESTBOOK_THEME

    if not THEME_NAME_PATTERN.match(theme):
        return [
            Error(
                (
                    f"GUESTBOOK_THEME={theme!r} is not a valid "
                    "theme name."
                ),
                hint=(
                    "Use lowercase letters, digits and "
                    "hyphens, e.g. white-party."
                ),
                id="guestbook.E001",
            )
        ]

    stylesheet = theme_stylesheet(theme)

    if finders.find(stylesheet) is None:
        return [
            Error(
                f"Theme stylesheet static/{stylesheet} was not found.",
                hint=(
                    "Create the file or change "
                    "GUESTBOOK_THEME."
                ),
                id="guestbook.E002",
            )
        ]

    return []


@register()
def check_schedule(
    app_configs: Any = None,
    **kwargs: Any,
) -> list[Error]:
    """
    Refuse to start when the event dates are inconsistent.
    """
    try:
        configured_schedule()
    except ValueError as error:
        return [
            Error(
                f"Invalid guestbook schedule: {error}",
                hint=(
                    "Check GUESTBOOK_STARTS_AT and "
                    "GUESTBOOK_ENDS_AT."
                ),
                id="guestbook.E003",
            )
        ]

    return []
