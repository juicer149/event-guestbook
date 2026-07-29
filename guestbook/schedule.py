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
    """

    event_start: datetime
    event_end: datetime
    pre_duration: timedelta
    post_duration: timedelta

    def __post_init__(self) -> None:
        if not timezone.is_aware(self.event_start):
            raise ValueError(
                "event_start must be timezone-aware."
            )

        if not timezone.is_aware(self.event_end):
            raise ValueError(
                "event_end must be timezone-aware."
            )

        if self.event_end <= self.event_start:
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
    def pre_start(self) -> datetime:
        """
        Return when the PRE phase begins.
        """
        return self.event_start - self.pre_duration

    @property
    def post_end(self) -> datetime:
        """
        Return when the POST phase ends.
        """
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
        """

        if not timezone.is_aware(moment):
            raise ValueError(
                "moment must be timezone-aware."
            )

        if moment < self.pre_start:
            return GuestbookPhase.CLOSED

        if moment < self.event_start:
            return GuestbookPhase.PRE

        if moment < self.event_end:
            return GuestbookPhase.LIVE

        if moment < self.post_end:
            return GuestbookPhase.POST

        return GuestbookPhase.ARCHIVED
