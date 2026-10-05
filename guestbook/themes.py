import re

from django.conf import settings


THEME_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def theme_stylesheet(
    theme: str | None = None,
) -> str:
    """
    Return the static path of the configured theme stylesheet.
    """
    name = settings.GUESTBOOK_THEME if theme is None else theme

    return f"css/themes/{name}.css"


def ornament_image(
    ornament: str | None = None,
) -> str:
    """
    Return the static path of the configured ornament, or "" for none.
    """
    name = (
        settings.GUESTBOOK_ORNAMENT
        if ornament is None
        else ornament
    )

    if not name:
        return ""

    return f"img/ornaments/{name}.svg"
