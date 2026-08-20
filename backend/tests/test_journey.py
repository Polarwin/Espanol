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
    assert len(exercises) == assessment["total_questions"]
    assert len(exercises) >= 4

    exercise = exercises[0]
    answer = exercise["options"][0] if exercise.get("options") else "Esta es una respuesta completa"
    response = client.post(
        f"/api/exercises/{exercise['id']}/attempt",
        json={"answer": answer},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "feedback" in response.json()
    assert client.get("/api/path/today", headers=auth_headers).json()["step"] == "mira"

    # Only the guarded Mi Ruta endpoint advances visible stages.
    route = today.json()
    while route["step"] != "adapta":
        route = client.post(
            "/api/path/advance", json={"step": route["step"]}, headers=auth_headers
        ).json()

    completed = client.get("/api/path/today", headers=auth_headers).json()
    assert completed["step"] == "adapta"
    progress = client.get("/api/progress", headers=auth_headers)
    recap = client.get("/api/recap/weekly", headers=auth_headers)
    assert progress.status_code == recap.status_code == 200
    assert progress.json()["streak"]["days"] == 1


def test_mi_ruta_stages_advance_and_stale_taps_do_not_skip(
    client: TestClient, auth_headers: dict
) -> None:
    today = client.get("/api/path/today", headers=auth_headers).json()
    assert today["step"] == "mira"
    assert today["captions"]
    assert len(today["captions"]) >= 2
    assert today["captions"][0]["text"] == today["subtitle"]["es"]
    assert today["clip_start"] < today["clip_end"]
    assert today["captions"][-1]["end"] > today["clip_end"]

    listening = client.post(
        "/api/path/advance", json={"step": "mira"}, headers=auth_headers
    )
    assert listening.status_code == 200
    assert listening.json()["step"] == "escucha"

    # A delayed duplicate request must not accidentally skip escucha.
    duplicate = client.post(
        "/api/path/advance", json={"step": "mira"}, headers=auth_headers
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["step"] == "escucha"

    speaking = client.post(
        "/api/path/advance", json={"step": "escucha"}, headers=auth_headers
    )
    assert speaking.json()["step"] == "comprueba"

    checking = client.post(
        "/api/path/advance", json={"step": "comprueba"}, headers=auth_headers
    )
    assert checking.json()["step"] == "habla"

    next_clip = client.post(
        "/api/path/advance", json={"step": "habla"}, headers=auth_headers
    ).json()
    assert next_clip["step"] == "mira"
    assert next_clip["clip_index"] == 1


def test_clip_quiz_after_listening(client: TestClient, auth_headers: dict) -> None:
    today = client.get("/api/path/today", headers=auth_headers).json()
    assert today["quiz"] is None

    client.post("/api/path/advance", json={"step": "mira"}, headers=auth_headers)
    quiz_path = client.post(
        "/api/path/advance", json={"step": "escucha"}, headers=auth_headers
    ).json()
    assert quiz_path["step"] == "comprueba"
    quiz = quiz_path["quiz"]
    assert quiz is not None
    assert quiz["prompt"].startswith("¿Qué significa")
    assert len(quiz["options"]) == 3

    # The correct meaning is the current clip's first transcript translation.
    detail = client.get(f"/api/lessons/{quiz_path['lesson']['id']}", headers=auth_headers).json()
    clip = detail["segments"][quiz_path["clip_index"]]
    answer = clip["transcript"][0]["en"]
    assert answer in quiz["options"]

    correct = client.post(
        "/api/path/quiz", json={"choice": answer}, headers=auth_headers
    )
    assert correct.status_code == 200
    assert correct.json() == {"correct": True, "correct_answer": answer}

    wrong_option = next(option for option in quiz["options"] if option != answer)
    wrong = client.post(
        "/api/path/quiz", json={"choice": wrong_option}, headers=auth_headers
    )
    assert wrong.json()["correct"] is False


def test_conversa_step_closes_the_lesson(client: TestClient, auth_headers: dict) -> None:
    today = client.get("/api/path/today", headers=auth_headers).json()
    first_lesson = today["lesson"]["id"]

    state = today
    while state["step"] != "adapta":
        state = client.post(
            "/api/path/advance", json={"step": state["step"]}, headers=auth_headers
        ).json()

    review = client.post(
        "/api/path/advance", json={"step": "adapta"}, headers=auth_headers
    ).json()
    assert review["step"] == "conversa"
    assert review["lesson"]["id"] == first_lesson  # same lesson, closing conversation

    moved = client.post(
        "/api/path/advance", json={"step": "conversa"}, headers=auth_headers
    ).json()
    assert moved["step"] == "mira"
    assert moved["clip_index"] == 0
    assert moved["lesson"]["id"] != first_lesson


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
