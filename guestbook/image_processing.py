from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO
from uuid import uuid4

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


THUMBNAIL_MAX_SIZE = (800, 800)
THUMBNAIL_QUALITY = 78


@dataclass(frozen=True, slots=True)
class ProcessedImage:
    """
    Contain the derived asset created from one original image.
    """

    thumbnail: ContentFile


def process_image(
    image_file: BinaryIO,
) -> ProcessedImage:
    """
    Create a WebP thumbnail while preserving the aspect ratio.

    EXIF orientation is applied before the thumbnail is generated.
    The supplied original file is rewound before returning.
    """
    image_file.seek(0)

    with Image.open(image_file) as source:
        oriented = ImageOps.exif_transpose(source)

        thumbnail = _prepare_for_webp(
            oriented.copy(),
        )

        thumbnail.thumbnail(
            THUMBNAIL_MAX_SIZE,
            Image.Resampling.LANCZOS,
        )

        output = BytesIO()

        thumbnail.save(
            output,
            format="WEBP",
            quality=THUMBNAIL_QUALITY,
            method=6,
        )

    image_file.seek(0)

    thumbnail_name = f"{uuid4().hex}.webp"

    return ProcessedImage(
        thumbnail=ContentFile(
            output.getvalue(),
            name=thumbnail_name,
        ),
    )


def _prepare_for_webp(
    image: Image.Image,
) -> Image.Image:
    """
    Convert unsupported image modes to RGB or RGBA.
    """
    if image.mode in {"RGB", "RGBA"}:
        return image

    if "transparency" in image.info:
        return image.convert("RGBA")

    return image.convert("RGB")
