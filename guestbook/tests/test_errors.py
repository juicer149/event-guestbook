from unittest.mock import patch

from django.test import (
    Client,
    RequestFactory,
    TestCase,
    override_settings,
)
from django.urls import reverse

from guestbook import errors


@override_settings(
    GUESTBOOK_TITLE="Testfest",
    GUESTBOOK_EYEBROW="TEST 18",
    GUESTBOOK_ACCESS_KEY="test-secret-key",
)
class ErrorPageTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_unknown_page_shows_guest_404(self) -> None:
        response = self.client.get("/finns-inte/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            "Skanna QR-koden",
            status_code=404,
        )
        self.assertContains(response, "Testfest", status_code=404)
        self.assertContains(response, "TEST 18", status_code=404)

    def test_404_has_no_link_back_to_album(self) -> None:
        response = self.client.get("/finns-inte/")

        self.assertNotContains(
            response,
            "Tillbaka till albumet",
            status_code=404,
        )

    def test_album_without_session_shows_guest_404(self) -> None:
        response = self.client.get(
            reverse("guestbook:index"),
        )

        self.assertContains(
            response,
            "Skanna QR-koden",
            status_code=404,
        )

    def test_csrf_failure_shows_guest_403(self) -> None:
        client = Client(enforce_csrf_checks=True)

        response = client.post(
            reverse("guestbook:upload_photos"),
        )

        self.assertContains(
            response,
            "Sidan hann gå ut",
            status_code=403,
        )
        self.assertContains(
            response,
            "Tillbaka till albumet",
            status_code=403,
        )

    def test_bad_request_page(self) -> None:
        response = errors.bad_request(
            self.factory.get("/"),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "färre bilder",
            response.content.decode(),
        )

    def test_server_error_page(self) -> None:
        response = errors.server_error(
            self.factory.get("/"),
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn(
            "Något gick fel",
            response.content.decode(),
        )

    def test_falls_back_to_plain_text_if_rendering_fails(
        self,
    ) -> None:
        with patch(
            "guestbook.errors.render",
            side_effect=RuntimeError("template broken"),
        ):
            response = errors.server_error(
                self.factory.get("/"),
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response["Content-Type"],
            "text/plain; charset=utf-8",
        )
