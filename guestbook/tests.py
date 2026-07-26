from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .access import SESSION_ACCESS_KEY
from .models import Entry


class GuestbookAccessTests(TestCase):
    def setUp(self) -> None:
        now = timezone.now()

        self.event_settings = {
            "GUESTBOOK_ACCESS_KEY": "test-secret",
            "GUESTBOOK_STARTS_AT": now - timedelta(hours=1),
            "GUESTBOOK_ENDS_AT": now + timedelta(hours=6),
            "GUESTBOOK_CLOSES_AT": now + timedelta(days=2),
        }

    def test_regular_visitor_cannot_see_create_button(self):
        with self.settings(**self.event_settings):
            response = self.client.get(
                reverse("guestbook:index"),
            )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_create_entry"])

    def test_valid_join_key_grants_access(self):
        with self.settings(**self.event_settings):
            response = self.client.get(
                reverse(
                    "guestbook:join",
                    kwargs={"key": "test-secret"},
                ),
            )

        self.assertRedirects(
            response,
            reverse("guestbook:index"),
        )
        self.assertTrue(
            self.client.session[SESSION_ACCESS_KEY],
        )

    def test_invalid_join_key_returns_404(self):
        with self.settings(**self.event_settings):
            response = self.client.get(
                reverse(
                    "guestbook:join",
                    kwargs={"key": "wrong-secret"},
                ),
            )

        self.assertEqual(response.status_code, 404)

    def test_create_page_requires_session_access(self):
        with self.settings(**self.event_settings):
            response = self.client.get(
                reverse("guestbook:create-entry"),
            )

        self.assertEqual(response.status_code, 404)

    def test_authorized_visitor_can_open_create_page(self):
        session = self.client.session
        session[SESSION_ACCESS_KEY] = True
        session.save()

        with self.settings(**self.event_settings):
            response = self.client.get(
                reverse("guestbook:create-entry"),
            )

        self.assertEqual(response.status_code, 200)

    def test_authorized_visitor_can_create_entry(self):
        session = self.client.session
        session[SESSION_ACCESS_KEY] = True
        session.save()

        with self.settings(**self.event_settings):
            response = self.client.post(
                reverse("guestbook:create-entry"),
                {
                    "author_name": "Albin",
                    "message": "Grattis Simon!",
                },
            )

        self.assertRedirects(
            response,
            reverse("guestbook:index"),
        )
        self.assertTrue(
            Entry.objects.filter(
                author_name="Albin",
                message="Grattis Simon!",
            ).exists(),
        )

    def test_join_link_stops_working_when_closed(self):
        now = timezone.now()

        closed_settings = {
            "GUESTBOOK_ACCESS_KEY": "test-secret",
            "GUESTBOOK_STARTS_AT": now - timedelta(days=3),
            "GUESTBOOK_ENDS_AT": now - timedelta(days=2),
            "GUESTBOOK_CLOSES_AT": now - timedelta(hours=1),
        }

        with self.settings(**closed_settings):
            response = self.client.get(
                reverse(
                    "guestbook:join",
                    kwargs={"key": "test-secret"},
                ),
            )

        self.assertEqual(response.status_code, 404)

    def test_existing_access_cannot_create_when_closed(self):
        session = self.client.session
        session[SESSION_ACCESS_KEY] = True
        session.save()

        now = timezone.now()

        closed_settings = {
            "GUESTBOOK_STARTS_AT": now - timedelta(days=3),
            "GUESTBOOK_ENDS_AT": now - timedelta(days=2),
            "GUESTBOOK_CLOSES_AT": now - timedelta(hours=1),
        }

        with self.settings(**closed_settings):
            response = self.client.get(
                reverse("guestbook:create-entry"),
            )

        self.assertEqual(response.status_code, 404)
