"""SQL queries the app runs, one function per question."""

from datetime import date

import psycopg


def tracker_grants(
    conn: psycopg.Connection, access_token: str
) -> list[tuple[str, str, date | None]]:
    """The grants on an organization's tracker, as (name, status, deadline)."""
    return conn.execute(
        """
        SELECT grants.name, saved_grants.status, grants.deadline
        FROM organizations
        JOIN saved_grants ON saved_grants.organization_id = organizations.id
        JOIN grants ON grants.id = saved_grants.grant_id
        WHERE organizations.access_token = %s
        ORDER BY grants.deadline NULLS LAST, grants.name
        """,
        (access_token,),
    ).fetchall()
