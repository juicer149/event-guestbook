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
    """
    Return the phase selected through GUESTBOOK_DEV_PHASE.

    Development overrides are ignored when DEBUG is false.
    """
    if not settings.DEBUG:
        return None

    value = os.environ.get(
        "GUESTBOOK_DEV_PHASE",
        "",
    ).strip().lower()

    if not value:
        return None

    try:
        return GuestbookPhase(value)
    except ValueError:
        return None


def current_phase() -> GuestbookPhase:
    """
    Return the guestbook's current high-level phase.

    PRE:
        The event has not started.

    LIVE:
        Approved guests may create entries.

    POST:
        The guestbook remains readable but no new entries may be made.

    CLOSED:
        Public guestbook access has ended.
    """
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


def guestbook_accepts_join() -> bool:
    """
    Return whether the shared QR access key may be redeemed.
    """
    override = development_phase_override()

    if override is not None:
        return override in {
            GuestbookPhase.PRE,
            GuestbookPhase.LIVE,
            GuestbookPhase.POST,
        }

    now = timezone.now()

    return (
        settings.GUESTBOOK_JOIN_OPENS_AT
        <= now
        < settings.GUESTBOOK_JOIN_CLOSES_AT
    )


def guestbook_accepts_entries() -> bool:
    """
    Return whether approved guests may create entries.
    """
    override = development_phase_override()

    if override is not None:
        return override is GuestbookPhase.LIVE

    now = timezone.now()

    return (
        settings.GUESTBOOK_STARTS_AT
        <= now
        < settings.GUESTBOOK_ENTRIES_CLOSE_AT
    )


def guestbook_is_available() -> bool:
    """
    Return whether approved guests may view the guestbook.
    """
    override = development_phase_override()

    if override is not None:
        return override is not GuestbookPhase.CLOSED

    return timezone.now() < settings.GUESTBOOK_CLOSES_AT
