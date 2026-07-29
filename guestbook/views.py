from secrets import compare_digest
from typing import Any

from django.conf import settings
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import redirect, render
from django.views.decorators.http import (
    require_http_methods,
)

from .access import (
    grant_guest_access,
    guest_access_required,
    has_guest_access,
)
from .forms import PostUploadForm
from .lifecycle import (
    GuestbookState,
    current_guestbook_state,
)
from .models import Post
from .posting import create_post


def require_accessible_guestbook(
    state: GuestbookState,
) -> None:
    """
    Hide the guestbook when the current phase is inaccessible.
    """
    if not state.configuration.is_accessible:
        raise Http404


def require_uploads_allowed(
    state: GuestbookState,
) -> None:
    """
    Hide the upload endpoint when uploads are disabled.
    """
    require_accessible_guestbook(state)

    if not state.configuration.allow_uploads:
        raise Http404


def upload_form_options(
    state: GuestbookState,
) -> dict[str, Any]:
    """
    Build phase- and settings-dependent PostUploadForm options.
    """
    return {
        "allow_multiple_images": (
            state.configuration.allow_multiple_images
        ),
        "max_images": (
            settings.GUESTBOOK_MAX_IMAGES_PER_POST
        ),
        "max_image_bytes": (
            settings.GUESTBOOK_MAX_IMAGE_BYTES
        ),
    }


@require_http_methods(["GET"])
def index(
    request: HttpRequest,
) -> HttpResponse:
    """
    Render the current guestbook page.

    Posts are only queried when the active phase exposes the feed.
    """
    state = current_guestbook_state()

    require_accessible_guestbook(state)

    if not has_guest_access(request):
        raise Http404

    posts = Post.objects.none()

    if state.configuration.show_feed:
        posts = (
            Post.objects
            .prefetch_related("images")
            .order_by("-created_at")
        )

    context = {
        "title": settings.GUESTBOOK_TITLE,
        "posts": posts,
        "phase": state.phase,
        "configuration": state.configuration,
    }

    return render(
        request,
        "guestbook/index.html",
        context,
    )


@require_http_methods(["GET"])
def join(
    request: HttpRequest,
    access_key: str,
) -> HttpResponse:
    """
    Redeem the shared event access key for the current browser.

    A successful redemption stores guest access in the browser's
    Django session.
    """
    state = current_guestbook_state()

    require_accessible_guestbook(state)

    if not state.configuration.allow_join:
        raise Http404

    configured_key = (
        settings.GUESTBOOK_ACCESS_KEY
    )

    if not configured_key:
        raise Http404

    if not compare_digest(
        access_key,
        configured_key,
    ):
        raise Http404

    grant_guest_access(request)

    return redirect(
        "guestbook:index",
    )


@require_http_methods(["GET", "POST"])
@guest_access_required
def upload_photos(
    request: HttpRequest,
) -> HttpResponse:
    """
    Render and process the photo upload form.
    """
    state = current_guestbook_state()

    require_uploads_allowed(state)

    form_options = upload_form_options(
        state,
    )

    if request.method == "POST":
        form = PostUploadForm(
            request.POST,
            request.FILES,
            **form_options,
        )

        if form.is_valid():
            create_post(
                form.cleaned_data["images"],
            )

            return redirect(
                "guestbook:index",
            )
    else:
        form = PostUploadForm(
            **form_options,
        )

    context = {
        "title": settings.GUESTBOOK_TITLE,
        "form": form,
        "phase": state.phase,
        "configuration": state.configuration,
    }

    return render(
        request,
        "guestbook/upload_photos.html",
        context,
    )
