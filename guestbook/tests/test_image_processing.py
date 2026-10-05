from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import ExifTags, Image

from guestbook.image_processing import (
    normalize_original,
    process_image,
)


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


def make_jpeg_with_metadata(
    *,
    size: tuple[int, int] = (200, 100),
    orientation: int | None = None,
) -> SimpleUploadedFile:
    """
    Create a phone-like JPEG carrying a GPS position.
    """
    image = Image.new(
        mode="RGB",
        size=size,
        color="white",
    )

    exif = image.getexif()
    exif[ExifTags.Base.Make] = "TestPhone"
    exif[ExifTags.IFD.GPSInfo] = {
        ExifTags.GPS.GPSLatitudeRef: "N",
        ExifTags.GPS.GPSLatitude: (60.0, 53.0, 0.0),
        ExifTags.GPS.GPSLongitudeRef: "E",
        ExifTags.GPS.GPSLongitude: (16.0, 42.0, 0.0),
    }

    if orientation is not None:
        exif[ExifTags.Base.Orientation] = orientation

    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
        exif=exif,
    )

    return SimpleUploadedFile(
        name="IMG_4821.jpg",
        content=buffer.getvalue(),
        content_type="image/jpeg",
    )


class NormalizeOriginalTests(SimpleTestCase):
    def test_fixture_contains_gps(self) -> None:
        uploaded = make_jpeg_with_metadata()

        with Image.open(uploaded) as image:
            self.assertTrue(
                image.getexif().get_ifd(
                    ExifTags.IFD.GPSInfo,
                ),
            )

    def test_removes_gps_and_other_metadata(
        self,
    ) -> None:
        uploaded = make_jpeg_with_metadata()

        original = normalize_original(uploaded)

        with Image.open(original) as image:
            exif = image.getexif()

            self.assertFalse(
                exif.get_ifd(ExifTags.IFD.GPSInfo),
            )
            self.assertEqual(len(exif), 0)
            self.assertNotIn("exif", image.info)
            self.assertNotIn("xmp", image.info)

    def test_applies_exif_orientation_to_pixels(
        self,
    ) -> None:
        uploaded = make_jpeg_with_metadata(
            size=(200, 100),
            orientation=6,
        )

        original = normalize_original(uploaded)

        with Image.open(original) as image:
            self.assertEqual(
                image.size,
                (100, 200),
            )

    def test_output_is_jpeg_with_random_name(
        self,
    ) -> None:
        uploaded = make_jpeg_with_metadata()

        original = normalize_original(uploaded)

        self.assertTrue(
            original.name.endswith(".jpg"),
        )
        self.assertNotIn(
            "IMG_4821",
            original.name,
        )

        with Image.open(original) as image:
            self.assertEqual(image.format, "JPEG")

    def test_png_is_converted_to_jpeg(self) -> None:
        uploaded = make_uploaded_image(
            name="screenshot.png",
            mode="RGBA",
            image_format="PNG",
        )

        original = normalize_original(uploaded)

        with Image.open(original) as image:
            self.assertEqual(image.format, "JPEG")
            self.assertEqual(image.mode, "RGB")

    def test_transparency_is_flattened_onto_white(
        self,
    ) -> None:
        buffer = BytesIO()

        Image.new(
            mode="RGBA",
            size=(10, 10),
            color=(0, 0, 0, 0),
        ).save(
            buffer,
            format="PNG",
        )

        uploaded = SimpleUploadedFile(
            name="transparent.png",
            content=buffer.getvalue(),
            content_type="image/png",
        )

        original = normalize_original(uploaded)

        with Image.open(original) as image:
            red, green, blue = image.getpixel((5, 5))

            self.assertGreater(min(red, green, blue), 250)

    def test_uploaded_file_is_rewound(self) -> None:
        uploaded = make_jpeg_with_metadata()

        normalize_original(uploaded)

        self.assertEqual(
            uploaded.tell(),
            0,
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
