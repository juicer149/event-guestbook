from collections.abc import Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse


SESSION_GUEST_ACCESS_KEY = "guestbook_guest_access"

P = ParamSpec("P")
R = TypeVar("R", bound=HttpResponse)

View = Callable[Concatenate[HttpRequest, P], R]


def grant_guest_access(request: HttpRequest) -> None:
    """
    Mark the current browser session as belonging to an event guest.

    The event's time windows still determine whether the guest may
    read the guestbook or create new entries.
    """
    request.session[SESSION_GUEST_ACCESS_KEY] = True
    request.session.set_expiry(
        settings.GUESTBOOK_GUEST_ACCESS_DURATION,
    )


def has_guest_access(request: HttpRequest) -> bool:
    """
    Return whether this browser has redeemed the guest access key.
    """
    return request.session.get(SESSION_GUEST_ACCESS_KEY) is True


def revoke_guest_access(request: HttpRequest) -> None:
    """
    Remove guest access from the current browser session.
    """
    request.session.pop(
        SESSION_GUEST_ACCESS_KEY,
        None,
    )


def guest_access_required(
    view_func: View[P, R],
) -> View[P, R]:
    """
    Hide a view from browsers without redeemed guest access.
    """

    @wraps(view_func)
    def wrapper(
        request: HttpRequest,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        if not has_guest_access(request):
            raise Http404

        return view_func(
            request,
            *args,
            **kwargs,
        )

    return wrapper
