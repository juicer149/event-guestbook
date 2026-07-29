from datetime import timedelta

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase, override_settings

from guestbook.access import (
    SESSION_GUEST_ACCESS_KEY,
    grant_guest_access,
    has_guest_access,
    revoke_guest_access,
)


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

    def test_access_is_stored_as_boolean_true(self) -> None:
        grant_guest_access(self.request)

        self.assertIs(
            self.request.session[
                SESSION_GUEST_ACCESS_KEY
            ],
            True,
        )

    def test_access_uses_configured_duration(self) -> None:
        grant_guest_access(self.request)

        expiry_age = (
            self.request.session.get_expiry_age()
        )

        expected_age = int(
            settings
            .GUESTBOOK_GUEST_ACCESS_DURATION
            .total_seconds()
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

    def test_revoke_is_safe_without_existing_access(
        self,
    ) -> None:
        revoke_guest_access(self.request)

        self.assertFalse(
            has_guest_access(self.request),
        )

    def test_truthy_string_does_not_grant_access(
        self,
    ) -> None:
        self.request.session[
            SESSION_GUEST_ACCESS_KEY
        ] = "true"

        self.assertFalse(
            has_guest_access(self.request),
        )

    def test_truthy_integer_does_not_grant_access(
        self,
    ) -> None:
        self.request.session[
            SESSION_GUEST_ACCESS_KEY
        ] = 1

        self.assertFalse(
            has_guest_access(self.request),
        )

    def test_false_boolean_does_not_grant_access(
        self,
    ) -> None:
        self.request.session[
            SESSION_GUEST_ACCESS_KEY
        ] = False

        self.assertFalse(
            has_guest_access(self.request),
        )
