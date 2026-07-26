from django.db import models


class Entry(models.Model):
    author_name = models.CharField(max_length=120)

    message = models.CharField(
        max_length=500,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.author_name


class EntryImage(models.Model):
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="guestbook/%Y/%m/%d/",
    )

    position = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = [
            "position",
            "id",
        ]

    def __str__(self) -> str:
        return self.image.name
