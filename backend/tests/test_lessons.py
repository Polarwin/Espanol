"""Seeded content endpoints and the /api/path/today core-loop shape."""

from fastapi.testclient import TestClient
from backend.app.seed.load import sync_missing_lessons


def test_lessons_list_published(client: TestClient) -> None:
    response = client.get("/api/lessons")
    assert response.status_code == 200
    lessons = response.json()
    assert [lesson["title"] for lesson in lessons] == [
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
    ]
    first = lessons[0]
    assert first["cefr_level"] == "A2"
    assert first["topics"] == ["planes", "vida diaria"]
    assert first["source"] == "local"
    assert first["duration_seconds"] == 180


def test_sync_missing_lessons_is_non_destructive(db_session) -> None:
    assert sync_missing_lessons(db_session, media=False) == 0


def test_lesson_detail(client: TestClient) -> None:
    lesson_id = client.get("/api/lessons").json()[0]["id"]
    response = client.get(f"/api/lessons/{lesson_id}")
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


def test_lesson_assessment_groups(client: TestClient) -> None:
    lesson_id = client.get("/api/lessons").json()[0]["id"]
    response = client.get(f"/api/lessons/{lesson_id}/assessment")
    assert response.status_code == 200
    assessment = response.json()
    assert [group["type"] for group in assessment["groups"]] == [
        "vocabulary",
        "grammar",
        "writing",
        "listening",
    ]
    assert assessment["total_questions"] == 8
    assert assessment["duration_minutes"] == 12

    listening = assessment["groups"][3]
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
