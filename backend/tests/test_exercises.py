"""Exercise attempt scoring, normalization, skill updates, loop advancement."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import SkillProgress, Streak


def _exercise(client: TestClient, group_type: str, prompt_fragment: str) -> dict:
    lesson_id = client.get("/api/lessons").json()[0]["id"]  # Charla con vecinos
    groups = client.get(f"/api/lessons/{lesson_id}/assessment").json()["groups"]
    group = next(g for g in groups if g["type"] == group_type)
    return next(ex for ex in group["exercises"] if prompt_fragment in ex["prompt"])


def _attempt(client: TestClient, headers: dict, exercise_id: int, answer: str) -> dict:
    response = client.post(
        f"/api/exercises/{exercise_id}/attempt", json={"answer": answer}, headers=headers
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_text_answer_normalization(client: TestClient, auth_headers: dict) -> None:
    exercise = _exercise(client, "grammar", "¿Qué planes tú tienes?")
    # No accents, no inverted punctuation, lowercase: still correct.
    body = _attempt(client, auth_headers, exercise["id"], "Que planes tienes")
    assert body["correct"] is True
    assert body["score"] == 1.0
    assert body["skill_updates"] == [
        {"skill": "grammar", "delta": 2.0},
        {"skill": "writing", "delta": 1.0},
    ]


def test_wrong_text_answer(client: TestClient, auth_headers: dict) -> None:
    exercise = _exercise(client, "grammar", "¿Qué planes tú tienes?")
    body = _attempt(client, auth_headers, exercise["id"], "no lo sé")
    assert body["correct"] is False
    assert body["score"] == 0.0
    assert "¿Qué planes tienes?" in body["feedback"]
    assert {u["skill"]: u["delta"] for u in body["skill_updates"]} == {
        "grammar": -1.0,
        "writing": -0.5,
    }


def test_option_answer_is_exact(client: TestClient, auth_headers: dict) -> None:
    exercise = _exercise(client, "listening", "Lucía")
    assert _attempt(client, auth_headers, exercise["id"], "Irá a la playa")["correct"] is True
    assert _attempt(client, auth_headers, exercise["id"], "irá a la playa")["correct"] is False
    assert _attempt(client, auth_headers, exercise["id"], "Trabajará en casa")["correct"] is False


def test_writing_heuristic(client: TestClient, auth_headers: dict) -> None:
    exercise = _exercise(client, "writing", "4 frases")
    short = _attempt(client, auth_headers, exercise["id"], "voy")
    assert short["correct"] is False
    long = _attempt(
        client,
        auth_headers,
        exercise["id"],
        "Este fin de semana voy a ir a la playa con mis amigos y voy a descansar.",
    )
    assert long["correct"] is True
    assert long["score"] == 0.8


def test_skill_score_clamped_at_100(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    exercise = _exercise(client, "grammar", "Este sábado")
    user_id = db_session.scalar(select(SkillProgress.user_id).limit(1))
    row = db_session.scalar(
        select(SkillProgress).where(
            SkillProgress.user_id == user_id, SkillProgress.skill == "grammar"
        )
    )
    row.score = 99.5
    db_session.flush()

    _attempt(client, auth_headers, exercise["id"], "voy")
    db_session.refresh(row)
    assert row.score == 100.0


def test_skill_score_clamped_at_0(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    exercise = _exercise(client, "listening", "Lucía")
    user_id = db_session.scalar(select(SkillProgress.user_id).limit(1))
    row = db_session.scalar(
        select(SkillProgress).where(
            SkillProgress.user_id == user_id, SkillProgress.skill == "listening"
        )
    )
    row.score = 0.5
    db_session.flush()

    _attempt(client, auth_headers, exercise["id"], "Trabajará en casa")
    db_session.refresh(row)
    assert row.score == 0.0


def test_attempt_advances_loop_and_streak(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    exercise = _exercise(client, "vocabulary", "quedar")

    def step() -> tuple[str, int]:
        body = client.get("/api/path/today", headers=auth_headers).json()
        return body["step"], body["clip_index"]

    assert step() == ("mira", 0)
    _attempt(client, auth_headers, exercise["id"], "reunirse")
    assert step() == ("escucha", 0)
    _attempt(client, auth_headers, exercise["id"], "reunirse")
    assert step() == ("habla", 0)
    _attempt(client, auth_headers, exercise["id"], "reunirse")
    assert step() == ("mira", 1)

    user_id = db_session.scalar(select(Streak.user_id).limit(1))
    streak = db_session.scalar(select(Streak).where(Streak.user_id == user_id))
    assert streak.current_days == 1  # same-day activity counts once
