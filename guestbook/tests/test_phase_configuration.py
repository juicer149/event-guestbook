from django.test import SimpleTestCase

from guestbook.phase_configuration import (
    PHASE_CONFIGURATIONS,
    PhaseConfiguration,
    configuration_for,
)
from guestbook.phases import GuestbookPhase


class PhaseConfigurationTests(SimpleTestCase):
    def test_every_phase_has_configuration(self) -> None:
        self.assertEqual(
            set(PHASE_CONFIGURATIONS),
            set(GuestbookPhase),
        )

    def test_closed_is_inaccessible(self) -> None:
        configuration = configuration_for(
            GuestbookPhase.CLOSED,
        )

        self.assertFalse(
            configuration.is_accessible,
        )
        self.assertFalse(
            configuration.allow_uploads,
        )
        self.assertFalse(
            configuration.show_feed,
        )

    def test_pre_is_accessible_without_feed_or_uploads(
        self,
    ) -> None:
        configuration = configuration_for(
            GuestbookPhase.PRE,
        )

        self.assertTrue(
            configuration.is_accessible,
        )
        self.assertTrue(
            configuration.allow_join,
        )
        self.assertFalse(
            configuration.allow_uploads,
        )
        self.assertFalse(
            configuration.show_feed,
        )

    def test_live_enables_camera_uploads_and_feed(
        self,
    ) -> None:
        configuration = configuration_for(
            GuestbookPhase.LIVE,
        )

        self.assertTrue(
            configuration.allow_uploads,
        )
        self.assertTrue(
            configuration.allow_camera_capture,
        )
        self.assertTrue(
            configuration.allow_multiple_images,
        )
        self.assertTrue(
            configuration.show_feed,
        )

    def test_post_disables_camera_but_keeps_uploads(
        self,
    ) -> None:
        configuration = configuration_for(
            GuestbookPhase.POST,
        )

        self.assertTrue(
            configuration.allow_uploads,
        )
        self.assertFalse(
            configuration.allow_camera_capture,
        )
        self.assertTrue(
            configuration.allow_multiple_images,
        )
        self.assertTrue(
            configuration.show_feed,
        )

    def test_archived_is_read_only(self) -> None:
        configuration = configuration_for(
            GuestbookPhase.ARCHIVED,
        )

        self.assertTrue(
            configuration.is_accessible,
        )
        self.assertFalse(
            configuration.allow_uploads,
        )
        self.assertTrue(
            configuration.show_feed,
        )

    def test_camera_requires_uploads(self) -> None:
        with self.assertRaises(ValueError):
            PhaseConfiguration(
                is_accessible=True,
                allow_join=True,
                allow_uploads=False,
                allow_camera_capture=True,
                allow_multiple_images=False,
                show_feed=True,
            )

    def test_multiple_images_require_uploads(self) -> None:
        with self.assertRaises(ValueError):
            PhaseConfiguration(
                is_accessible=True,
                allow_join=True,
                allow_uploads=False,
                allow_camera_capture=False,
                allow_multiple_images=True,
                show_feed=True,
            )
