from django.conf import settings
from django.utils import timezone

# TODO: add strenum for pre live and post
def current_phase() -> str:
    now = timezone.now()

    if now < settings.GUESTBOOK_STARTS_AT:
        return "pre"

    if now <= settings.GUESTBOOK_ENDS_AT:
        return "live"

    return "post"
