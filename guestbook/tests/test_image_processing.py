from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from guestbook.image_processing import process_image


def make_uploaded_image(
    *,
    name: str = "photo.jpg",
    size: tuple[int, int] = (1600, 1200),
    mode: str = "RGB",
    image_format: str = "JPEG",
) -> SimpleUploadedFile:
    buffer = BytesIO()

    Image.new(
        mode=mode,
        size=size,
        color="white",
    ).save(
        buffer,
        format=image_format,
    )

    return SimpleUploadedFile(
        name=name,
        content=buffer.getvalue(),
        content_type=f"image/{image_format.lower()}",
    )


class ProcessImageTests(SimpleTestCase):
    def test_creates_webp_thumbnail(self) -> None:
        uploaded = make_uploaded_image()

        processed = process_image(uploaded)

        self.assertTrue(
            processed.thumbnail.name.endswith(".webp"),
        )

        with Image.open(
            processed.thumbnail
        ) as thumbnail:
            self.assertEqual(
                thumbnail.format,
                "WEBP",
            )

    def test_landscape_thumbnail_preserves_ratio(
        self,
    ) -> None:
        uploaded = make_uploaded_image(
            size=(1600, 800),
        )

        processed = process_image(uploaded)

        with Image.open(
            processed.thumbnail
        ) as thumbnail:
            self.assertEqual(
                thumbnail.size,
                (800, 400),
            )

    def test_portrait_thumbnail_preserves_ratio(
        self,
    ) -> None:
        uploaded = make_uploaded_image(
            size=(800, 1600),
        )

        processed = process_image(uploaded)

        with Image.open(
            processed.thumbnail
        ) as thumbnail:
            self.assertEqual(
                thumbnail.size,
                (400, 800),
            )

    def test_small_image_is_not_upscaled(self) -> None:
        uploaded = make_uploaded_image(
            size=(400, 300),
        )

        processed = process_image(uploaded)

        with Image.open(
            processed.thumbnail
        ) as thumbnail:
            self.assertEqual(
                thumbnail.size,
                (400, 300),
            )

    def test_original_file_is_rewound(self) -> None:
        uploaded = make_uploaded_image()

        process_image(uploaded)

        self.assertEqual(
            uploaded.tell(),
            0,
        )
