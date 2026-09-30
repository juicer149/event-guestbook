from io import StringIO
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from guestbook.models import Post, PostImage


class SeedDemoCommandTests(TestCase):
    def setUp(self) -> None:
        self.media_directory = TemporaryDirectory()
        self.addCleanup(
            self.media_directory.cleanup,
        )

        media_override = override_settings(
            MEDIA_ROOT=self.media_directory.name,
            DEBUG=True,
        )

        media_override.enable()
        self.addCleanup(
            media_override.disable,
        )

    def test_creates_requested_number_of_images(self) -> None:
        call_command(
            "seed_demo",
            count=7,
            stdout=StringIO(),
        )

        self.assertEqual(
            PostImage.objects.count(),
            7,
        )

    def test_groups_images_into_uploads(self) -> None:
        call_command(
            "seed_demo",
            count=12,
            stdout=StringIO(),
        )

        self.assertGreaterEqual(
            Post.objects.count(),
            3,
        )
        self.assertLessEqual(
            Post.objects.count(),
            12,
        )

    def test_every_image_has_a_thumbnail(self) -> None:
        call_command(
            "seed_demo",
            count=3,
            stdout=StringIO(),
        )

        for image in PostImage.objects.all():
            self.assertTrue(
                image.thumbnail.name.endswith(".webp"),
            )

    @override_settings(DEBUG=False)
    def test_refuses_to_run_without_debug(self) -> None:
        with self.assertRaises(CommandError):
            call_command(
                "seed_demo",
                count=1,
                stdout=StringIO(),
            )

        self.assertEqual(
            PostImage.objects.count(),
            0,
        )
