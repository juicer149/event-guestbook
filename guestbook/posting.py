from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from .image_processing import process_image
from .models import Post, PostImage


@dataclass(frozen=True, slots=True)
class StoredImageFile:
    """
    Describe one file that has already been written to storage.
    """

    storage: Any
    name: str


def create_post(
    images: Iterable[UploadedFile],
) -> Post:
    """
    Create one upload group containing the supplied images.

    Every image becomes an independent feed item. The Post remains as
    the technical grouping for one upload action.

    Database rows are transactional. File storage is not, so files
    written before a failure are removed explicitly.
    """
    uploaded_images = list(images)

    if not uploaded_images:
        raise ValueError(
            "A post must contain at least one image."
        )

    stored_files: list[StoredImageFile] = []

    try:
        with transaction.atomic():
            post = Post.objects.create()

            for uploaded_image in uploaded_images:
                post_image = _prepare_post_image(
                    post=post,
                    uploaded_image=uploaded_image,
                    stored_files=stored_files,
                )

                post_image.save()

    except Exception:
        _delete_stored_files(stored_files)
        raise

    return post


def _prepare_post_image(
    *,
    post: Post,
    uploaded_image: UploadedFile,
    stored_files: list[StoredImageFile],
) -> PostImage:
    """
    Store one original and thumbnail and return the unsaved model.
    """
    processed = process_image(
        uploaded_image,
    )

    post_image = PostImage(
        post=post,
    )

    post_image.image.save(
        uploaded_image.name,
        uploaded_image,
        save=False,
    )

    stored_files.append(
        StoredImageFile(
            storage=post_image.image.storage,
            name=post_image.image.name,
        )
    )

    post_image.thumbnail.save(
        processed.thumbnail.name,
        processed.thumbnail,
        save=False,
    )

    stored_files.append(
        StoredImageFile(
            storage=post_image.thumbnail.storage,
            name=post_image.thumbnail.name,
        )
    )

    return post_image


def _delete_stored_files(
    stored_files: Iterable[StoredImageFile],
) -> None:
    """
    Remove files written before a failed database transaction.
    """
    for stored_file in reversed(
        list(stored_files)
    ):
        stored_file.storage.delete(
            stored_file.name,
        )
