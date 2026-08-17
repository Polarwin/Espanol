"""Placement test flow: fresh sampling per level, grading, per-skill results."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Exercise, SkillProgress, UserState


def _correct_answers(db_session: Session, questions: list[dict]) -> dict[str, str]:
    ids = [int(question["id"][3:]) for question in questions]
    rows = db_session.scalars(select(Exercise).where(Exercise.id.in_(ids))).all()
    return {f"ex-{row.id}": row.expected_answer for row in rows}


def _block(client: TestClient, auth_headers: dict, level: str) -> list[dict]:
    response = client.get(f"/api/placement?level={level}", headers=auth_headers)
    assert response.status_code == 200
    return response.json()


def test_block_is_sampled_from_seed_content(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    questions = _block(client, auth_headers, "A2")
    assert 4 <= len(questions) <= 8
    assert all("answer" not in question and "expected_answer" not in question for question in questions)
    ids = [int(question["id"][3:]) for question in questions]
    rows = db_session.scalars(select(Exercise).where(Exercise.id.in_(ids))).all()
    assert len(rows) == len(ids)


def test_block_includes_reading_passage_and_listening_audio(
    client: TestClient, auth_headers: dict
) -> None:
    questions = _block(client, auth_headers, "B1")
    by_skill: dict[str, list[dict]] = {}
    for question in questions:
        by_skill.setdefault(question["skill"], []).append(question)
    assert any(q["passage"] for q in by_skill.get("reading", []))
    assert any(q["audio_url"] for q in by_skill.get("listening", []))


def test_unknown_level_rejected(client: TestClient, auth_headers: dict) -> None:
    response = client.get("/api/placement?level=D1", headers=auth_headers)
    assert response.status_code == 400


def test_grade_pass_and_fail(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    questions = _block(client, auth_headers, "A2")
    correct = _correct_answers(db_session, questions)
    response = client.post("/api/placement/grade", json={"level": "A2", "answers": correct}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["passed"] is True
    wrong = {key: "respuesta inventada" for key in correct}
    response = client.post("/api/placement/grade", json={"level": "A2", "answers": wrong}, headers=auth_headers)
    assert response.json()["passed"] is False


def test_all_levels_correct_place_at_c2(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    answers: dict[str, str] = {}
    for level in ("A2", "B1", "B2", "C1", "C2"):
        answers.update(_correct_answers(db_session, _block(client, auth_headers, level)))
    response = client.post("/api/placement", json={"answers": answers}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["overall_level"] == "C2"
    assert body["correct"] == body["total"] > 0
    levels = db_session.scalars(select(SkillProgress.level)).all()
    assert "C2" in levels
    path = client.get("/api/path/today", headers=auth_headers).json()
    assert path["lesson"]["cefr_level"] == "C2"


def test_only_lower_levels_correct_place_at_a2(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    answers: dict[str, str] = {}
    for level in ("A1", "A2"):
        answers.update(_correct_answers(db_session, _block(client, auth_headers, level)))
    for level in ("B1",):
        answers.update({key: "respuesta inventada" for key in _correct_answers(db_session, _block(client, auth_headers, level))})
    response = client.post("/api/placement", json={"answers": answers}, headers=auth_headers)
    assert response.json()["overall_level"] == "A2"


def test_unknown_question_ids_cannot_inflate_level(
    client: TestClient, auth_headers: dict
) -> None:
    response = client.post(
        "/api/placement",
        json={"answers": {"ex-999999": "B2", "ex-888888": "B2"}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["overall_level"] == "A1"
    assert body["total"] == 0


def test_sampling_uses_random_sample(
    client: TestClient, auth_headers: dict, monkeypatch
) -> None:
    monkeypatch.setattr(
        "backend.app.routers.placement.random.sample",
        lambda rows, k: list(rows)[:k],
    )
    monkeypatch.setattr(
        "backend.app.routers.placement.random.shuffle",
        lambda rows: None,
    )
    monkeypatch.setattr(
        "backend.app.routers.placement.random.choice",
        lambda rows: list(rows)[0],
    )
    first = _block(client, auth_headers, "B2")
    second = _block(client, auth_headers, "B2")
    assert [q["id"] for q in first] == [q["id"] for q in second]


def test_skip_starts_at_random_a1_lesson(client: TestClient, auth_headers: dict, db_session: Session) -> None:
    response = client.post("/api/placement/skip", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["overall_level"] == "A1"
    path = client.get("/api/path/today", headers=auth_headers).json()
    assert path["lesson"]["cefr_level"] == "A1"
    state = db_session.scalar(select(UserState))
    assert state is not None


def test_manual_level_selection(client: TestClient, auth_headers: dict, db_session: Session) -> None:
    response = client.post("/api/placement/manual", json={"level": "B2"}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["overall_level"] == "B2"
    assert set(body["skill_levels"].values()) == {"B2"}
    levels = db_session.scalars(select(SkillProgress.level)).all()
    assert levels and set(levels) == {"B2"}
    path = client.get("/api/path/today", headers=auth_headers).json()
    assert path["lesson"]["cefr_level"] == "B2"
    bad = client.post("/api/placement/manual", json={"level": "D1"}, headers=auth_headers)
    assert bad.status_code == 400
