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

    configured_phase = getattr(
        settings,
        "GUESTBOOK_DEV_PHASE",
        "",
    ).strip().lower()

    try:
        return GuestbookPhase(configured_phase)
    except ValueError:
        return None


def schedule_is_bypassed() -> bool:
    return getattr(
        settings,
        "GUESTBOOK_BYPASS_SCHEDULE",
        False,
    )


def current_phase() -> GuestbookPhase:
    if schedule_is_bypassed():
        return GuestbookPhase.LIVE

    override = development_phase_override()

    if override is not None:
        return override

    now = timezone.now()

    if now < settings.GUESTBOOK_STARTS_AT:
        return GuestbookPhase.PRE

    if now < settings.GUESTBOOK_ENTRIES_CLOSE_AT:
        return GuestbookPhase.LIVE

    if now < settings.GUESTBOOK_CLOSES_AT:
        return GuestbookPhase.POST

    return GuestbookPhase.CLOSED


def guestbook_is_available() -> bool:
    if schedule_is_bypassed():
        return True

    return current_phase() != GuestbookPhase.CLOSED


def guestbook_accepts_join() -> bool:
    if schedule_is_bypassed():
        return True

    override = development_phase_override()

    if override is not None:
        return override != GuestbookPhase.CLOSED

    now = timezone.now()

    return (
        settings.GUESTBOOK_JOIN_OPENS_AT
        <= now
        < settings.GUESTBOOK_JOIN_CLOSES_AT
    )


def guestbook_accepts_entries() -> bool:
    if schedule_is_bypassed():
        return True

    return current_phase() == GuestbookPhase.LIVE
