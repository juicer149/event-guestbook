from django.contrib import admin
from django.db.models import Count, QuerySet

from .models import Post, PostImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0

    fields = (
        "image",
        "position",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "position",
        "id",
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_count",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        PostImageInline,
    ]

    def get_queryset(
        self,
        request,
    ) -> QuerySet[Post]:
        queryset = super().get_queryset(request)

        return queryset.annotate(
            admin_image_count=Count("images"),
        )

    @admin.display(
        description="Bilder",
        ordering="admin_image_count",
    )
    def image_count(
        self,
        post: Post,
    ) -> int:
        return post.admin_image_count
