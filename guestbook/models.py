from django.db import models


class Post(models.Model):
    """
    Represent one upload action.

    A post groups the images that were uploaded together. The group
    does not need to be visible in the public photo feed.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"Post {self.pk}"


class PostImage(models.Model):
    """
    Represent one image in the shared event feed.

    The original image is the permanent source of truth. The
    thumbnail is a derived asset that may be regenerated from the
    original.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="guestbook/originals/%Y/%m/%d/",
    )

    thumbnail = models.ImageField(
        upload_to="guestbook/thumbnails/%Y/%m/%d/",
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = [
            "-created_at",
            "-id",
        ]

    def __str__(self) -> str:
        return self.image.name
