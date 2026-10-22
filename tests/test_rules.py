from app.rules import requires_location


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
