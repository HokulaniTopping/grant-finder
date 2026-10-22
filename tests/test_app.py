from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_page_loads() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Grant Finder" in response.text


def test_grant_endpoint_returns_fields() -> None:
    response = client.get("/api/grants")
    assert response.status_code == 200
    body = response.json()

    assert set(body) == {"org_type", "island", "focus", "budget", "needs", "matches"}
    assert body["org_type"] == "501(c)(3)"
    assert body["island"] == "O'ahu"
    assert isinstance(body["focus"], list)
    assert isinstance(body["needs"], list)
    assert isinstance(body["matches"], list)
