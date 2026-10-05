from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
        name="media",
    ),
    path(
        "",
        include("guestbook.urls"),
    ),
]


handler400 = "guestbook.errors.bad_request"
handler403 = "guestbook.errors.permission_denied"
handler404 = "guestbook.errors.page_not_found"
handler500 = "guestbook.errors.server_error"
