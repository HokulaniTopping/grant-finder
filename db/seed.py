"""Load sample rows into an empty database. Stops if rows already exist.

Grants come from data/grants.json (real public listings). Organizations are
synthetic profiles based on the sample inputs in docs/proposal.md.
"""

import json
import os
import secrets
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

FOCUS_AREAS = [
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
]
FUNDING_USES = ["programs", "equipment", "capital", "operating", "events"]

ORGANIZATIONS = [
    {
        "description": (
            "We're a 501(c)(3) on O'ahu with 4 staff. We run after-school coding and "
            "Hawaiian culture programs for about 60 middle schoolers in Waiʻanae. Annual "
            "budget is around $350k. We want money for laptops and a summer program next "
            "year, and we'd love help keeping track of which grants we've already started."
        ),
        "name": "Waiʻanae Code & Culture",
        "org_type": "501(c)(3)",
        "island": "oahu",
        "location": "Waiʻanae",
        "population": "middle school students",
        "budget": 350000,
        "focus": ["youth education", "STEM", "Hawaiian culture"],
        "needs": ["equipment", "programs"],
        "saved": [
            ("castle-general", "drafting"),
            ("strong-foundation", "interested"),
            ("dhhl-rfp-27-005", "submitted"),
        ],
    },
    {
        "description": "Hawaiʻi Island food bank serving Hilo and Puna, about $1.2M budget.",
        "name": "Hilo Community Food Bank",
        "org_type": "501(c)(3)",
        "island": "hawaii",
        "location": "Hilo",
        "population": "families facing food insecurity",
        "budget": 1200000,
        "focus": ["food security", "health"],
        "needs": ["operating", "equipment"],
        "saved": [("kaiser-hawaii-community", "interested")],
    },
    {
        "description": (
            "Fiscally sponsored Maui group helping Lahaina families recover after the fires."
        ),
        "name": "Lahaina Ohana Recovery Hui",
        "org_type": "fiscally sponsored",
        "island": "maui",
        "location": "Lahaina",
        "population": None,
        "budget": None,
        "focus": ["disaster recovery", "community development"],
        "needs": ["programs"],
        "saved": [("ola-maui-nui", "drafting")],
    },
    {
        "description": "Kauaʻi watershed restoration nonprofit working on Hanalei streams.",
        "name": "Hanalei Watershed Kokua",
        "org_type": "501(c)(3)",
        "island": "kauai",
        "location": "Hanalei",
        "population": None,
        "budget": 180000,
        "focus": ["environment", "conservation"],
        "needs": ["programs"],
        "saved": [],
    },
]

load_dotenv()

with open(ROOT / "data" / "grants.json", encoding="utf-8") as f:
    grants = json.load(f)

# Commits at the end, rolls back everything on an error.
with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    row = conn.execute("SELECT count(*) FROM focus_areas").fetchone()
    if row is not None and row[0] > 0:
        sys.exit("focus_areas already has rows, so nothing was changed.")

    focus_ids: dict[str, int] = {}
    for name in FOCUS_AREAS:
        new = conn.execute(
            "INSERT INTO focus_areas (name) VALUES (%s) RETURNING id", (name,)
        ).fetchone()
        assert new is not None
        focus_ids[name] = new[0]

    use_ids: dict[str, int] = {}
    for name in FUNDING_USES:
        new = conn.execute(
            "INSERT INTO funding_uses (name) VALUES (%s) RETURNING id", (name,)
        ).fetchone()
        assert new is not None
        use_ids[name] = new[0]

    grant_ids: dict[str, int] = {}
    for g in grants:
        new = conn.execute(
            "INSERT INTO grants (slug, name, funder, source_url, eligibility_sentence, "
            "amount_text, deadline, deadline_note, verified) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (
                g["id"],
                g["name"],
                g["funder"],
                g["source_url"],
                g["eligibility_sentence"],
                g["amount"],
                g["deadline"],
                g["deadline_note"],
                g["verified"],
            ),
        ).fetchone()
        assert new is not None
        grant_id = new[0]
        grant_ids[g["id"]] = grant_id
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO grant_islands (grant_id, island) VALUES (%s, %s)",
                [(grant_id, island.lower()) for island in g["islands"]],
            )
            cur.executemany(
                "INSERT INTO grant_org_types (grant_id, org_type) VALUES (%s, %s)",
                [(grant_id, t) for t in g["org_types"] or []],
            )
            cur.executemany(
                "INSERT INTO grant_focus_areas (grant_id, focus_area_id) VALUES (%s, %s)",
                [(grant_id, focus_ids[name]) for name in g["focus_areas"]],
            )
            cur.executemany(
                "INSERT INTO grant_funding_uses (grant_id, funding_use_id) VALUES (%s, %s)",
                [(grant_id, use_ids[name]) for name in g["uses"]],
            )

    for org in ORGANIZATIONS:
        new = conn.execute(
            "INSERT INTO organizations (access_token, description, name, org_type, "
            "island, location, population, budget) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (
                secrets.token_urlsafe(16),
                org["description"],
                org["name"],
                org["org_type"],
                org["island"],
                org["location"],
                org["population"],
                org["budget"],
            ),
        ).fetchone()
        assert new is not None
        org_id = new[0]
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO organization_focus_areas (organization_id, focus_area_id) "
                "VALUES (%s, %s)",
                [(org_id, focus_ids[name]) for name in org["focus"]],
            )
            cur.executemany(
                "INSERT INTO organization_needs (organization_id, funding_use_id) "
                "VALUES (%s, %s)",
                [(org_id, use_ids[name]) for name in org["needs"]],
            )
            cur.executemany(
                "INSERT INTO saved_grants (organization_id, grant_id, status) "
                "VALUES (%s, %s, %s)",
                [(org_id, grant_ids[slug], status) for slug, status in org["saved"]],
            )

print("Sample rows loaded.")
