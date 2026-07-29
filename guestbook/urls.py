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
        "join/<str:access_key>/",
        views.join,
        name="join",
    ),
    path(
        "upload/",
        views.upload_photos,
        name="upload_photos",
    ),
]
