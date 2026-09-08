"""Review queue: answers are not leaked and not-yet-due items cannot be farmed."""

from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Attempt, Exercise, Lesson, ReviewItem, User
from backend.app.services.spaced_review import create_review_item
from conftest import USER


def _current_user(db_session: Session) -> User:
    user = db_session.scalar(select(User).where(User.email == USER["email"]))
    assert user is not None
    return user


def _lesson_id(db_session: Session) -> int:
    lesson_id = db_session.scalar(select(Lesson.id).limit(1))
    assert lesson_id is not None
    return lesson_id


def _mc_exercise(
    db_session: Session,
    *,
    kind: str = "vocabulary",
    prompt: str = "¿Cómo se dice 'train'?",
    options: list[str] | None = None,
    expected: str = "el tren",
) -> Exercise:
    exercise = Exercise(
        lesson_id=_lesson_id(db_session),
        type=kind,
        instructions="Elige la opción correcta",
        prompt=prompt,
        options=options if options is not None else ["el tren", "la playa", "el mercado", "la estación"],
        expected_answer=expected,
    )
    db_session.add(exercise)
    db_session.flush()
    return exercise


def _attempt(
    db_session: Session,
    user: User,
    exercise: Exercise,
    answer: str,
    correct: bool,
    created_at: datetime | None = None,
) -> Attempt:
    attempt = Attempt(
        user_id=user.id,
        exercise_id=exercise.id,
        answer=answer,
        correct=correct,
        score=1.0 if correct else 0.0,
        created_at=created_at or datetime(2026, 9, 1, 12, 0, 0),
    )
    db_session.add(attempt)
    db_session.flush()
    return attempt


def _queue(client: TestClient, headers: dict) -> list[dict]:
    response = client.get("/api/review", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_review_queue_omits_answers(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    user = _current_user(db_session)
    create_review_item(
        db_session, user, "vocabulary", {"word": "el tren", "translation": "the train"}
    )
    db_session.commit()

    queue = client.get("/api/review", headers=auth_headers)
    assert queue.status_code == 200
    item = next(row for row in queue.json() if row["prompt"] == "el tren")
    assert "answer" not in item


def test_future_due_review_answer_rejected(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    user = _current_user(db_session)
    item = create_review_item(
        db_session, user, "vocabulary", {"word": "la playa", "translation": "the beach"}
    )
    item.due_date = date.today() + timedelta(days=3)
    db_session.commit()

    response = client.post(
        f"/api/review/{item.id}", json={"answer": "the beach"}, headers=auth_headers
    )
    assert response.status_code == 409

    db_session.refresh(item)
    assert item.due_date == date.today() + timedelta(days=3)  # untouched by the attempt


def test_due_review_answer_still_accepted(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    user = _current_user(db_session)
    item = create_review_item(
        db_session, user, "vocabulary", {"word": "el mercado", "translation": "the market"}
    )
    db_session.commit()

    response = client.post(
        f"/api/review/{item.id}", json={"answer": "the market"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_failed_vocabulary_choice_shown_once(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    user = _current_user(db_session)
    exercise = _mc_exercise(db_session)
    _attempt(db_session, user, exercise, "la playa", correct=False)
    db_session.commit()

    queue = _queue(client, auth_headers)
    matches = [row for row in queue if row["prompt"] == exercise.prompt]
    assert len(matches) == 1
    item = matches[0]
    assert item["previous_incorrect_answer"] == "la playa"
    assert item["previous_incorrect_answer"] != exercise.expected_answer
    assert "answer" not in item  # the queue still never identifies the correct answer
    assert sum("previous_incorrect_answer" in row for row in queue) == 1


def test_latest_failure_deterministic_with_tie_and_later_correct(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    user = _current_user(db_session)
    exercise = _mc_exercise(db_session)
    tie = datetime(2026, 9, 3, 9, 0, 0)
    _attempt(db_session, user, exercise, "la playa", False, datetime(2026, 9, 2, 9, 0, 0))
    _attempt(db_session, user, exercise, "el mercado", False, tie)
    # Same timestamp as the previous failure: the higher id wins the tie-break.
    _attempt(db_session, user, exercise, "la estación", False, tie)
    # A later correct original attempt does not erase the latest failure.
    _attempt(db_session, user, exercise, "el tren", True, datetime(2026, 9, 4, 9, 0, 0))
    db_session.commit()

    queue = _queue(client, auth_headers)
    item = next(row for row in queue if row["prompt"] == exercise.prompt)
    assert item["previous_incorrect_answer"] == "la estación"


def test_previous_answer_user_isolation_and_foreign_post_404(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    user = _current_user(db_session)
    other = {"email": "otro@example.com", "password": "secret123", "display_name": "Otro"}
    response = client.post("/api/auth/register", json=other)
    assert response.status_code == 201, response.text
    other_headers = {"Authorization": f"Bearer {response.json()['token']}"}
    other_user = db_session.scalar(select(User).where(User.email == other["email"]))
    assert other_user is not None

    exercise = _mc_exercise(db_session)
    # The other user failed the exercise; the current user never attempted it.
    _attempt(db_session, other_user, exercise, "la playa", correct=False)
    item = create_review_item(
        db_session,
        user,
        "vocabulary",
        {
            "exercise_id": exercise.id,
            "prompt": exercise.prompt,
            "answer": exercise.expected_answer,
            "options": exercise.options,
        },
    )
    other_item = create_review_item(
        db_session,
        other_user,
        "vocabulary",
        {"word": "el tren", "translation": "the train"},
    )
    db_session.commit()

    queue = _queue(client, auth_headers)
    row = next(r for r in queue if r["id"] == item.id)
    assert "previous_incorrect_answer" not in row  # no leak of the other user's failure

    foreign = client.post(
        f"/api/review/{other_item.id}", json={"answer": "the train"}, headers=auth_headers
    )
    assert foreign.status_code == 404


def test_unsupported_and_legacy_items_omit_previous_answer(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    user = _current_user(db_session)
    grammar = _mc_exercise(db_session, kind="grammar", prompt="Elige el futuro correcto")
    _attempt(db_session, user, grammar, "la playa", correct=False)
    # Vocabulary but free-text (no options): not a multiple-choice item.
    writing_vocab = _mc_exercise(db_session, prompt="Traduce: the train", options=[])
    _attempt(db_session, user, writing_vocab, "el trenn", correct=False)
    # Legacy phrase item: no backing exercise at all.
    create_review_item(db_session, user, "vocabulary", {"word": "la ventana", "translation": "the window"})
    db_session.commit()

    queue = _queue(client, auth_headers)
    assert queue
    assert all("previous_incorrect_answer" not in row for row in queue)
    prompts = {row["prompt"] for row in queue}
    assert {grammar.prompt, writing_vocab.prompt, "la ventana"} <= prompts


def test_retry_scoring_and_scheduling_unchanged_with_previous_answer(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    user = _current_user(db_session)
    exercise = _mc_exercise(db_session)
    _attempt(db_session, user, exercise, "la playa", correct=False)
    db_session.commit()

    queue = _queue(client, auth_headers)
    item = next(row for row in queue if row["prompt"] == exercise.prompt)
    assert item["previous_incorrect_answer"] == "la playa"

    response = client.post(
        f"/api/review/{item['id']}", json={"answer": "el tren"}, headers=auth_headers
    )
    assert response.status_code == 200, response.text
    assert response.json()["correct"] is True
    assert response.json()["next_due"] > date.today().isoformat()

    # Rescheduled into the future: an immediate retry is rejected and changes nothing.
    retry = client.post(
        f"/api/review/{item['id']}", json={"answer": "la playa"}, headers=auth_headers
    )
    assert retry.status_code == 409

    stored = db_session.get(ReviewItem, item["id"])
    assert stored is not None
    assert stored.repetitions == 1
    assert stored.due_date == date.today() + timedelta(days=1)
