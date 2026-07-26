from django.conf import settings
from django.shortcuts import render

from .phases import current_phase


def index(request):
    context = {
        "title": settings.GUESTBOOK_TITLE,
        "phase": current_phase(),
    }

    return render(
        request,
        "guestbook/index.html",
        context,
    )
