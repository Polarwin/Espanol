"""Auth flow: register, login, /api/me."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.models import User
from backend.app.routers import auth

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


def test_register_race_returns_409_not_500(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    client.post("/api/auth/register", json=USER)
    # Simulate a lost race: the duplicate-email pre-check misses the existing
    # row, so the unique constraint fires at flush/commit time.
    monkeypatch.setattr(
        auth, "select", lambda *a, **k: select(User).where(User.id == -1)
    )
    response = client.post("/api/auth/register", json=USER)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"
    # The session was rolled back and stays usable.
    monkeypatch.undo()
    login = client.post(
        "/api/auth/login", json={"email": USER["email"], "password": USER["password"]}
    )
    assert login.status_code == 200


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


def test_register_rejects_short_or_empty_password(client: TestClient) -> None:
    for password in ("", "short", "1234567"):
        response = client.post(
            "/api/auth/register",
            json={**USER, "email": f"{len(password)}@example.com", "password": password},
        )
        assert response.status_code == 422


def test_register_rejects_non_email(client: TestClient) -> None:
    for email in ("not-an-email", "missing@tld", "two@@example.com", "spaces in@example.com"):
        response = client.post("/api/auth/register", json={**USER, "email": email})
        assert response.status_code == 422


def test_register_rejects_oversized_fields(client: TestClient) -> None:
    too_long_password = client.post(
        "/api/auth/register", json={**USER, "password": "p" * 129}
    )
    assert too_long_password.status_code == 422

    too_long_name = client.post(
        "/api/auth/register", json={**USER, "display_name": "Maya " * 20}
    )
    assert too_long_name.status_code == 422

    too_many_interests = client.post(
        "/api/auth/register",
        json={**USER, "interests": [f"tema{i}" for i in range(11)]},
    )
    assert too_many_interests.status_code == 422

    too_long_interest = client.post(
        "/api/auth/register", json={**USER, "interests": ["x" * 41]}
    )
    assert too_long_interest.status_code == 422


def test_register_valid_payload_still_works_and_is_trimmed(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "email": "lucia@example.com",
            "password": "una-clave-segura",
            "display_name": "  Lucía   García  ",
            "interests": ["planes", "", "viajes"],
        },
    )
    assert response.status_code == 201
    assert response.json()["user"]["display_name"] == "Lucía García"
    assert response.json()["user"]["interests"] == ["planes", "viajes"]


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
