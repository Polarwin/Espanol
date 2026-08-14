"""A complete learner journey across the public app capabilities."""

from fastapi.testclient import TestClient


def test_complete_learner_journey(client: TestClient, auth_headers: dict) -> None:
    placement = client.post("/api/placement/skip", headers=auth_headers)
    assert placement.status_code == 200
    assert placement.json()["overall_level"] == "A1"

    today = client.get("/api/path/today", headers=auth_headers)
    assert today.status_code == 200
    assert today.json()["lesson"]["cefr_level"] == "A1"
    lesson_id = today.json()["lesson"]["id"]

    detail = client.get(f"/api/lessons/{lesson_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert len(detail.json()["segments"]) >= 2

    assessment = client.get(
        f"/api/lessons/{lesson_id}/assessment", headers=auth_headers
    ).json()
    exercises = [exercise for group in assessment["groups"] for exercise in group["exercises"]]
    assert len(exercises) == assessment["total_questions"] == 6

    # A randomized lesson can contain two, three, or four clips. Each clip
    # advances through mira -> escucha -> habla before the review step.
    attempts_needed = today.json()["total_clips"] * 3
    for index in range(attempts_needed):
        exercise = exercises[index % len(exercises)]
        answer = exercise["options"][0] if exercise.get("options") else "Esta es una respuesta completa"
        response = client.post(
            f"/api/exercises/{exercise['id']}/attempt",
            json={"answer": answer},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert "feedback" in response.json()

    completed = client.get("/api/path/today", headers=auth_headers).json()
    assert completed["step"] == "adapta"
    progress = client.get("/api/progress", headers=auth_headers)
    recap = client.get("/api/recap/weekly", headers=auth_headers)
    assert progress.status_code == recap.status_code == 200
    assert progress.json()["streak"]["days"] == 1


def test_group_join_and_encouragement_journey(
    client: TestClient, auth_headers: dict
) -> None:
    owner = client.get("/api/me", headers=auth_headers).json()
    created = client.post(
        "/api/groups", json={"name": "Compañeros"}, headers=auth_headers
    )
    assert created.status_code == 201
    group = created.json()

    friend_auth = client.post(
        "/api/auth/register",
        json={
            "email": "friend@example.com",
            "password": "secret123",
            "display_name": "Amiga",
            "interests": [],
        },
    ).json()
    friend_headers = {"Authorization": f"Bearer {friend_auth['token']}"}
    joined = client.post(
        "/api/groups/join",
        json={"invite_code": group["invite_code"].lower()},
        headers=friend_headers,
    )
    assert joined.status_code == 200
    assert len(joined.json()["members"]) == 2

    encouraged = client.post(
        f"/api/groups/{group['id']}/encouragements",
        json={"to_user_id": owner["id"], "message": "¡Sigue así!"},
        headers=friend_headers,
    )
    assert encouraged.status_code == 200
    assert encouraged.json()["encouragements"][0]["message"] == "¡Sigue así!"
