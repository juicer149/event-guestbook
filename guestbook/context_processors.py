from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.templatetags.static import static

from .themes import (
    ornament_image,
    theme_assets,
    theme_stylesheet,
)


def event(
    request: HttpRequest,
) -> dict[str, Any]:
    """
    Expose the event identity and theme to every template.
    """
    assets = theme_assets()

    # Link previews (Messenger, Snapchat, iMessage) need an absolute
    # image URL. They also see error pages, since the crawler has no
    # guest session, so these tags live in base.html.
    share_image_url = (
        request.build_absolute_uri(
            static(assets["share_image"]),
        )
        if assets["share_image"]
        else ""
    )

    return {
        "description": settings.GUESTBOOK_DESCRIPTION,
        "share_image_url": share_image_url,
        "favicon_svg": assets["favicon_svg"],
        "favicon_png": assets["favicon_png"],
        "apple_touch_icon": assets["apple_touch_icon"],
        "eyebrow": settings.GUESTBOOK_EYEBROW,
        "theme_stylesheet": theme_stylesheet(),
        "theme_color": settings.GUESTBOOK_THEME_COLOR,
        "theme_color_dark": settings.GUESTBOOK_THEME_COLOR_DARK,
        "ornament": ornament_image(),
    }
