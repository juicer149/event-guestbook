from dataclasses import dataclass
from datetime import datetime, timedelta

from django.utils import timezone

from .phases import GuestbookPhase


@dataclass(frozen=True, slots=True)
class EventSchedule:
    """
    Calculate the event phase for an explicit point in time.

    The schedule only knows when phases occur. It does not know
    which application features are enabled during those phases.

    Both boundaries are optional. A missing boundary removes the
    phases on that side of LIVE:

        no start, no end:  always LIVE
        start only:        CLOSED -> PRE -> LIVE, never closes
        end only:          LIVE -> POST -> ARCHIVED
        start and end:     CLOSED -> PRE -> LIVE -> POST -> ARCHIVED
    """

    event_start: datetime | None = None
    event_end: datetime | None = None
    pre_duration: timedelta = timedelta(0)
    post_duration: timedelta = timedelta(0)

    def __post_init__(self) -> None:
        if (
            self.event_start is not None
            and not timezone.is_aware(self.event_start)
        ):
            raise ValueError(
                "event_start must be timezone-aware."
            )

        if (
            self.event_end is not None
            and not timezone.is_aware(self.event_end)
        ):
            raise ValueError(
                "event_end must be timezone-aware."
            )

        if (
            self.event_start is not None
            and self.event_end is not None
            and self.event_end <= self.event_start
        ):
            raise ValueError(
                "event_end must be later than event_start."
            )

        if self.pre_duration < timedelta(0):
            raise ValueError(
                "pre_duration cannot be negative."
            )

        if self.post_duration < timedelta(0):
            raise ValueError(
                "post_duration cannot be negative."
            )

    @property
    def pre_start(self) -> datetime | None:
        """
        Return when the PRE phase begins, if the event has a start.
        """
        if self.event_start is None:
            return None

        return self.event_start - self.pre_duration

    @property
    def post_end(self) -> datetime | None:
        """
        Return when the POST phase ends, if the event has an end.
        """
        if self.event_end is None:
            return None

        return self.event_end + self.post_duration

    def phase_at(
        self,
        moment: datetime,
    ) -> GuestbookPhase:
        """
        Return the phase active at the given moment.

        Intervals are left-inclusive and right-exclusive:

            PRE:
                pre_start <= moment < event_start

            LIVE:
                event_start <= moment < event_end

            POST:
                event_end <= moment < post_end

        A missing boundary skips the phases on its side.
        """

        if not timezone.is_aware(moment):
            raise ValueError(
                "moment must be timezone-aware."
            )

        if self.event_start is not None:
            if moment < self.pre_start:
                return GuestbookPhase.CLOSED

            if moment < self.event_start:
                return GuestbookPhase.PRE

        if self.event_end is None:
            return GuestbookPhase.LIVE

        if moment < self.event_end:
            return GuestbookPhase.LIVE

        if moment < self.post_end:
            return GuestbookPhase.POST

        return GuestbookPhase.ARCHIVED
