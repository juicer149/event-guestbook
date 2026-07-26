from django.contrib import admin

from .models import Entry, EntryImage


class EntryImageInline(admin.TabularInline):
    model = EntryImage
    extra = 0


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = (
        "author_name",
        "created_at",
    )
    search_fields = (
        "author_name",
        "message",
    )
    inlines = [
        EntryImageInline,
    ]
