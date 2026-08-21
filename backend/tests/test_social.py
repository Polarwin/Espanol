"""Private groups: invite codes, membership races, encouragements."""

import pytest
from fastapi.testclient import TestClient

from backend.app.routers import social


def _create_group(client: TestClient, headers: dict, name: str = "Amigos") -> dict:
    response = client.post("/api/groups", json={"name": name}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_invite_code_keeps_mixed_case(
    client: TestClient, auth_headers: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(social.secrets, "token_urlsafe", lambda _n: "aB3-x_Yo")
    group = _create_group(client, auth_headers)
    assert group["invite_code"] == "aB3-x_Yo"  # not folded to upper case

    joined = client.post(
        "/api/groups/join", json={"invite_code": "aB3-x_Yo"}, headers=auth_headers
    )
    assert joined.status_code == 200
    # Codes are case-sensitive now: the folded form must not match.
    folded = client.post(
        "/api/groups/join", json={"invite_code": "AB3-X_YO"}, headers=auth_headers
    )
    assert folded.status_code == 404


def test_invite_code_collision_retries_with_fresh_code(
    client: TestClient, auth_headers: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    codes = iter(["same-code1", "same-code1", "fresh-code2"])
    monkeypatch.setattr(social.secrets, "token_urlsafe", lambda _n: next(codes))

    first = _create_group(client, auth_headers, "Grupo Uno")
    assert first["invite_code"] == "same-code1"
    second = _create_group(client, auth_headers, "Grupo Dos")
    assert second["invite_code"] == "fresh-code2"


def test_invite_code_collision_gives_up_after_retries(
    client: TestClient, auth_headers: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(social.secrets, "token_urlsafe", lambda _n: "same-code1")
    _create_group(client, auth_headers, "Grupo Uno")
    response = client.post("/api/groups", json={"name": "Grupo Dos"}, headers=auth_headers)
    assert response.status_code == 500
    # The session survives the rolled-back inserts: reads still work.
    assert client.get("/api/groups", headers=auth_headers).status_code == 200


def test_join_membership_race_is_idempotent(
    client: TestClient, auth_headers: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    group = _create_group(client, auth_headers)
    # Simulate a lost race: the membership check misses an existing row, so
    # the insert hits the unique constraint — the join must still succeed.
    monkeypatch.setattr(social, "_member", lambda db, group_id, user_id: None)
    response = client.post(
        "/api/groups/join",
        json={"invite_code": group["invite_code"]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["members"]) == 1


def test_cannot_encourage_yourself(client: TestClient, auth_headers: dict) -> None:
    group = _create_group(client, auth_headers)
    my_id = client.get("/api/me", headers=auth_headers).json()["id"]
    response = client.post(
        f"/api/groups/{group['id']}/encouragements",
        json={"to_user_id": my_id, "message": "¡Tú puedes!"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "ti mismo" in response.json()["detail"]


def test_encouraging_another_member_still_works(
    client: TestClient, auth_headers: dict
) -> None:
    group = _create_group(client, auth_headers)
    other = client.post(
        "/api/auth/register",
        json={
            "email": "otro@example.com",
            "password": "secret123",
            "display_name": "Otro",
        },
    )
    assert other.status_code == 201, other.text
    other_headers = {"Authorization": f"Bearer {other.json()['token']}"}
    joined = client.post(
        "/api/groups/join",
        json={"invite_code": group["invite_code"]},
        headers=other_headers,
    )
    assert joined.status_code == 200, joined.text
    other_id = other.json()["user"]["id"]

    response = client.post(
        f"/api/groups/{group['id']}/encouragements",
        json={"to_user_id": other_id, "message": "¡Vas muy bien!"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    encouragements = response.json()["encouragements"]
    assert encouragements[0]["to_user_id"] == other_id
    assert encouragements[0]["message"] == "¡Vas muy bien!"
