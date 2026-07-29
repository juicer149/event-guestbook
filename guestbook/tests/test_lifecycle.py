from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase, override_settings

from guestbook.lifecycle import (
    current_guestbook_state,
    current_phase,
)
from guestbook.phases import GuestbookPhase


TZ = ZoneInfo("Europe/Stockholm")

EVENT_START = datetime(
    2026,
    8,
    1,
    18,
    0,
    tzinfo=TZ,
)

EVENT_END = datetime(
    2026,
    8,
    2,
    2,
    0,
    tzinfo=TZ,
)


@override_settings(
    DEBUG=False,
    GUESTBOOK_BYPASS_SCHEDULE=False,
    GUESTBOOK_DEV_PHASE="",
    GUESTBOOK_STARTS_AT=EVENT_START,
    GUESTBOOK_ENDS_AT=EVENT_END,
    GUESTBOOK_PRE_DURATION=timedelta(days=10),
    GUESTBOOK_POST_DURATION=timedelta(hours=24),
)
class LifecycleTests(SimpleTestCase):
    def test_uses_schedule_for_current_phase(self) -> None:
        with patch(
            "guestbook.lifecycle.timezone.now",
            return_value=EVENT_START,
        ):
            self.assertEqual(
                current_phase(),
                GuestbookPhase.LIVE,
            )

    @override_settings(
        DEBUG=True,
        GUESTBOOK_DEV_PHASE="post",
    )
    def test_development_override(self) -> None:
        self.assertEqual(
            current_phase(),
            GuestbookPhase.POST,
        )

    @override_settings(
        DEBUG=False,
        GUESTBOOK_DEV_PHASE="post",
    )
    def test_override_is_ignored_outside_debug(self) -> None:
        with patch(
            "guestbook.lifecycle.timezone.now",
            return_value=EVENT_START,
        ):
            self.assertEqual(
                current_phase(),
                GuestbookPhase.LIVE,
            )

    @override_settings(
        GUESTBOOK_BYPASS_SCHEDULE=True,
    )
    def test_bypass_forces_live_phase(self) -> None:
        self.assertEqual(
            current_phase(),
            GuestbookPhase.LIVE,
        )

    def test_state_contains_matching_configuration(self) -> None:
        with patch(
            "guestbook.lifecycle.current_phase",
            return_value=GuestbookPhase.POST,
        ):
            state = current_guestbook_state()

        self.assertEqual(
            state.phase,
            GuestbookPhase.POST,
        )
        self.assertTrue(
            state.configuration.allow_uploads,
        )
        self.assertFalse(
            state.configuration.allow_camera_capture,
        )
