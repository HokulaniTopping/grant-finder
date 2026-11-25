"""Business rules for the Grant Finder app."""

from dataclasses import dataclass
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


EligibilityStatus = Literal["eligible", "ineligible", "unknown"]


@dataclass(frozen=True)
class Eligibility:
    """The outcome of one eligibility rule, with the reason shown to the user."""

    status: EligibilityStatus
    reason: str


# Spellings people use for each island, mapped to one key.
_ISLAND_ALIASES = {
    "oahu": "oahu",
    "maui": "maui",
    "hawaii": "hawaii",
    "hawaii island": "hawaii",
    "big island": "hawaii",
    "kauai": "kauai",
    "molokai": "molokai",
    "lanai": "lanai",
    "niihau": "niihau",
    "kahoolawe": "kahoolawe",
}
_STATEWIDE = "statewide"


def normalize_island(name: str) -> str | None:
    """Return a single key for an island name, or None if it is not a Hawaii island.

    Ignores case, the ʻokina, apostrophes, and macrons, so "O'ahu", "Oʻahu", and
    "Oahu" all match.
    """
    cleaned = name.strip().lower()
    for mark in ("ʻ", "'", "‘", "’", "`"):
        cleaned = cleaned.replace(mark, "")
    cleaned = cleaned.translate(str.maketrans("āēīōū", "aeiou"))
    if cleaned == _STATEWIDE:
        return _STATEWIDE
    return _ISLAND_ALIASES.get(cleaned)


def island_eligibility(profile: dict[str, object], grant: dict[str, object]) -> Eligibility:
    """Decide whether a grant's island restriction allows the organization's island.

    A grant lists the islands it serves in "islands". An empty list or "Statewide"
    means any island. A grant with no "islands" key, or a profile with no island,
    is "unknown" rather than a guess.
    """
    islands = grant.get("islands")
    if not isinstance(islands, list):
        return Eligibility("unknown", "The grant does not say which islands it serves.")
    allowed = {normalize_island(str(name)) for name in islands}
    if not islands or _STATEWIDE in allowed:
        return Eligibility("eligible", "Open to organizations on any island.")
    org_island = profile.get("island")
    if not isinstance(org_island, str) or normalize_island(org_island) is None:
        return Eligibility("unknown", "Your island is not known yet.")
    if normalize_island(org_island) in allowed:
        return Eligibility("eligible", f"Open to organizations on {org_island}.")
    served = ", ".join(str(name) for name in islands)
    return Eligibility("ineligible", f"Only open to organizations on {served}.")


def _normalize_org_type(value: str) -> str:
    return "".join(value.lower().split()).replace("(", "").replace(")", "")


def org_type_eligibility(profile: dict[str, object], grant: dict[str, object]) -> Eligibility:
    """Decide whether the organization's legal type is one the grant accepts.

    A grant lists accepted types in "org_types", such as "501(c)(3)" or
    "fiscally sponsored". A missing list on either side is "unknown". The
    comparison ignores case, spaces, and parentheses, so "501c3" matches "501(c)(3)".
    A 501(c)(3) also qualifies for a grant that accepts any "nonprofit".
    """
    accepted = grant.get("org_types")
    if not isinstance(accepted, list) or not accepted:
        return Eligibility("unknown", "The grant does not say which organization types qualify.")
    org_type = profile.get("org_type")
    if not isinstance(org_type, str) or not org_type.strip():
        return Eligibility("unknown", "Your organization type is not known yet.")
    accepted_keys = {_normalize_org_type(str(t)) for t in accepted}
    org_key = _normalize_org_type(org_type)
    if org_key in accepted_keys or (org_key == "501c3" and "nonprofit" in accepted_keys):
        return Eligibility("eligible", f"Accepts {org_type} organizations.")
    allowed = ", ".join(str(t) for t in accepted)
    return Eligibility(
        "ineligible", f"Only accepts {allowed} organizations; yours is {org_type}."
    )


# Fields the app must have before matching, in the order it asks for them.
_REQUIRED_FIELDS = (
    ("org_type", "What type of organization are you, such as a 501(c)(3) or fiscally sponsored?"),
    ("island", "Which island is your organization on?"),
    ("budget", "What is your organization's annual budget, roughly?"),
)


def follow_up_questions(profile: dict[str, object]) -> list[str]:
    """Return the questions to ask before matching, one per missing required field.

    An empty list means the profile has enough to match. A location given in place
    of an island counts as the island, as in `requires_location`.
    """
    questions = []
    for field, question in _REQUIRED_FIELDS:
        if field == "island":
            if requires_location(profile):
                questions.append(question)
        elif profile.get(field) in (None, "", []):
            questions.append(question)
    return questions


def _lowered(values: object) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {str(v).strip().lower() for v in values}


def match_score(profile: dict[str, object], grant: dict[str, object]) -> int:
    """Score how well a grant fits; higher ranks first.

    Each of the organization's focus areas that the grant also funds is worth 2.
    Each of its needs that the grant pays for ("uses") is worth 1. Matching ignores
    case. Missing lists score 0.
    """
    focus = _lowered(profile.get("focus")) & _lowered(grant.get("focus_areas"))
    needs = _lowered(profile.get("needs")) & _lowered(grant.get("uses"))
    return 2 * len(focus) + len(needs)
