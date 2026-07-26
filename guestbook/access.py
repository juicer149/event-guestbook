from datetime import timedelta
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from django.http import Http404, HttpRequest, HttpResponse


SESSION_ACCESS_KEY = "guestbook_can_create"
ACCESS_DURATION = timedelta(hours=48)

P = ParamSpec("P")
R = TypeVar("R", bound=HttpResponse)


def grant_create_access(request: HttpRequest) -> None:
    request.session[SESSION_ACCESS_KEY] = True
    request.session.set_expiry(ACCESS_DURATION)


def has_create_access(request: HttpRequest) -> bool:
    return request.session.get(SESSION_ACCESS_KEY) is True


def revoke_create_access(request: HttpRequest) -> None:
    request.session.pop(SESSION_ACCESS_KEY, None)


def create_access_required(
    view_func: Callable[P, R],
) -> Callable[P, R]:
    @wraps(view_func)
    def wrapper(
        request: HttpRequest,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        if not has_create_access(request):
            raise Http404

        return view_func(request, *args, **kwargs)

    return wrapper
