from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from .phases import GuestbookPhase


@dataclass(frozen=True, slots=True)
class PhaseConfiguration:
    """
    Describe the capabilities enabled during one phase.

    Time does not belong here. The current phase is calculated
    separately by EventSchedule.
    """

    is_accessible: bool
    allow_join: bool
    allow_uploads: bool
    allow_camera_capture: bool
    allow_multiple_images: bool
    show_feed: bool

    def __post_init__(self) -> None:
        if not self.is_accessible:
            inaccessible_capabilities = (
                self.allow_join,
                self.allow_uploads,
                self.allow_camera_capture,
                self.allow_multiple_images,
                self.show_feed,
            )

            if any(inaccessible_capabilities):
                raise ValueError(
                    (
                        "An inaccessible phase cannot expose "
                        "guestbook capabilities."
                    )
                )

        if (
            self.allow_camera_capture
            and not self.allow_uploads
        ):
            raise ValueError(
                (
                    "Camera capture requires uploads "
                    "to be enabled."
                )
            )

        if (
            self.allow_multiple_images
            and not self.allow_uploads
        ):
            raise ValueError(
                (
                    "Multiple images require uploads "
                    "to be enabled."
                )
            )


PHASE_CONFIGURATIONS: Mapping[
    GuestbookPhase,
    PhaseConfiguration,
] = MappingProxyType(
    {
        GuestbookPhase.CLOSED: PhaseConfiguration(
            is_accessible=False,
            allow_join=False,
            allow_uploads=False,
            allow_camera_capture=False,
            allow_multiple_images=False,
            show_feed=False,
        ),
        GuestbookPhase.PRE: PhaseConfiguration(
            is_accessible=True,
            allow_join=True,
            allow_uploads=False,
            allow_camera_capture=False,
            allow_multiple_images=False,
            show_feed=False,
        ),
        GuestbookPhase.LIVE: PhaseConfiguration(
            is_accessible=True,
            allow_join=True,
            allow_uploads=True,
            allow_camera_capture=True,
            allow_multiple_images=True,
            show_feed=True,
        ),
        GuestbookPhase.POST: PhaseConfiguration(
            is_accessible=True,
            allow_join=True,
            allow_uploads=True,
            allow_camera_capture=False,
            allow_multiple_images=True,
            show_feed=True,
        ),
        GuestbookPhase.ARCHIVED: PhaseConfiguration(
            is_accessible=True,
            allow_join=True,
            allow_uploads=False,
            allow_camera_capture=False,
            allow_multiple_images=False,
            show_feed=True,
        ),
    }
)


def configuration_for(
    phase: GuestbookPhase,
) -> PhaseConfiguration:
    """
    Return the configuration belonging to a phase.

    A missing phase is a programming error, so the dictionary's
    KeyError is intentionally allowed to propagate.
    """
    return PHASE_CONFIGURATIONS[phase]
