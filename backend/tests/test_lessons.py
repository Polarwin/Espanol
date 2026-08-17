"""Seeded content endpoints and the /api/path/today core-loop shape."""

from fastapi.testclient import TestClient
from backend.app.seed.load import sync_missing_lessons


def test_lessons_list_published(client: TestClient) -> None:
    response = client.get("/api/lessons")
    assert response.status_code == 200
    lessons = response.json()
    titles = [lesson["title"] for lesson in lessons]
    assert titles[:15] == [
        "Charla con vecinos",
        "En el café",
        "De viaje",
        "Primeras presentaciones",
        "Compras en el mercado",
        "Mi familia y mi casa",
        "Un día normal",
        "En la consulta",
        "Buscar piso",
        "Vitamina A2 · U1: Vamos a conocernos",
        "Vitamina A2 · U2: Mi lugar en el mundo",
        "Vitamina A2 · Repaso U1–U2",
        "Aprender juntos",
        "Una ruta de senderismo",
        "Mensajes con intención",
    ]
    assert len(lessons) == 86
    assert {
        level: sum(lesson["cefr_level"] == level for lesson in lessons)
        for level in ("A1", "A2", "B1", "B2", "C1", "C2")
    } == {"A1": 10, "A2": 10, "B1": 10, "B2": 12, "C1": 24, "C2": 20}
    first = lessons[0]
    assert first["cefr_level"] == "A2"
    assert first["topics"] == ["planes", "vida diaria"]
    assert first["source"] == "local"
    assert first["duration_seconds"] == 180


def test_sync_missing_lessons_is_non_destructive(db_session) -> None:
    assert sync_missing_lessons(db_session, media=False) == 0


def test_lesson_detail(client: TestClient, auth_headers: dict) -> None:
    lesson_id = client.get("/api/lessons").json()[0]["id"]
    response = client.get(f"/api/lessons/{lesson_id}", headers=auth_headers)
    assert response.status_code == 200
    detail = response.json()
    assert detail["video_url"].startswith("/media/seed/charla-con-vecinos/")
    assert len(detail["segments"]) == 4
    segment = detail["segments"][0]
    assert segment["video_url"] == detail["video_url"]
    assert segment["transcript"][0] == {
        "es": "¿Qué planes tienes para el fin de semana?",
        "en": "What plans do you have for the weekend?",
    }
    assert {phrase["text"] for phrase in segment["phrases"]} >= {"fin de semana"}
    assert "Maya" in detail["personal_welcome"]
    assert detail["session_mission"]
    assert detail["closing_challenge"]
    assert len(detail["vocabulary"]) == 12
    assert {item["text"] for item in detail["vocabulary"]} >= {"los vecinos", "el fin de semana"}
    weekend = next(item for item in detail["vocabulary"] if item["text"] == "el fin de semana")
    assert weekend["definition_es"].startswith("Una palabra")
    assert "fin de semana" in weekend["example_es"].lower()


def test_select_lesson_remembers_catalog_choice(client: TestClient, auth_headers: dict) -> None:
    lessons = client.get("/api/lessons").json()
    selected = lessons[-1]
    response = client.post(f"/api/lessons/{selected['id']}/select", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"selected": True, "lesson_id": selected["id"]}
    today = client.get("/api/path/today", headers=auth_headers).json()
    assert today["lesson"]["id"] == selected["id"]
    assert today["step"] == "mira"
    assert today["clip_index"] == 0


def test_lesson_assessment_groups(client: TestClient) -> None:
    lesson_id = client.get("/api/lessons").json()[0]["id"]
    response = client.get(f"/api/lessons/{lesson_id}/assessment")
    assert response.status_code == 200
    assessment = response.json()
    assert [group["type"] for group in assessment["groups"]] == [
        "vocabulary",
        "grammar",
        "reading",
        "writing",
        "listening",
    ]
    assert assessment["total_questions"] == 13
    assert assessment["duration_minutes"] == 20

    listening = assessment["groups"][4]
    question = next(
        ex for ex in listening["exercises"] if "Lucía" in ex["prompt"]
    )
    assert question["options"] == [
        "Visitará a sus vecinos",
        "Irá a la playa",
        "Trabajará en casa",
    ]
    assert "expected_answer" not in question
    assert question["audio_url"].startswith("/media/")


def test_path_today_shape_for_new_user(client: TestClient, auth_headers: dict) -> None:
    response = client.get("/api/path/today", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()

    assert body["lesson"]["title"] == "Charla con vecinos"
    assert body["lesson"]["cefr_level"] == "A2"
    assert body["step"] == "mira"
    assert body["clip_index"] == 0
    assert body["total_clips"] == 4
    assert body["video_url"] == "/media/seed/charla-con-vecinos/video.mp4"
    assert body["subtitle"]["es"] == "¿Qué planes tienes para el fin de semana?"

    assert body["feedback"] == {"pronunciation": 82.0, "fluidez": 74.0, "gramatica": 90.0}
    assert body["pronunciation_tip"] == {
        "phrase": "fin de semana",
        "tip": "Suaviza la d entre vocales",
    }
    assert body["grammar_tip"] == {
        "wrong": "¿Qué planes tú tienes?",
        "right": "¿Qué planes tienes?",
        "explanation": "El pronombre no es necesario aquí.",
    }
    assert body["next"]["label"].startswith("Siguiente: ")
    assert isinstance(body["next"]["lesson_id"], int)
    assert isinstance(body["next"]["description"], str)
    assert isinstance(body["next"]["topics"], list)


def test_lesson_completion_is_saved_once(client: TestClient, auth_headers: dict) -> None:
    lesson_id = client.get("/api/lessons").json()[0]["id"]

    first = client.post(f"/api/lessons/{lesson_id}/complete", headers=auth_headers)
    second = client.post(f"/api/lessons/{lesson_id}/complete", headers=auth_headers)

    assert first.status_code == second.status_code == 200
    assert first.json()["new_completion"] is True
    assert second.json()["new_completion"] is False
    assert second.json()["lessons_completed_total"] == 1

    progress = client.get("/api/progress", headers=auth_headers).json()
    assert progress["lessons_completed_total"] == 1
    assert progress["completed_lesson_ids"] == [lesson_id]
    assert progress["weekly_goal"]["current"] == 1
