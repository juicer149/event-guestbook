"""
Inline SVG icons from templates/guestbook/icons/<name>.svg.

    {% load guestbook_icons %}
    {% icon "plus" class="feed-action__icon" %}

The SVG is written inline into the page, so existing CSS (stroke,
fill, size) keeps working exactly as with hand-written markup. Icons
are decorative and always get aria-hidden="true"; the surrounding
link or button carries the accessible label.
"""

import re
from django import template
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe


register = template.Library()

ICON_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _icon_markup(name: str) -> str:
    if not ICON_NAME_PATTERN.match(name):
        raise template.TemplateSyntaxError(
            f"Invalid icon name: {name!r}"
        )

    markup = get_template(
        f"guestbook/icons/{name}.svg",
    ).render().strip()

    if not markup.startswith("<svg "):
        raise template.TemplateSyntaxError(
            f"Icon {name!r} must start with <svg."
        )

    return markup


@register.simple_tag
def icon(
    name: str,
    *,
    css_class: str = "",
    **attributes: str,
) -> SafeString:
    """
    Render one icon, optionally with a CSS class.

    Accepts class="..." in the template (passed through **attributes
    because "class" is a Python keyword).
    """
    css_class = attributes.pop("class", css_class)

    if attributes:
        raise template.TemplateSyntaxError(
            f"Unsupported icon attributes: {sorted(attributes)}"
        )

    extra = (
        format_html(' class="{}"', css_class)
        if css_class
        else ""
    )

    markup = _icon_markup(name)

    return mark_safe(
        markup.replace(
            "<svg ",
            f'<svg{extra} aria-hidden="true" ',
            1,
        )
    )
