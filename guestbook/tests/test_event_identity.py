from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from guestbook.access import SESSION_GUEST_ACCESS_KEY
from guestbook.checks import (
    check_ornament,
    check_schedule,
    check_theme,
)
from guestbook.phases import GuestbookPhase
from guestbook.tests.test_views import state_for


TZ = ZoneInfo("Europe/Stockholm")


@override_settings(
    GUESTBOOK_ACCESS_KEY="test-secret-key",
    GUESTBOOK_TITLE="Testfest",
    GUESTBOOK_THEME="white-party",
    GUESTBOOK_THEME_COLOR="#123456",
)
class EventIdentityViewTests(TestCase):
    def get_index(self):
        session = self.client.session
        session[SESSION_GUEST_ACCESS_KEY] = True
        session.save()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            return self.client.get(
                reverse("guestbook:index"),
            )

    @override_settings(GUESTBOOK_EYEBROW="FELICIA 18")
    def test_eyebrow_is_rendered(self) -> None:
        response = self.get_index()

        self.assertContains(response, "FELICIA 18")
        self.assertContains(response, 'class="event-label"')

    @override_settings(GUESTBOOK_EYEBROW="")
    def test_empty_eyebrow_is_hidden(self) -> None:
        response = self.get_index()

        self.assertNotContains(response, 'class="event-label"')

    @override_settings(GUESTBOOK_EYEBROW="")
    def test_theme_stylesheet_and_color_are_rendered(
        self,
    ) -> None:
        response = self.get_index()

        self.assertContains(response, "css/themes/white-party")
        self.assertContains(response, 'content="#123456"')


    @override_settings(GUESTBOOK_EYEBROW="", GUESTBOOK_ORNAMENT="")
    def test_plain_divider_without_ornament(self) -> None:
        response = self.get_index()

        self.assertContains(response, 'class="event-divider"')
        self.assertNotContains(response, 'class="event-ornament"')

    @override_settings(GUESTBOOK_EYEBROW="", GUESTBOOK_ORNAMENT="bow")
    def test_ornament_replaces_divider(self) -> None:
        response = self.get_index()

        self.assertContains(response, 'class="event-ornament"')
        self.assertContains(response, "img/ornaments/bow")
        self.assertNotContains(response, 'class="event-divider"')


    @override_settings(GUESTBOOK_EYEBROW="", GUESTBOOK_THEME_COLOR_DARK="")
    def test_single_theme_color_without_dark_mode(self) -> None:
        response = self.get_index()

        self.assertNotContains(response, "prefers-color-scheme")

    @override_settings(
        GUESTBOOK_EYEBROW="",
        GUESTBOOK_THEME_COLOR_DARK="#2a1d22",
    )
    def test_dark_theme_color(self) -> None:
        response = self.get_index()

        self.assertContains(response, 'content="#2a1d22"')
        self.assertContains(
            response,
            'media="(prefers-color-scheme: dark)"',
        )
        self.assertContains(
            response,
            'media="(prefers-color-scheme: light)"',
        )


class OrnamentCheckTests(SimpleTestCase):
    @override_settings(GUESTBOOK_ORNAMENT="")
    def test_no_ornament_passes(self) -> None:
        self.assertEqual(check_ornament(), [])

    @override_settings(GUESTBOOK_ORNAMENT="bow")
    def test_bow_exists(self) -> None:
        self.assertEqual(check_ornament(), [])

    @override_settings(GUESTBOOK_ORNAMENT="does-not-exist")
    def test_missing_ornament_is_an_error(self) -> None:
        self.assertEqual(
            [error.id for error in check_ornament()],
            ["guestbook.E005"],
        )

    @override_settings(GUESTBOOK_ORNAMENT="../secrets")
    def test_invalid_ornament_name_is_an_error(self) -> None:
        self.assertEqual(
            [error.id for error in check_ornament()],
            ["guestbook.E004"],
        )


class ThemeCheckTests(SimpleTestCase):
    @override_settings(GUESTBOOK_THEME="white-party")
    def test_existing_theme_passes(self) -> None:
        self.assertEqual(check_theme(), [])

    @override_settings(GUESTBOOK_THEME="felicia-18")
    def test_felicia_theme_exists(self) -> None:
        self.assertEqual(check_theme(), [])

    @override_settings(GUESTBOOK_THEME="does-not-exist")
    def test_missing_theme_is_an_error(self) -> None:
        errors = check_theme()

        self.assertEqual(
            [error.id for error in errors],
            ["guestbook.E002"],
        )

    @override_settings(GUESTBOOK_THEME="../secrets")
    def test_invalid_theme_name_is_an_error(self) -> None:
        errors = check_theme()

        self.assertEqual(
            [error.id for error in errors],
            ["guestbook.E001"],
        )


class ScheduleCheckTests(SimpleTestCase):
    @override_settings(
        GUESTBOOK_STARTS_AT=None,
        GUESTBOOK_ENDS_AT=None,
    )
    def test_missing_dates_pass(self) -> None:
        self.assertEqual(check_schedule(), [])

    @override_settings(
        GUESTBOOK_STARTS_AT=datetime(2026, 10, 25, 2, 0, tzinfo=TZ),
        GUESTBOOK_ENDS_AT=datetime(2026, 10, 24, 18, 0, tzinfo=TZ),
    )
    def test_end_before_start_is_an_error(self) -> None:
        errors = check_schedule()

        self.assertEqual(
            [error.id for error in errors],
            ["guestbook.E003"],
        )
