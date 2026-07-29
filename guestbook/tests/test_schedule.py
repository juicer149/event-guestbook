from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase

from guestbook.phases import GuestbookPhase
from guestbook.schedule import EventSchedule


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

PRE_DURATION = timedelta(days=10)
POST_DURATION = timedelta(hours=24)


class EventScheduleTests(SimpleTestCase):
    def setUp(self) -> None:
        self.schedule = EventSchedule(
            event_start=EVENT_START,
            event_end=EVENT_END,
            pre_duration=PRE_DURATION,
            post_duration=POST_DURATION,
        )

    def test_pre_start_is_derived_from_event_start(self) -> None:
        self.assertEqual(
            self.schedule.pre_start,
            EVENT_START - PRE_DURATION,
        )

    def test_post_end_is_derived_from_event_end(self) -> None:
        self.assertEqual(
            self.schedule.post_end,
            EVENT_END + POST_DURATION,
        )

    def test_phase_is_closed_before_pre(self) -> None:
        moment = self.schedule.pre_start - timedelta(
            microseconds=1,
        )

        self.assertEqual(
            self.schedule.phase_at(moment),
            GuestbookPhase.CLOSED,
        )

    def test_phase_is_pre_at_pre_start(self) -> None:
        self.assertEqual(
            self.schedule.phase_at(
                self.schedule.pre_start,
            ),
            GuestbookPhase.PRE,
        )

    def test_phase_is_live_at_event_start(self) -> None:
        self.assertEqual(
            self.schedule.phase_at(EVENT_START),
            GuestbookPhase.LIVE,
        )

    def test_phase_is_post_at_event_end(self) -> None:
        self.assertEqual(
            self.schedule.phase_at(EVENT_END),
            GuestbookPhase.POST,
        )

    def test_phase_is_archived_at_post_end(self) -> None:
        self.assertEqual(
            self.schedule.phase_at(
                self.schedule.post_end,
            ),
            GuestbookPhase.ARCHIVED,
        )

    def test_rejects_end_before_start(self) -> None:
        with self.assertRaises(ValueError):
            EventSchedule(
                event_start=EVENT_START,
                event_end=EVENT_START,
                pre_duration=PRE_DURATION,
                post_duration=POST_DURATION,
            )

    def test_rejects_naive_datetimes(self) -> None:
        naive_start = EVENT_START.replace(
            tzinfo=None,
        )

        with self.assertRaises(ValueError):
            EventSchedule(
                event_start=naive_start,
                event_end=EVENT_END,
                pre_duration=PRE_DURATION,
                post_duration=POST_DURATION,
            )
