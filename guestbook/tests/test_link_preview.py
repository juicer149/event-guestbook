from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from guestbook.access import SESSION_GUEST_ACCESS_KEY
from guestbook.phases import GuestbookPhase
from guestbook.tests.test_views import state_for
from guestbook.themes import theme_assets


@override_settings(
    GUESTBOOK_ACCESS_KEY="test-secret-key",
    GUESTBOOK_TITLE="Testfest",
    GUESTBOOK_DESCRIPTION="Dela bilder från testfesten.",
    GUESTBOOK_THEME="felicia-18",
    GUESTBOOK_ORNAMENT="",
    ALLOWED_HOSTS=["fest.example"],
)
class LinkPreviewTests(TestCase):
    def get_index(self):
        session = self.client.session
        session[SESSION_GUEST_ACCESS_KEY] = True
        session.save()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(GuestbookPhase.LIVE),
        ):
            return self.client.get(
                reverse("guestbook:index"),
                HTTP_HOST="fest.example",
            )

    def test_index_has_open_graph_tags(self) -> None:
        response = self.get_index()

        self.assertContains(
            response,
            '<meta property="og:title" content="Testfest">',
            html=True,
        )
        self.assertContains(
            response,
            "Dela bilder från testfesten.",
        )

    def test_share_image_is_absolute(self) -> None:
        response = self.get_index()

        self.assertContains(
            response,
            "http://fest.example/static/img/share/felicia-18",
        )

    def test_favicons_are_linked(self) -> None:
        response = self.get_index()

        self.assertContains(response, "img/favicons/felicia-18.svg")
        self.assertContains(response, 'rel="apple-touch-icon"')

    def test_crawler_without_session_still_gets_preview(
        self,
    ) -> None:
        response = self.client.get(
            reverse("guestbook:index"),
            HTTP_HOST="fest.example",
        )

        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            'property="og:title"',
            status_code=404,
        )

    @override_settings(GUESTBOOK_THEME="white-party")
    def test_theme_without_assets_omits_tags(self) -> None:
        response = self.get_index()

        self.assertNotContains(response, 'property="og:image"')
        self.assertNotContains(response, 'rel="apple-touch-icon"')


class ThemeAssetTests(TestCase):
    def test_felicia_has_all_assets(self) -> None:
        assets = theme_assets("felicia-18")

        self.assertTrue(all(assets.values()), assets)

    def test_missing_assets_are_empty(self) -> None:
        assets = theme_assets("white-party")

        self.assertEqual(set(assets.values()), {""})
