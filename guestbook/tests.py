from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import (
    RequestFactory,
    SimpleTestCase,
    TestCase,
    override_settings,
)
from django.urls import reverse

from .access import (
    SESSION_GUEST_ACCESS_KEY,
    grant_guest_access,
    has_guest_access,
    revoke_guest_access,
)
from .phases import (
    GuestbookPhase,
    current_phase,
    guestbook_accepts_entries,
    guestbook_accepts_join,
    guestbook_is_available,
)


TZ = ZoneInfo("Europe/Stockholm")

STARTS_AT = datetime(
    2026,
    8,
    1,
    18,
    0,
    tzinfo=TZ,
)

ENDS_AT = datetime(
    2026,
    8,
    2,
    2,
    0,
    tzinfo=TZ,
)

JOIN_OPENS_AT = STARTS_AT - timedelta(hours=6)
JOIN_CLOSES_AT = ENDS_AT + timedelta(hours=12)
ENTRIES_CLOSE_AT = ENDS_AT + timedelta(days=1)
CLOSES_AT = ENDS_AT + timedelta(days=7)


@override_settings(
    GUESTBOOK_GUEST_ACCESS_DURATION=timedelta(days=7),
)
class GuestAccessTests(TestCase):
    def setUp(self) -> None:
        self.request = RequestFactory().get("/")

        middleware = SessionMiddleware(
            lambda request: None,
        )
        middleware.process_request(self.request)
        self.request.session.save()

    def test_guest_has_no_access_initially(self) -> None:
        self.assertFalse(
            has_guest_access(self.request),
        )

    def test_grant_guest_access(self) -> None:
        grant_guest_access(self.request)

        self.assertTrue(
            has_guest_access(self.request),
        )

    def test_access_is_stored_as_boolean(self) -> None:
        grant_guest_access(self.request)

        self.assertIs(
            self.request.session[
                SESSION_GUEST_ACCESS_KEY
            ],
            True,
        )

    def test_access_uses_configured_duration(self) -> None:
        grant_guest_access(self.request)

        expiry_age = self.request.session.get_expiry_age()

        expected_age = int(
            settings.GUESTBOOK_GUEST_ACCESS_DURATION.total_seconds()
        )

        self.assertLessEqual(
            abs(expiry_age - expected_age),
            1,
        )

    def test_revoke_guest_access(self) -> None:
        grant_guest_access(self.request)
        revoke_guest_access(self.request)

        self.assertFalse(
            has_guest_access(self.request),
        )

    def test_truthy_string_does_not_grant_access(self) -> None:
        self.request.session[
            SESSION_GUEST_ACCESS_KEY
        ] = "true"

        self.assertFalse(
            has_guest_access(self.request),
        )


@override_settings(
    DEBUG=False,
    GUESTBOOK_STARTS_AT=STARTS_AT,
    GUESTBOOK_ENDS_AT=ENDS_AT,
    GUESTBOOK_JOIN_OPENS_AT=JOIN_OPENS_AT,
    GUESTBOOK_JOIN_CLOSES_AT=JOIN_CLOSES_AT,
    GUESTBOOK_ENTRIES_CLOSE_AT=ENTRIES_CLOSE_AT,
    GUESTBOOK_CLOSES_AT=CLOSES_AT,
)
class GuestbookPhaseTests(SimpleTestCase):
    def test_phase_is_pre_before_event(self) -> None:
        now = STARTS_AT - timedelta(seconds=1)

        with patch(
            "guestbook.phases.timezone.now",
            return_value=now,
        ):
            self.assertEqual(
                current_phase(),
                GuestbookPhase.PRE,
            )

    def test_phase_is_live_at_event_start(self) -> None:
        with patch(
            "guestbook.phases.timezone.now",
            return_value=STARTS_AT,
        ):
            self.assertEqual(
                current_phase(),
                GuestbookPhase.LIVE,
            )

    def test_phase_is_post_after_entries_close(self) -> None:
        with patch(
            "guestbook.phases.timezone.now",
            return_value=ENTRIES_CLOSE_AT,
        ):
            self.assertEqual(
                current_phase(),
                GuestbookPhase.POST,
            )

    def test_phase_is_closed_at_public_close(self) -> None:
        with patch(
            "guestbook.phases.timezone.now",
            return_value=CLOSES_AT,
        ):
            self.assertEqual(
                current_phase(),
                GuestbookPhase.CLOSED,
            )

    def test_join_is_closed_before_join_window(self) -> None:
        now = JOIN_OPENS_AT - timedelta(seconds=1)

        with patch(
            "guestbook.phases.timezone.now",
            return_value=now,
        ):
            self.assertFalse(
                guestbook_accepts_join(),
            )

    def test_join_opens_at_join_start(self) -> None:
        with patch(
            "guestbook.phases.timezone.now",
            return_value=JOIN_OPENS_AT,
        ):
            self.assertTrue(
                guestbook_accepts_join(),
            )

    def test_join_closes_at_join_end(self) -> None:
        with patch(
            "guestbook.phases.timezone.now",
            return_value=JOIN_CLOSES_AT,
        ):
            self.assertFalse(
                guestbook_accepts_join(),
            )

    def test_entries_open_at_event_start(self) -> None:
        with patch(
            "guestbook.phases.timezone.now",
            return_value=STARTS_AT,
        ):
            self.assertTrue(
                guestbook_accepts_entries(),
            )

    def test_entries_close_at_entry_deadline(self) -> None:
        with patch(
            "guestbook.phases.timezone.now",
            return_value=ENTRIES_CLOSE_AT,
        ):
            self.assertFalse(
                guestbook_accepts_entries(),
            )

    def test_guestbook_available_before_close(self) -> None:
        now = CLOSES_AT - timedelta(seconds=1)

        with patch(
            "guestbook.phases.timezone.now",
            return_value=now,
        ):
            self.assertTrue(
                guestbook_is_available(),
            )

    def test_guestbook_unavailable_at_close(self) -> None:
        with patch(
            "guestbook.phases.timezone.now",
            return_value=CLOSES_AT,
        ):
            self.assertFalse(
                guestbook_is_available(),
            )


@override_settings(
    GUESTBOOK_ACCESS_KEY="test-secret-key",
)
class GuestbookViewAccessTests(TestCase):
    def join_url(
        self,
        key: str = "test-secret-key",
    ) -> str:
        return reverse(
            "guestbook:join",
            kwargs={
                "access_key": key,
            },
        )

    def grant_access(self) -> None:
        with patch(
            "guestbook.views.guestbook_accepts_join",
            return_value=True,
        ):
            self.client.get(
                self.join_url(),
            )

    def test_index_requires_guest_access(self) -> None:
        with patch(
            "guestbook.views.guestbook_is_available",
            return_value=True,
        ):
            response = self.client.get(
                reverse("guestbook:index"),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_valid_join_key_grants_access(self) -> None:
        with patch(
            "guestbook.views.guestbook_accepts_join",
            return_value=True,
        ):
            response = self.client.get(
                self.join_url(),
            )

        self.assertRedirects(
            response,
            reverse("guestbook:index"),
            fetch_redirect_response=False,
        )

        self.assertIs(
            self.client.session[
                SESSION_GUEST_ACCESS_KEY
            ],
            True,
        )

    def test_invalid_join_key_returns_404(self) -> None:
        with patch(
            "guestbook.views.guestbook_accepts_join",
            return_value=True,
        ):
            response = self.client.get(
                self.join_url("wrong-key"),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_join_returns_404_outside_window(self) -> None:
        with patch(
            "guestbook.views.guestbook_accepts_join",
            return_value=False,
        ):
            response = self.client.get(
                self.join_url(),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_create_requires_guest_access(self) -> None:
        with patch(
            "guestbook.views.guestbook_is_available",
            return_value=True,
        ), patch(
            "guestbook.views.guestbook_accepts_entries",
            return_value=True,
        ):
            response = self.client.get(
                reverse("guestbook:create-entry"),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_approved_guest_can_view_index(self) -> None:
        self.grant_access()

        with patch(
            "guestbook.views.guestbook_is_available",
            return_value=True,
        ), patch(
            "guestbook.views.guestbook_accepts_entries",
            return_value=True,
        ):
            response = self.client.get(
                reverse("guestbook:index"),
            )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_approved_guest_cannot_view_closed_guestbook(
        self,
    ) -> None:
        self.grant_access()

        with patch(
            "guestbook.views.guestbook_is_available",
            return_value=False,
        ):
            response = self.client.get(
                reverse("guestbook:index"),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_approved_guest_cannot_create_after_deadline(
        self,
    ) -> None:
        self.grant_access()

        with patch(
            "guestbook.views.guestbook_is_available",
            return_value=True,
        ), patch(
            "guestbook.views.guestbook_accepts_entries",
            return_value=False,
        ):
            response = self.client.get(
                reverse("guestbook:create-entry"),
            )

        self.assertEqual(
            response.status_code,
            404,
        )
