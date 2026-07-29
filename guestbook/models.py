from django.db import models


class Post(models.Model):
    """
    Represent one upload action.

    A post contains one or more images selected and uploaded
    together by a guest.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Post {self.pk}"


class PostImage(models.Model):
    """
    Represent one image belonging to a post.

    Position preserves the order in which the guest selected
    the images.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="guestbook/%Y/%m/%d/",
    )

    position = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "position",
            "id",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "post",
                    "position",
                ],
                name="unique_post_image_position",
            ),
        ]

    def __str__(self) -> str:
        return self.image.name
