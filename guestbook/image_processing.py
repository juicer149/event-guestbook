from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO
from uuid import uuid4

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


THUMBNAIL_MAX_SIZE = (800, 800)
THUMBNAIL_QUALITY = 78

ORIGINAL_QUALITY = 92
ORIGINAL_BACKGROUND = (255, 255, 255)


@dataclass(frozen=True, slots=True)
class ProcessedImage:
    """
    Contain the derived asset created from one original image.
    """

    thumbnail: ContentFile


def normalize_original(
    image_file: BinaryIO,
) -> ContentFile:
    """
    Re-encode an uploaded original as a JPEG without metadata.

    Guests can open and download originals, and phone photos often
    carry the GPS position where they were taken. The upload is
    therefore never stored as-is.

    EXIF orientation is applied to the pixels, and the pixels are
    copied into a new image, so no EXIF, XMP or other metadata is
    carried over. Transparency is flattened onto white. The ICC
    color profile is kept for RGB sources so colors stay correct.

    The supplied file is rewound before returning.
    """
    image_file.seek(0)

    with Image.open(image_file) as source:
        icc_profile = (
            source.info.get("icc_profile")
            if source.mode in {"RGB", "RGBA"}
            else None
        )

        oriented = ImageOps.exif_transpose(source)

        clean = _flatten_to_clean_rgb(
            oriented,
        )

    save_options: dict[str, object] = {
        "format": "JPEG",
        "quality": ORIGINAL_QUALITY,
        "optimize": True,
    }

    if icc_profile:
        save_options["icc_profile"] = icc_profile

    output = BytesIO()

    clean.save(
        output,
        **save_options,
    )

    image_file.seek(0)

    return ContentFile(
        output.getvalue(),
        name=f"{uuid4().hex}.jpg",
    )


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


def _flatten_to_clean_rgb(
    image: Image.Image,
) -> Image.Image:
    """
    Copy the pixels into a new RGB image without any metadata.

    A new image starts with an empty info dictionary, so nothing
    from the source (EXIF, XMP, comments) can follow along when
    the image is saved.
    """
    rgba = image.convert("RGBA")

    clean = Image.new(
        "RGB",
        rgba.size,
        ORIGINAL_BACKGROUND,
    )

    clean.paste(
        rgba,
        mask=rgba.getchannel("A"),
    )

    return clean
