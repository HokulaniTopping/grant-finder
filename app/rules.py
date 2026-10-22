"""Business rules for the Grant Finder app."""


def requires_location(profile: dict[str, object]) -> bool:
    """Return True when a profile is missing enough location data to match grants safely.

    The proposal says the app should ask for the location before matching when the
    user has not provided one. This keeps the app from guessing and allows a clear,
    testable rule.
    """
    island = profile.get("island")
    location = profile.get("location")
    return not bool(island or location)
