import os
from enum import StrEnum

from django.conf import settings
from django.utils import timezone


class GuestbookPhase(StrEnum):
    PRE = "pre"
    LIVE = "live"
    POST = "post"
    CLOSED = "closed"


def development_phase_override() -> GuestbookPhase | None:
    if not settings.DEBUG:
        return None

    phase_value = os.environ.get("GUESTBOOK_DEV_PHASE")

    if not phase_value:
        return None

    try:
        return GuestbookPhase(phase_value)
    except ValueError:
        raise ValueError(
            "GUESTBOOK_DEV_PHASE must be one of: "
            "pre, live, post, closed"
        ) from None


def current_phase() -> GuestbookPhase:
    override = development_phase_override()

    if override is not None:
        return override

    now = timezone.now()

    if now < settings.GUESTBOOK_STARTS_AT:
        return GuestbookPhase.PRE

    if now < settings.GUESTBOOK_ENDS_AT:
        return GuestbookPhase.LIVE

    if now < settings.GUESTBOOK_CLOSES_AT:
        return GuestbookPhase.POST

    return GuestbookPhase.CLOSED


def guestbook_accepts_entries() -> bool:
    return current_phase() in {
        GuestbookPhase.LIVE,
        GuestbookPhase.POST,
    }


def guestbook_accepts_join() -> bool:
    return current_phase() is not GuestbookPhase.CLOSED
