import os
import secrets
from collections.abc import Iterator
from datetime import date

import psycopg
import pytest
from dotenv import load_dotenv

from db.queries import tracker_grants

load_dotenv()
pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"), reason="DATABASE_URL is not set"
)


@pytest.fixture
def conn() -> Iterator[psycopg.Connection]:
    with (
        psycopg.connect(os.environ["DATABASE_URL"]) as conn,
        conn.transaction(force_rollback=True),  # undo everything the test writes
    ):
        yield conn


def _add_org(conn: psycopg.Connection, description: str) -> tuple[int, str]:
    token = secrets.token_urlsafe(16)
    row = conn.execute(
        "INSERT INTO organizations (access_token, description) VALUES (%s, %s) RETURNING id",
        (token, description),
    ).fetchone()
    assert row is not None
    return row[0], token


def _add_grant(conn: psycopg.Connection, slug: str, name: str, deadline: date | None) -> int:
    row = conn.execute(
        "INSERT INTO grants (slug, name, funder, source_url, eligibility_sentence, "
        "amount_text, deadline) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
        (slug, name, "Test funder", "https://example.org", "Open to nonprofits.", "$1", deadline),
    ).fetchone()
    assert row is not None
    return row[0]


def _save(conn: psycopg.Connection, org_id: int, grant_id: int, status: str) -> None:
    conn.execute(
        "INSERT INTO saved_grants (organization_id, grant_id, status) VALUES (%s, %s, %s)",
        (org_id, grant_id, status),
    )


def test_tracker_lists_saved_grants_by_deadline_with_unknown_last(
    conn: psycopg.Connection,
) -> None:
    busy_id, busy_token = _add_org(conn, "O'ahu youth coding nonprofit")
    other_id, _ = _add_org(conn, "Maui food pantry")
    later = _add_grant(conn, "test-later", "Later grant", date(2027, 3, 1))
    sooner = _add_grant(conn, "test-sooner", "Sooner grant", date(2026, 12, 1))
    rolling = _add_grant(conn, "test-rolling", "Rolling grant", None)
    _save(conn, busy_id, later, "interested")
    _save(conn, busy_id, rolling, "drafting")
    _save(conn, busy_id, sooner, "submitted")
    _save(conn, other_id, later, "declined")  # another org's tracker must not appear

    assert tracker_grants(conn, busy_token) == [
        ("Sooner grant", "submitted", date(2026, 12, 1)),
        ("Later grant", "interested", date(2027, 3, 1)),
        ("Rolling grant", "drafting", None),
    ]


def test_tracker_with_no_saved_grants_is_empty(conn: psycopg.Connection) -> None:
    _, token = _add_org(conn, "Kauaʻi watershed group with nothing saved yet")
    assert tracker_grants(conn, token) == []


def test_unknown_token_returns_nothing(conn: psycopg.Connection) -> None:
    assert tracker_grants(conn, "not-a-real-token") == []
