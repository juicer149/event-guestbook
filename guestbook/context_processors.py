from typing import Any

from django.conf import settings
from django.http import HttpRequest

from .themes import ornament_image, theme_stylesheet


def event(
    request: HttpRequest,
) -> dict[str, Any]:
    """
    Expose the event identity and theme to every template.
    """
    return {
        "eyebrow": settings.GUESTBOOK_EYEBROW,
        "theme_stylesheet": theme_stylesheet(),
        "theme_color": settings.GUESTBOOK_THEME_COLOR,
        "ornament": ornament_image(),
    }
