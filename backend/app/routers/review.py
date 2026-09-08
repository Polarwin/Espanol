"""Personal mistake review backed by the spaced-repetition scheduler."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Attempt, Exercise, ReviewItem, User
from ..services.progress import apply_skill_deltas
from ..services.scoring import score_attempt
from ..services.security import get_current_user
from ..services.spaced_review import due_items, record_result, review_item_from_failed_exercise
from .path import media_url

router = APIRouter(prefix="/api/review", tags=["review"])


class ReviewAnswer(BaseModel):
    answer: str = Field(max_length=2000)


def _out(item: ReviewItem, previous_incorrect_answer: str | None = None) -> dict:
    content = item.content or {}
    out = {
        "id": item.id,
        "kind": item.kind,
        "prompt": content.get("prompt") or content.get("word") or content.get("concept", "Repasa este punto"),
        "options": content.get("options"),
        "passage": content.get("passage"),
        "audio_url": media_url(content.get("audio_path")),
        "due_date": item.due_date.isoformat(),
    }
    if previous_incorrect_answer:
        out["previous_incorrect_answer"] = previous_incorrect_answer
    return out


def _eligible_exercise_ids(items: list[ReviewItem]) -> set[int]:
    """Vocabulary multiple-choice items backed by an original exercise."""
    ids: set[int] = set()
    for item in items:
        content = item.content or {}
        exercise_id = content.get("exercise_id")
        if item.kind == "vocabulary" and content.get("options") and exercise_id is not None:
            ids.add(exercise_id)
    return ids


def _latest_failed_answers(db: Session, user: User, items: list[ReviewItem]) -> dict[int, str]:
    """exercise_id -> answer of the user's latest failed original attempt (one batch query)."""
    exercise_ids = _eligible_exercise_ids(items)
    if not exercise_ids:
        return {}
    rows = db.execute(
        select(Attempt.exercise_id, Attempt.answer)
        .where(
            Attempt.user_id == user.id,
            Attempt.exercise_id.in_(exercise_ids),
            Attempt.correct.is_(False),
        )
        .order_by(Attempt.created_at.desc(), Attempt.id.desc())
    ).all()
    latest: dict[int, str] = {}
    for exercise_id, answer in rows:
        latest.setdefault(exercise_id, answer)
    return latest


@router.get("")
def review_queue(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    # Backfill earlier mistakes made before the review screen was introduced.
    failed_exercises = db.scalars(
        select(Exercise)
        .join(Attempt, Attempt.exercise_id == Exercise.id)
        .where(Attempt.user_id == user.id, Attempt.correct.is_(False))
        .order_by(Attempt.created_at.desc())
        .limit(100)
    ).all()
    for exercise in failed_exercises:
        review_item_from_failed_exercise(db, user, exercise)
    db.commit()
    items = due_items(db, user, limit=20)
    latest_failed = _latest_failed_answers(db, user, items)
    return [_out(item, latest_failed.get((item.content or {}).get("exercise_id"))) for item in items]


@router.post("/{item_id}")
def answer_review(
    item_id: int,
    payload: ReviewAnswer,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    item = db.get(ReviewItem, item_id)
    if item is None or item.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review item not found")
    if item.due_date > date.today():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este repaso aún no toca; vuelve cuando llegue su fecha.",
        )
    correction = None
    exercise_id = (item.content or {}).get("exercise_id")
    exercise = db.get(Exercise, exercise_id) if exercise_id else None
    if exercise is None:
        expected = (item.content or {}).get("answer") or (item.content or {}).get("translation") or (item.content or {}).get("example", "")
        correct = payload.answer.strip().casefold() == str(expected).strip().casefold()
        feedback = "¡Correcto!" if correct else f"La respuesta correcta es: {expected}"
    else:
        db.commit()  # Release the read transaction before optional model inference.
        result = score_attempt(exercise, payload.answer)
        correct, feedback = result.correct, result.feedback
        correction = result.correction
        apply_skill_deltas(db, user, result.deltas)
    record_result(db, item, 5 if correct else 1)
    db.commit()
    return {"correct": correct, "feedback": feedback, "next_due": item.due_date.isoformat(), "correction": correction.model_dump() if correction else None}
