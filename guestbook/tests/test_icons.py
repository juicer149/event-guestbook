from pathlib import Path

from django.conf import settings
from django.template import Context, Template, TemplateSyntaxError
from django.test import SimpleTestCase

from guestbook.templatetags.guestbook_icons import icon


ICON_DIRECTORY = (
    Path(settings.BASE_DIR)
    / "templates"
    / "guestbook"
    / "icons"
)


def render(source: str) -> str:
    return Template(
        "{% load guestbook_icons %}" + source,
    ).render(Context())


class IconTagTests(SimpleTestCase):
    def test_renders_inline_svg(self) -> None:
        html = render('{% icon "plus" %}')

        self.assertTrue(html.startswith("<svg"))
        self.assertIn('viewBox="0 0 24 24"', html)
        self.assertIn('aria-hidden="true"', html)
        self.assertIn('d="M12 5v14"', html)

    def test_adds_css_class(self) -> None:
        html = render(
            '{% icon "plus" class="feed-action__icon" %}',
        )

        self.assertIn('class="feed-action__icon"', html)

    def test_escapes_css_class(self) -> None:
        html = icon(
            "plus",
            **{"class": '"><script>x</script>'},
        )

        self.assertNotIn("<script>", html)
        self.assertIn("&quot;&gt;&lt;script&gt;", html)

    def test_unknown_icon_fails_loudly(self) -> None:
        with self.assertRaises(Exception):
            render('{% icon "does-not-exist" %}')

    def test_invalid_icon_name_is_rejected(self) -> None:
        with self.assertRaises(TemplateSyntaxError):
            render('{% icon "../base.html" %}')

    def test_every_icon_file_renders(self) -> None:
        names = sorted(
            path.stem
            for path in ICON_DIRECTORY.glob("*.svg")
        )

        self.assertTrue(names)

        for name in names:
            with self.subTest(icon=name):
                html = render(f'{{% icon "{name}" %}}')

                self.assertTrue(html.startswith("<svg "))
                self.assertIn("viewBox=", html)
