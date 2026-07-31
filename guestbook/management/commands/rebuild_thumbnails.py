from django.core.management.base import BaseCommand

from guestbook.image_processing import process_image
from guestbook.models import PostImage


class Command(BaseCommand):
    help = (
        "Regenerate thumbnails from stored original images."
    )

    def add_arguments(
        self,
        parser,
    ) -> None:
        parser.add_argument(
            "--missing-only",
            action="store_true",
            help=(
                "Only process images that do not have a thumbnail."
            ),
        )

    def handle(
        self,
        *args,
        **options,
    ) -> None:
        images = PostImage.objects.order_by("pk")

        if options["missing_only"]:
            images = images.filter(
                thumbnail="",
            )

        rebuilt_count = 0
        failed_count = 0

        for post_image in images.iterator():
            try:
                self._rebuild_thumbnail(
                    post_image,
                )
            except Exception as error:
                failed_count += 1

                self.stderr.write(
                    self.style.ERROR(
                        (
                            f"PostImage {post_image.pk}: "
                            f"{error}"
                        )
                    )
                )
            else:
                rebuilt_count += 1

                self.stdout.write(
                    (
                        "Rebuilt thumbnail for "
                        f"PostImage {post_image.pk}"
                    )
                )

        summary = (
            f"Rebuilt: {rebuilt_count}, "
            f"failed: {failed_count}"
        )

        if failed_count:
            self.stderr.write(
                self.style.WARNING(summary)
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(summary)
            )

    @staticmethod
    def _rebuild_thumbnail(
        post_image: PostImage,
    ) -> None:
        old_thumbnail_name = (
            post_image.thumbnail.name
            if post_image.thumbnail
            else ""
        )

        with post_image.image.open("rb") as original:
            processed = process_image(original)

        post_image.thumbnail.save(
            processed.thumbnail.name,
            processed.thumbnail,
            save=False,
        )

        post_image.save(
            update_fields=[
                "thumbnail",
            ]
        )

        new_thumbnail_name = (
            post_image.thumbnail.name
        )

        if (
            old_thumbnail_name
            and old_thumbnail_name
            != new_thumbnail_name
        ):
            post_image.thumbnail.storage.delete(
                old_thumbnail_name,
            )
