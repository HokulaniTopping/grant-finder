"""Business rules for the Grant Finder app."""

from datetime import date, datetime
from typing import Literal


def requires_location(profile: dict[str, object]) -> bool:
    """Return True when a profile is missing enough location data to match grants safely.

    The proposal says the app should ask for the location before matching when the
    user has not provided one. This keeps the app from guessing and allows a clear,
    testable rule.
    """
    island = profile.get("island")
    location = profile.get("location")
    return not bool(island or location)


DeadlineStatus = Literal["open", "closed", "unknown"]


def deadline_status(grant: dict[str, object], today: date) -> DeadlineStatus:
    """Classify a grant's deadline as open, closed, or unknown.

    The proposal says a grant whose deadline has already passed should not be shown
    as a match and should be listed under "Closed" instead. A deadline on `today`
    is still open. A missing or unreadable deadline is "unknown" so the app never
    guesses whether a nonprofit can still apply.
    """
    raw = grant.get("deadline")
    if isinstance(raw, datetime):
        deadline = raw.date()
    elif isinstance(raw, date):
        deadline = raw
    elif isinstance(raw, str):
        try:
            deadline = date.fromisoformat(raw.strip())
        except ValueError:
            return "unknown"
    else:
        return "unknown"
    return "open" if deadline >= today else "closed"
