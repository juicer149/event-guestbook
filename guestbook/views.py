from secrets import compare_digest

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .access import (
    grant_guest_access,
    guest_access_required,
    has_guest_access,
)
from .forms import EntryForm
from .models import Entry
from .phases import (
    current_phase,
    guestbook_accepts_entries,
    guestbook_accepts_join,
    guestbook_is_available,
)


def index(request: HttpRequest) -> HttpResponse:
    if not guestbook_is_available():
        raise Http404

    if not has_guest_access(request):
        raise Http404

    entries = (
        Entry.objects
        .prefetch_related("images")
        .order_by("-created_at")
    )

    context = {
        "title": settings.GUESTBOOK_TITLE,
        "entries": entries,
        "phase": current_phase(),
        "can_create_entry": (
            guestbook_accepts_entries()
            and has_guest_access(request)
        ),
    }

    return render(
        request,
        "guestbook/index.html",
        context,
    )


def join(
    request: HttpRequest,
    access_key: str,
) -> HttpResponse:
    if not guestbook_accepts_join():
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

    return redirect("guestbook:index")


@guest_access_required
def create_entry(
    request: HttpRequest,
) -> HttpResponse:
    if not guestbook_is_available():
        raise Http404

    if not guestbook_accepts_entries():
        raise Http404

    if request.method == "POST":
        form = EntryForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "guestbook:index",
            )
    else:
        form = EntryForm()

    context = {
        "title": settings.GUESTBOOK_TITLE,
        "form": form,
        "phase": current_phase(),
    }

    return render(
        request,
        "guestbook/create_entry.html",
        context,
    )
