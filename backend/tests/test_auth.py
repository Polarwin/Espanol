"""Auth flow: register, login, /api/me."""

from fastapi.testclient import TestClient

from conftest import USER


def test_register_returns_token_and_user(client: TestClient) -> None:
    response = client.post("/api/auth/register", json=USER)
    assert response.status_code == 201
    body = response.json()
    assert body["token"]
    assert body["user"]["email"] == USER["email"]
    assert body["user"]["display_name"] == "Maya"
    assert body["user"]["nickname"] is None
    assert body["user"]["interests"] == ["planes", "viajes"]


def test_register_duplicate_email_conflict(client: TestClient) -> None:
    client.post("/api/auth/register", json=USER)
    response = client.post("/api/auth/register", json=USER)
    assert response.status_code == 409


def test_login_success_and_me(client: TestClient) -> None:
    client.post("/api/auth/register", json=USER)
    response = client.post(
        "/api/auth/login", json={"email": USER["email"], "password": USER["password"]}
    )
    assert response.status_code == 200
    token = response.json()["token"]

    me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == USER["email"]
    assert me.json()["interests"] == ["planes", "viajes"]


def test_login_wrong_password(client: TestClient) -> None:
    client.post("/api/auth/register", json=USER)
    response = client.post(
        "/api/auth/login", json={"email": USER["email"], "password": "wrong"}
    )
    assert response.status_code == 401


def test_me_requires_auth(client: TestClient) -> None:
    assert client.get("/api/me").status_code == 401
    assert client.get("/api/path/today").status_code == 401


def test_user_can_change_name_and_nickname(client: TestClient, auth_headers: dict) -> None:
    response = client.patch(
        "/api/me",
        headers=auth_headers,
        json={"display_name": "María García", "nickname": "Mari"},
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "María García"
    assert response.json()["nickname"] == "Mari"
    assert client.get("/api/me", headers=auth_headers).json()["nickname"] == "Mari"
