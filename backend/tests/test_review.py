"""Review queue: answers are not leaked and not-yet-due items cannot be farmed."""

from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import User
from backend.app.services.spaced_review import create_review_item
from conftest import USER


def _current_user(db_session: Session) -> User:
    user = db_session.scalar(select(User).where(User.email == USER["email"]))
    assert user is not None
    return user


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
