from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from .phase_configuration import (
    PhaseConfiguration,
    configuration_for,
)
from .phases import GuestbookPhase
from .schedule import EventSchedule


@dataclass(frozen=True, slots=True)
class GuestbookState:
    """
    Represent one consistent snapshot of the guestbook lifecycle.

    The phase and its configuration are resolved together so that
    one request does not accidentally use different phase values.
    """

    phase: GuestbookPhase
    configuration: PhaseConfiguration


def configured_schedule() -> EventSchedule:
    """
    Build the event schedule from Django settings.

    This function is the adapter between Django's global settings
    and the pure EventSchedule domain object.
    """
    return EventSchedule(
        event_start=settings.GUESTBOOK_STARTS_AT,
        event_end=settings.GUESTBOOK_ENDS_AT,
        pre_duration=settings.GUESTBOOK_PRE_DURATION,
        post_duration=settings.GUESTBOOK_POST_DURATION,
    )


def development_phase_override() -> GuestbookPhase | None:
    """
    Return the configured development phase.

    The override is disabled outside DEBUG mode. An empty or invalid
    value is treated as no override.
    """
    if not settings.DEBUG:
        return None

    configured_phase = getattr(
        settings,
        "GUESTBOOK_DEV_PHASE",
        "",
    ).strip().lower()

    if not configured_phase:
        return None

    try:
        return GuestbookPhase(configured_phase)
    except ValueError:
        return None


def schedule_is_bypassed() -> bool:
    """
    Return whether the normal event schedule is bypassed.

    The bypass forces the application into the LIVE phase and is
    intended only as a temporary development or deployment switch.
    """
    return getattr(
        settings,
        "GUESTBOOK_BYPASS_SCHEDULE",
        False,
    )


def current_phase() -> GuestbookPhase:
    """
    Return the phase active at the current time.

    Resolution order:

    1. Explicit schedule bypass.
    2. Development phase override.
    3. EventSchedule evaluated against the current time.
    """
    if schedule_is_bypassed():
        return GuestbookPhase.LIVE

    override = development_phase_override()

    if override is not None:
        return override

    return configured_schedule().phase_at(
        timezone.now(),
    )


def current_guestbook_state() -> GuestbookState:
    """
    Resolve the current phase and its configuration.
    """
    phase = current_phase()

    return GuestbookState(
        phase=phase,
        configuration=configuration_for(phase),
    )
