"""Adaptive next-lesson selection and coaching notes."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import SkillProgress, User
from backend.app.services import adaptive
from backend.app.services.security import hash_password


def _user(db_session: Session, interests: list[str]) -> User:
    user = User(
        email="adapt@example.com",
        password_hash=hash_password("x"),
        display_name="Ada",
        interests=interests,
    )
    db_session.add(user)
    db_session.flush()
    return user


def _set_score(db_session: Session, user: User, skill: str, score: float) -> None:
    row = db_session.scalar(
        select(SkillProgress).where(
            SkillProgress.user_id == user.id, SkillProgress.skill == skill
        )
    )
    if row is None:
        row = SkillProgress(user_id=user.id, skill=skill, level="A1")
        db_session.add(row)
    row.score = score
    db_session.flush()


def test_choose_next_lesson_targets_weakest_skill(db_session: Session) -> None:
    user = _user(db_session, interests=[])
    for skill, score in [
        ("pronunciation", 80.0),
        ("vocabulary", 80.0),
        ("grammar", 80.0),
        ("writing", 80.0),
        ("fluency", 80.0),
        ("listening", 10.0),  # weakest
    ]:
        _set_score(db_session, user, skill, score)

    assert adaptive.weakest_skill(db_session, user) == "listening"
    lesson = adaptive.choose_next_lesson(db_session, user)
    # Charla con vecinos has two listening exercises; the others have one.
    assert lesson is not None
    assert lesson.title == "Charla con vecinos"


def test_choose_next_lesson_respects_interests(db_session: Session) -> None:
    user = _user(db_session, interests=["viajes"])
    # All skills even: interest overlap breaks the tie towards "De viaje".
    lesson = adaptive.choose_next_lesson(db_session, user)
    assert lesson is not None
    assert "viajes" in lesson.topics


def test_adaptive_note_from_failed_exercises(
    client: TestClient, auth_headers: dict
) -> None:
    lesson_id = client.get("/api/lessons").json()[0]["id"]
    groups = client.get(f"/api/lessons/{lesson_id}/assessment").json()["groups"]
    grammar = next(g for g in groups if g["type"] == "grammar")["exercises"][0]
    response = client.post(
        f"/api/exercises/{grammar['id']}/attempt",
        json={"answer": "respuesta incorrecta"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    body = client.get("/api/path/today", headers=auth_headers).json()
    assert "Necesitas más práctica con" in body["next"]["description"]
    # The grammar mistake also feeds the grammar tip in the loop.
    assert body["grammar_tip"]["right"]
