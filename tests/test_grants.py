from datetime import date

from app.grants import FOCUS_AREAS, USES, load_grants
from app.rules import normalize_island

REQUIRED_TEXT = ("id", "name", "funder", "source_url", "eligibility_sentence", "amount")


def test_every_listing_has_required_text_fields() -> None:
    for grant in load_grants():
        for field in REQUIRED_TEXT:
            value = grant.get(field)
            assert isinstance(value, str) and value.strip(), f"{grant.get('id')}: {field}"
        assert str(grant["source_url"]).startswith("https://")


def test_listing_ids_are_unique() -> None:
    ids = [grant["id"] for grant in load_grants()]
    assert len(ids) == len(set(ids))


def test_deadlines_are_iso_dates_or_null_with_a_note() -> None:
    for grant in load_grants():
        deadline = grant["deadline"]
        if deadline is None:
            assert grant["deadline_note"], f"{grant['id']}: missing deadline needs a note"
        else:
            date.fromisoformat(str(deadline))


def test_islands_are_known_island_names() -> None:
    for grant in load_grants():
        islands = grant["islands"]
        assert isinstance(islands, list) and islands, grant["id"]
        for name in islands:
            assert normalize_island(str(name)) is not None, f"{grant['id']}: {name}"


def test_focus_areas_and_uses_come_from_the_shared_vocabulary() -> None:
    for grant in load_grants():
        assert set(grant["focus_areas"]) <= FOCUS_AREAS, grant["id"]  # type: ignore[arg-type]
        assert set(grant["uses"]) <= USES, grant["id"]  # type: ignore[arg-type]


def test_org_types_are_a_list_or_null() -> None:
    for grant in load_grants():
        assert grant["org_types"] is None or isinstance(grant["org_types"], list)


def _grant(grant_id: str) -> dict[str, object]:
    return next(g for g in load_grants() if g["id"] == grant_id)


def test_maui_only_grant_excludes_oahu_org() -> None:
    from app.rules import island_eligibility

    result = island_eligibility({"island": "O'ahu"}, _grant("ola-maui-nui"))
    assert result.status == "ineligible"


def test_past_kauai_cultural_deadline_is_closed() -> None:
    from app.rules import deadline_status

    assert deadline_status(_grant("kauai-cultural-fy2027"), date(2026, 11, 23)) == "closed"
