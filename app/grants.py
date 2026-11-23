"""Load the grant listings the app matches organizations against."""

import json
from pathlib import Path

GRANTS_FILE = Path(__file__).resolve().parent.parent / "data" / "grants.json"

# The only focus areas and uses a listing may name, so profiles and grants share
# one vocabulary and `match_score` can compare them.
FOCUS_AREAS = frozenset(
    {
        "youth education",
        "STEM",
        "Hawaiian culture",
        "Hawaiian language",
        "food security",
        "environment",
        "conservation",
        "health",
        "community development",
        "disaster recovery",
    }
)
USES = frozenset({"programs", "equipment", "capital", "operating", "events"})


def load_grants(path: Path = GRANTS_FILE) -> list[dict[str, object]]:
    """Return every grant listing in the data file."""
    with path.open(encoding="utf-8") as f:
        grants: list[dict[str, object]] = json.load(f)
    return grants
