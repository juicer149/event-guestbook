from secrets import compare_digest

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .access import (
    create_access_required,
    grant_create_access,
    has_create_access,
)
from .forms import EntryForm
from .models import Entry
from .phases import (
    current_phase,
    guestbook_accepts_entries,
    guestbook_accepts_join,
)


def index(request: HttpRequest) -> HttpResponse:
    entries = Entry.objects.order_by("-created_at")

    context = {
        "title": settings.GUESTBOOK_TITLE,
        "phase": current_phase(),
        "entries": entries,
        "can_create_entry": (
            has_create_access(request)
            and guestbook_accepts_entries()
        ),
    }

    return render(
        request,
        "guestbook/index.html",
        context,
    )


def join(request: HttpRequest, key: str) -> HttpResponse:
    configured_key = settings.GUESTBOOK_ACCESS_KEY

    if not configured_key:
        raise Http404

    if not guestbook_accepts_join():
        raise Http404

    if not compare_digest(key, configured_key):
        raise Http404

    grant_create_access(request)

    return redirect("guestbook:index")


@create_access_required
@require_http_methods(["GET", "POST"])
def create_entry(request: HttpRequest) -> HttpResponse:
    if not guestbook_accepts_entries():
        raise Http404

    if request.method == "POST":
        form = EntryForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("guestbook:index")
    else:
        form = EntryForm()

    context = {
        "title": settings.GUESTBOOK_TITLE,
        "phase": current_phase(),
        "form": form,
    }

    return render(
        request,
        "guestbook/create_entry.html",
        context,
    )
