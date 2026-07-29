from enum import StrEnum


class GuestbookPhase(StrEnum):
    """
    Represent the event's position on its timeline.

    CLOSED:
        The guestbook has not opened yet.

    PRE:
        The guestbook is reachable before the event.

    LIVE:
        The event is currently taking place.

    POST:
        The event has ended, but uploads remain open.

    ARCHIVED:
        Uploads are closed, but the feed remains available.
    """

    CLOSED = "closed"
    PRE = "pre"
    LIVE = "live"
    POST = "post"
    ARCHIVED = "archived"
