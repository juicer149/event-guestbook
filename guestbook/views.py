from secrets import compare_digest

from django.conf import settings
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import redirect, render
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
)

from .access import (
    grant_guest_access,
    guest_access_required,
    has_guest_access,
)
from .forms import (
    DEFAULT_MAX_IMAGE_BYTES,
    DEFAULT_MAX_IMAGES,
    PostUploadForm,
)
from .lifecycle import current_guestbook_state
from .models import PostImage
from .posting import create_post


@require_GET
def index(
    request: HttpRequest,
) -> HttpResponse:
    """
    Render the shared event photo feed.

    The lifecycle configuration decides whether the guestbook and
    feed are available. Guest access is checked independently through
    the browser session.
    """
    state = current_guestbook_state()

    if not state.configuration.is_accessible:
        raise Http404

    if not has_guest_access(request):
        raise Http404

    if state.configuration.show_feed:
        images = PostImage.objects.all()
    else:
        images = PostImage.objects.none()

    context = {
        "title": settings.GUESTBOOK_TITLE,
        "phase": state.phase.value,
        "configuration": state.configuration,
        "images": images,
        "image_count": images.count(),
    }

    return render(
        request,
        "guestbook/index.html",
        context,
    )


@require_GET
def join(
    request: HttpRequest,
    access_key: str,
) -> HttpResponse:
    """
    Grant guest access when the event and shared key allow it.

    A successful join stores guest access in the Django session and
    redirects to the photo feed.
    """
    state = current_guestbook_state()

    if not state.configuration.allow_join:
        raise Http404

    configured_key = settings.GUESTBOOK_ACCESS_KEY

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


@require_http_methods(
    [
        "GET",
        "POST",
    ]
)
@guest_access_required
def upload_photos(
    request: HttpRequest,
) -> HttpResponse:
    """
    Render and process one multi-image upload action.

    The current phase controls whether uploads, multiple selection,
    and camera capture are available. The form validates the files,
    while create_post performs the application use case.
    """
    state = current_guestbook_state()
    configuration = state.configuration

    if not configuration.is_accessible:
        raise Http404

    if not configuration.allow_uploads:
        raise Http404

    form_options = {
        "allow_multiple_images": (
            configuration.allow_multiple_images
        ),
        "max_images": getattr(
            settings,
            "GUESTBOOK_MAX_IMAGES_PER_POST",
            DEFAULT_MAX_IMAGES,
        ),
        "max_image_bytes": getattr(
            settings,
            "GUESTBOOK_MAX_IMAGE_BYTES",
            DEFAULT_MAX_IMAGE_BYTES,
        ),
    }

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
        "phase": state.phase.value,
        "configuration": configuration,
        "form": form,
        "max_images": form_options["max_images"],
    }

    return render(
        request,
        "guestbook/upload_photos.html",
        context,
    )
