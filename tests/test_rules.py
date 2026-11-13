from datetime import date, datetime

from app.rules import deadline_status, requires_location


def test_requires_location_when_no_island_or_location() -> None:
    profile = {
        "org_type": "501(c)(3)",
        "focus": ["youth education", "STEM"],
        "budget": 350000,
    }

    assert requires_location(profile) is True


def test_does_not_require_location_when_island_is_given() -> None:
    profile = {
        "org_type": "501(c)(3)",
        "island": "O'ahu",
        "focus": ["youth education", "STEM"],
        "budget": 350000,
    }

    assert requires_location(profile) is False


TODAY = date(2026, 11, 12)


def test_deadline_in_future_is_open() -> None:
    assert deadline_status({"deadline": "2026-12-01"}, TODAY) == "open"


def test_deadline_today_is_still_open() -> None:
    assert deadline_status({"deadline": date(2026, 11, 12)}, TODAY) == "open"


def test_deadline_in_past_is_closed() -> None:
    assert deadline_status({"deadline": "2026-11-11"}, TODAY) == "closed"


def test_datetime_deadline_uses_its_date() -> None:
    grant = {"deadline": datetime(2026, 11, 12, 23, 59)}
    assert deadline_status(grant, TODAY) == "open"


def test_missing_deadline_is_unknown() -> None:
    assert deadline_status({"name": "Rolling fund"}, TODAY) == "unknown"


def test_unreadable_deadline_is_unknown() -> None:
    assert deadline_status({"deadline": "sometime in spring"}, TODAY) == "unknown"
    assert deadline_status({"deadline": None}, TODAY) == "unknown"
