from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.db import transaction

from guestbook.models import Post, PostImage


class Command(BaseCommand):
    help = (
        "Delete all guestbook posts, images, thumbnails, "
        "and database records."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--confirm",
            action="store_true",
            help=(
                "Required to perform the destructive reset."
            ),
        )

    def handle(
        self,
        *args,
        **options,
    ) -> None:
        if not options["confirm"]:
            raise CommandError(
                "Refusing to reset without --confirm."
            )

        images = list(
            PostImage.objects.all()
        )

        deleted_originals = 0
        deleted_thumbnails = 0

        for image in images:
            if (
                image.thumbnail
                and image.thumbnail.name
            ):
                image.thumbnail.delete(
                    save=False,
                )
                deleted_thumbnails += 1

            if image.image and image.image.name:
                image.image.delete(
                    save=False,
                )
                deleted_originals += 1

        with transaction.atomic():
            deleted_rows, details = (
                Post.objects.all().delete()
            )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Deleted {deleted_rows} database rows, "
                    f"{deleted_originals} originals, and "
                    f"{deleted_thumbnails} thumbnails."
                )
            )
        )

        if details:
            self.stdout.write(
                str(details)
            )
