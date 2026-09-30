"""Fill the local guestbook with generated demo photos.

The images are created with Pillow and uploaded through the same
create_post() path as real guest uploads, so originals, thumbnails and
upload groups are produced exactly as in production.
"""

from io import BytesIO
from random import Random

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw, ImageFont

from guestbook.models import Post
from guestbook.posting import create_post


# Portrait, landscape and square, so the masonry feed looks realistic.
SIZES = (
    (1200, 1600),
    (1600, 1200),
    (1400, 1400),
    (1080, 1920),
)

# Warm evening colours that suit a white party theme.
PALETTE = (
    ((244, 236, 220), (201, 164, 108)),
    ((236, 226, 214), (140, 110, 90)),
    ((250, 244, 235), (214, 186, 150)),
    ((228, 220, 206), (96, 84, 72)),
    ((245, 232, 225), (190, 130, 120)),
    ((232, 238, 236), (120, 150, 140)),
)


class Command(BaseCommand):
    help = "Create generated demo photos in the local guestbook."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--count",
            type=int,
            default=24,
            help="Number of demo photos to create (default: 24).",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=30,
            help="Random seed, so the demo looks the same every time.",
        )

    def handle(self, *args, **options) -> None:
        if not settings.DEBUG:
            raise CommandError(
                "Refusing to create demo data when DEBUG is False."
            )

        count = options["count"]

        if count < 1:
            raise CommandError("--count must be at least 1.")

        rng = Random(options["seed"])
        created = 0
        posts = 0

        while created < count:
            # Guests often upload a few photos at once.
            group_size = min(rng.randint(1, 4), count - created)

            images = [
                _demo_image(
                    number=created + index + 1,
                    rng=rng,
                )
                for index in range(group_size)
            ]

            create_post(images)

            created += group_size
            posts += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created} demo photos in {posts} uploads "
                f"({Post.objects.count()} uploads in total)."
            )
        )

        access_key = settings.GUESTBOOK_ACCESS_KEY

        if access_key:
            self.stdout.write(
                f"Open: http://127.0.0.1:8000/join/{access_key}/"
            )


def _demo_image(
    *,
    number: int,
    rng: Random,
) -> SimpleUploadedFile:
    width, height = rng.choice(SIZES)
    light, dark = rng.choice(PALETTE)

    image = Image.new("RGB", (width, height), light)
    draw = ImageDraw.Draw(image)

    # Vertical gradient from the light to the dark colour.
    for y in range(height):
        ratio = y / (height - 1)
        colour = tuple(
            round(a + (b - a) * ratio)
            for a, b in zip(light, dark)
        )
        draw.line([(0, y), (width, y)], fill=colour)

    # A few translucent circles, like out-of-focus party lights.
    lights = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    lights_draw = ImageDraw.Draw(lights)

    for _ in range(rng.randint(4, 9)):
        radius = rng.randint(width // 20, width // 7)
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        lights_draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(255, 255, 255, rng.randint(50, 110)),
        )

    image = Image.alpha_composite(
        image.convert("RGBA"),
        lights,
    ).convert("RGB")
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default(size=width // 6)
    label = f"#{number}"
    box = draw.textbbox((0, 0), label, font=font)
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]

    draw.text(
        ((width - text_width) / 2, (height - text_height) / 2),
        label,
        font=font,
        fill=(255, 255, 255),
        stroke_width=max(2, width // 300),
        stroke_fill=dark,
    )

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=85)

    return SimpleUploadedFile(
        name=f"demo-{number:03d}.jpg",
        content=buffer.getvalue(),
        content_type="image/jpeg",
    )
