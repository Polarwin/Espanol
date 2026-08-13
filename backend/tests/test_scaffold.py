"""Integration coverage for completed scaffold endpoints."""

from fastapi.testclient import TestClient


def test_progress_and_recap_require_auth(client: TestClient) -> None:
    assert client.get("/api/progress").status_code == 401
    assert client.get("/api/recap/weekly").status_code == 401


def test_progress_and_recap(client: TestClient, auth_headers: dict) -> None:
    assert client.get("/api/progress", headers=auth_headers).status_code == 200
    assert client.get("/api/recap/weekly", headers=auth_headers).status_code == 200


def test_create_and_list_private_group(client: TestClient, auth_headers: dict) -> None:
    created = client.post("/api/groups", json={"name": "Amigos"}, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["members"][0]["role"] == "owner"
    groups = client.get("/api/groups", headers=auth_headers)
    assert [group["name"] for group in groups.json()] == ["Amigos"]


def test_content_sources_and_pronunciation_boundary(client: TestClient, auth_headers: dict) -> None:
    sources = client.get("/api/content/sources", headers=auth_headers)
    assert [source["name"] for source in sources.json()] == ["Español", "Vitamina"]
    response = client.post("/api/pronunciation/evaluate", files={"audio": ("voice.webm", b"audio")}, headers=auth_headers)
    assert response.status_code == 501
