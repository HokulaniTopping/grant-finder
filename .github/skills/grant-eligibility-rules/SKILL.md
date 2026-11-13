---
name: grant-eligibility-rules
description: Use when adding, changing, or reviewing deterministic Grant Finder rules for location, grant eligibility, deadlines, or match explanations.
---

# Grant Eligibility Rules

Use this skill only for deterministic grant-matching and eligibility behavior.

## Workflow

1. Read the relevant requirement in `docs/proposal.md` and the nearby implementation and tests before changing behavior.
2. Translate the requirement into explicit inputs, outcomes, and reasons. Treat missing information as unknown; do not guess an island, eligibility status, or deadline.
3. Keep deterministic business decisions in `app/rules.py`. Keep HTTP handling in `app/main.py` and AI extraction or generation in `app/agent.py` when that module exists.
4. Add or update focused tests in `tests/test_rules.py` for qualifying, non-qualifying, and missing or boundary inputs relevant to the rule.
5. When explaining a match or exclusion, use the grant's stated eligibility evidence. Do not invent requirements or imply certainty that the source does not support.
6. Run `uv run pytest`, `uv run ruff check`, and `uv run mypy` after changing rules.

Keep each rule small, named for its decision, and independently testable. Avoid adding abstractions until more than one rule needs them.