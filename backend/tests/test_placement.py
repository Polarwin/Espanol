"""Placement test flow and per-skill initialization."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import SkillProgress, UserState


def test_questions_do_not_expose_answers(client: TestClient, auth_headers: dict) -> None:
    response = client.get("/api/placement", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 11
    assert all("answer" not in question for question in response.json())


def test_skip_starts_at_random_a1_lesson(client: TestClient, auth_headers: dict, db_session: Session) -> None:
    response = client.post("/api/placement/skip", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["overall_level"] == "A1"
    path = client.get("/api/path/today", headers=auth_headers).json()
    assert path["lesson"]["cefr_level"] == "A1"
    state = db_session.scalar(select(UserState))
    assert state is not None


def test_strong_answers_place_at_b1(client: TestClient, auth_headers: dict, db_session: Session) -> None:
    questions = client.get("/api/placement", headers=auth_headers).json()
    answers = {
        "v1": "morning", "g1": "soy", "l1": "8:30", "r1": "Su gato",
        "v2": "meet friends", "g2": "vamos", "l2": "Irán al mercado", "r2": "El sábado",
        "v3": "no obstante", "g3": "estudiaría", "r3": "A tiempo",
    }
    response = client.post("/api/placement", json={"answers": answers}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["overall_level"] == "B1"
    levels = db_session.scalars(select(SkillProgress.level)).all()
    assert "B1" in levels
    path = client.get("/api/path/today", headers=auth_headers).json()
    assert path["lesson"]["cefr_level"] == "B1"


def test_questions_are_returned_in_randomized_order(
    client: TestClient, auth_headers: dict, monkeypatch
) -> None:
    monkeypatch.setattr(
        "backend.app.routers.placement.random.sample",
        lambda questions, k: list(reversed(questions)),
    )
    response = client.get("/api/placement", headers=auth_headers)
    assert response.json()[0]["id"] == "r3"
