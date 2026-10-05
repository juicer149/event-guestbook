"""
Friendly error pages for guests.

Django's default error pages are plain English text. Guests reach
these pages in ordinary situations during the party, for example by
opening the album in a different browser than the one that scanned
the QR code, so every page explains what to do next.
"""

from dataclasses import dataclass

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@dataclass(frozen=True, slots=True)
class ErrorPage:
    heading: str
    text: str
    link_to_album: bool


ERROR_PAGES = {
    400: ErrorPage(
        heading="Något gick snett",
        text=(
            "Uppladdningen gick inte igenom. "
            "Försök igen med färre bilder åt gången."
        ),
        link_to_album=True,
    ),
    403: ErrorPage(
        heading="Sidan hann gå ut",
        text=(
            "Gå tillbaka till albumet och försök igen. "
            "Fungerar det inte, skanna QR-koden på festen igen."
        ),
        link_to_album=True,
    ),
    404: ErrorPage(
        heading="Hittar inte sidan",
        text=(
            "Skanna QR-koden på festen för att komma in i albumet. "
            "Öppnade du länken i en annan app eller webbläsare, "
            "skanna koden igen därifrån."
        ),
        link_to_album=False,
    ),
    500: ErrorPage(
        heading="Något gick fel",
        text="Vänta en liten stund och försök igen.",
        link_to_album=True,
    ),
}


def render_error(
    request: HttpRequest,
    status: int,
) -> HttpResponse:
    """
    Render the error page for one status code.

    If the page itself cannot be rendered, a plain-text response is
    returned instead, so an error page never causes a second error.
    """
    page = ERROR_PAGES[status]

    try:
        return render(
            request,
            "guestbook/error.html",
            {
                "title": settings.GUESTBOOK_TITLE,
                "page": page,
            },
            status=status,
        )
    except Exception:
        return HttpResponse(
            f"{page.heading}. {page.text}",
            content_type="text/plain; charset=utf-8",
            status=status,
        )


def bad_request(
    request: HttpRequest,
    exception: Exception | None = None,
) -> HttpResponse:
    return render_error(request, 400)


def permission_denied(
    request: HttpRequest,
    exception: Exception | None = None,
) -> HttpResponse:
    return render_error(request, 403)


def csrf_failure(
    request: HttpRequest,
    reason: str = "",
) -> HttpResponse:
    return render_error(request, 403)


def page_not_found(
    request: HttpRequest,
    exception: Exception | None = None,
) -> HttpResponse:
    return render_error(request, 404)


def server_error(
    request: HttpRequest,
) -> HttpResponse:
    return render_error(request, 500)
