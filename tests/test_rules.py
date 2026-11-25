from datetime import date, datetime

from app.rules import (
    deadline_status,
    follow_up_questions,
    island_eligibility,
    match_score,
    normalize_island,
    org_type_eligibility,
    requires_location,
)


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


# Island eligibility

def test_island_spellings_normalize_to_one_key() -> None:
    for name in ("O'ahu", "Oʻahu", "Oahu", " oahu "):
        assert normalize_island(name) == "oahu"
    assert normalize_island("Hawai'i Island") == "hawaii"
    assert normalize_island("Big Island") == "hawaii"
    assert normalize_island("Kauaʻi") == "kauai"
    assert normalize_island("Waianae") is None


def test_grant_on_same_island_is_eligible() -> None:
    result = island_eligibility({"island": "O'ahu"}, {"islands": ["Oahu"]})
    assert result.status == "eligible"


def test_grant_restricted_to_other_island_is_ineligible_with_reason() -> None:
    result = island_eligibility({"island": "O'ahu"}, {"islands": ["Maui", "Molokaʻi"]})
    assert result.status == "ineligible"
    assert result.reason == "Only open to organizations on Maui, Molokaʻi."


def test_statewide_or_empty_island_list_is_eligible() -> None:
    profile = {"island": "Kauaʻi"}
    assert island_eligibility(profile, {"islands": ["Statewide"]}).status == "eligible"
    assert island_eligibility(profile, {"islands": []}).status == "eligible"


def test_island_unknown_when_grant_or_profile_does_not_say() -> None:
    assert island_eligibility({"island": "Maui"}, {}).status == "unknown"
    assert island_eligibility({}, {"islands": ["Maui"]}).status == "unknown"


# Org type eligibility (sample case 3)

def test_fiscally_sponsored_group_excluded_from_501c3_only_grant() -> None:
    profile = {"org_type": "fiscally sponsored", "island": "Maui"}
    result = org_type_eligibility(profile, {"org_types": ["501(c)(3)"]})
    assert result.status == "ineligible"
    assert result.reason == (
        "Only accepts 501(c)(3) organizations; yours is fiscally sponsored."
    )


def test_fiscally_sponsored_group_eligible_when_grant_accepts_it() -> None:
    profile = {"org_type": "Fiscally Sponsored"}
    grant = {"org_types": ["501(c)(3)", "fiscally sponsored"]}
    assert org_type_eligibility(profile, grant).status == "eligible"


def test_org_type_ignores_spacing_and_parentheses() -> None:
    result = org_type_eligibility({"org_type": "501c3"}, {"org_types": ["501(c)(3)"]})
    assert result.status == "eligible"


def test_org_type_unknown_when_grant_or_profile_does_not_say() -> None:
    assert org_type_eligibility({"org_type": "501(c)(3)"}, {}).status == "unknown"
    assert org_type_eligibility({"org_type": "501(c)(3)"}, {"org_types": []}).status == "unknown"
    assert org_type_eligibility({}, {"org_types": ["501(c)(3)"]}).status == "unknown"


# Follow-up questions (sample cases 6 and 8)

def test_very_short_profile_gets_all_follow_up_questions() -> None:
    profile = {"description": "we help kupuna"}
    assert follow_up_questions(profile) == [
        "What type of organization are you, such as a 501(c)(3) or fiscally sponsored?",
        "Which island is your organization on?",
        "What is your organization's annual budget, roughly?",
    ]


def test_profile_missing_only_location_asks_only_for_island() -> None:
    profile = {"org_type": "501(c)(3)", "budget": 350000}
    assert follow_up_questions(profile) == ["Which island is your organization on?"]


def test_complete_profile_needs_no_follow_up() -> None:
    profile = {"org_type": "501(c)(3)", "island": "O'ahu", "budget": 350000}
    assert follow_up_questions(profile) == []


# Match score (sample cases 1 and 2)

OAHU_YOUTH_PROFILE = {
    "focus": ["youth education", "STEM", "Hawaiian culture"],
    "needs": ["equipment", "summer programming"],
}


def test_more_focus_and_need_overlap_scores_higher() -> None:
    stem_grant = {"focus_areas": ["STEM", "Youth Education"], "uses": ["equipment"]}
    culture_grant = {"focus_areas": ["Hawaiian culture"], "uses": ["operating"]}
    assert match_score(OAHU_YOUTH_PROFILE, stem_grant) == 5
    assert match_score(OAHU_YOUTH_PROFILE, culture_grant) == 2


def test_unrelated_grant_scores_zero() -> None:
    food_bank = {"focus": ["food security"], "needs": ["refrigeration"]}
    youth_grant = {"focus_areas": ["youth education"], "uses": ["equipment"]}
    assert match_score(food_bank, youth_grant) == 0


def test_missing_lists_score_zero() -> None:
    assert match_score({}, {"focus_areas": ["STEM"]}) == 0
    assert match_score(OAHU_YOUTH_PROFILE, {}) == 0


def test_501c3_qualifies_for_grant_open_to_any_nonprofit() -> None:
    grant = {"org_types": ["nonprofit"]}
    assert org_type_eligibility({"org_type": "501(c)(3)"}, grant).status == "eligible"
    assert org_type_eligibility({"org_type": "fiscally sponsored"}, grant).status == "ineligible"
