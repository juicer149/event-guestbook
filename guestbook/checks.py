from typing import Any

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.checks import Error, register

from .lifecycle import configured_schedule
from .themes import (
    THEME_NAME_PATTERN,
    ornament_image,
    theme_stylesheet,
)


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
def check_ornament(
    app_configs: Any = None,
    **kwargs: Any,
) -> list[Error]:
    """
    Refuse to start when the configured ornament does not exist.
    """
    ornament = settings.GUESTBOOK_ORNAMENT

    if not ornament:
        return []

    if not THEME_NAME_PATTERN.match(ornament):
        return [
            Error(
                (
                    f"GUESTBOOK_ORNAMENT={ornament!r} is not a "
                    "valid ornament name."
                ),
                hint=(
                    "Use lowercase letters, digits and "
                    "hyphens, e.g. bow."
                ),
                id="guestbook.E004",
            )
        ]

    image = ornament_image(ornament)

    if finders.find(image) is None:
        return [
            Error(
                f"Ornament image static/{image} was not found.",
                hint=(
                    "Add the SVG or leave GUESTBOOK_ORNAMENT "
                    "empty to use the plain divider."
                ),
                id="guestbook.E005",
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
