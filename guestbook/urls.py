from django.urls import path

from . import views


app_name = "guestbook"

urlpatterns = [
    path(
        "",
        views.index,
        name="index",
    ),
    path(
        "join/<str:key>/",
        views.join,
        name="join",
    ),
    path(
        "entries/new/",
        views.create_entry,
        name="create-entry",
    ),
]
