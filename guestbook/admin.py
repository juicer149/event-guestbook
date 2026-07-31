from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Post, PostImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0
    fields = [
        "image",
        "thumbnail",
        "created_at",
    ]
    readonly_fields = [
        "thumbnail",
        "created_at",
    ]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"

    list_display = [
        "id",
        "created_at",
        "image_count",
    ]

    inlines = [
        PostImageInline,
    ]

    def get_queryset(
        self,
        request: HttpRequest,
    ) -> QuerySet[Post]:
        return (
            super()
            .get_queryset(request)
            .annotate(
                _image_count=Count("images"),
            )
        )

    @admin.display(
        description="Images",
        ordering="_image_count",
    )
    def image_count(
        self,
        post: Post,
    ) -> int:
        return post._image_count


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"

    list_display = [
        "id",
        "post",
        "created_at",
        "has_thumbnail",
    ]

    list_select_related = [
        "post",
    ]

    @admin.display(
        boolean=True,
        description="Thumbnail",
    )
    def has_thumbnail(
        self,
        image: PostImage,
    ) -> bool:
        return bool(image.thumbnail)
