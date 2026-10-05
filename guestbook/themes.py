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
