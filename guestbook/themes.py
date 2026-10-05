import re
from functools import lru_cache

from django.conf import settings
from django.contrib.staticfiles import finders


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


# Optional per-theme assets, used only when the file exists:
#
#   img/share/<theme>.png           link preview image (1200 x 630)
#   img/favicons/<theme>.svg        favicon for modern browsers
#   img/favicons/<theme>-32.png     favicon fallback
#   img/favicons/<theme>-180.png    iOS home screen icon
THEME_ASSETS = {
    "share_image": "img/share/{theme}.png",
    "favicon_svg": "img/favicons/{theme}.svg",
    "favicon_png": "img/favicons/{theme}-32.png",
    "apple_touch_icon": "img/favicons/{theme}-180.png",
}


@lru_cache(maxsize=64)
def _static_exists(path: str) -> bool:
    return finders.find(path) is not None


def theme_assets(
    theme: str | None = None,
) -> dict[str, str]:
    """
    Return the static paths of the theme's optional assets.

    Missing assets map to "", so templates can skip their tags.
    """
    name = settings.GUESTBOOK_THEME if theme is None else theme

    assets = {}

    for key, pattern in THEME_ASSETS.items():
        path = pattern.format(theme=name)
        assets[key] = path if _static_exists(path) else ""

    return assets
