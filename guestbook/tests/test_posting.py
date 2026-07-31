from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from guestbook.models import Post, PostImage
from guestbook.posting import create_post


def make_uploaded_image(
    *,
    name: str,
    size: tuple[int, int] = (1600, 1200),
) -> SimpleUploadedFile:
    buffer = BytesIO()

    Image.new(
        mode="RGB",
        size=size,
        color="white",
    ).save(
        buffer,
        format="JPEG",
    )

    return SimpleUploadedFile(
        name=name,
        content=buffer.getvalue(),
        content_type="image/jpeg",
    )


class CreatePostTests(TestCase):
    def setUp(self) -> None:
        self.media_directory = TemporaryDirectory()
        self.addCleanup(
            self.media_directory.cleanup,
        )

        media_override = override_settings(
            MEDIA_ROOT=self.media_directory.name,
        )

        media_override.enable()
        self.addCleanup(
            media_override.disable,
        )

    def test_creates_one_post(self) -> None:
        uploaded = make_uploaded_image(
            name="party.jpg",
        )

        create_post([uploaded])

        self.assertEqual(
            Post.objects.count(),
            1,
        )

    def test_creates_one_image_per_uploaded_file(
        self,
    ) -> None:
        first = make_uploaded_image(
            name="first.jpg",
        )
        second = make_uploaded_image(
            name="second.jpg",
        )

        post = create_post(
            [
                first,
                second,
            ]
        )

        self.assertEqual(
            post.images.count(),
            2,
        )

    def test_creates_original_file(self) -> None:
        uploaded = make_uploaded_image(
            name="party.jpg",
        )

        post = create_post([uploaded])
        post_image = post.images.get()

        self.assertTrue(
            Path(post_image.image.path).exists(),
        )

    def test_creates_thumbnail_file(self) -> None:
        uploaded = make_uploaded_image(
            name="party.jpg",
        )

        post = create_post([uploaded])
        post_image = post.images.get()

        self.assertTrue(
            Path(post_image.thumbnail.path).exists(),
        )

    def test_original_uses_original_directory(
        self,
    ) -> None:
        uploaded = make_uploaded_image(
            name="party.jpg",
        )

        post = create_post([uploaded])
        post_image = post.images.get()

        self.assertIn(
            "guestbook/originals/",
            post_image.image.name,
        )

    def test_thumbnail_uses_thumbnail_directory(
        self,
    ) -> None:
        uploaded = make_uploaded_image(
            name="party.jpg",
        )

        post = create_post([uploaded])
        post_image = post.images.get()

        self.assertIn(
            "guestbook/thumbnails/",
            post_image.thumbnail.name,
        )

    def test_thumbnail_has_expected_maximum_size(
        self,
    ) -> None:
        uploaded = make_uploaded_image(
            name="party.jpg",
            size=(2400, 1600),
        )

        post = create_post([uploaded])
        post_image = post.images.get()

        with Image.open(
            post_image.thumbnail.path
        ) as thumbnail:
            self.assertEqual(
                thumbnail.size,
                (800, 533),
            )

    def test_rejects_empty_image_collection(
        self,
    ) -> None:
        with self.assertRaisesMessage(
            ValueError,
            "A post must contain at least one image.",
        ):
            create_post([])

    def test_images_do_not_have_position_field(
        self,
    ) -> None:
        field_names = {
            field.name
            for field in PostImage._meta.fields
        }

        self.assertNotIn(
            "position",
            field_names,
        )
