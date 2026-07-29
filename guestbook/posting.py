from collections.abc import Iterable

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from .models import Post, PostImage


def create_post(
    images: Iterable[UploadedFile],
) -> Post:
    """
    Create one post containing the supplied images.

    The images are stored in their iterable order. Database rows are
    created inside one transaction so that Post and PostImage records
    are committed or rolled back together.

    The storage backend itself is not part of the database
    transaction. Files already written to local or object storage
    cannot automatically be rolled back by the database.
    """
    image_list = list(images)

    if not image_list:
        raise ValueError(
            "A post must contain at least one image."
        )

    with transaction.atomic():
        post = Post.objects.create()

        for position, image in enumerate(image_list):
            PostImage.objects.create(
                post=post,
                image=image,
                position=position,
            )

    return post
