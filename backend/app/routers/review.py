"""Personal mistake review backed by the spaced-repetition scheduler."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
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
    answer: str


def _out(item: ReviewItem) -> dict:
    content = item.content or {}
    return {
        "id": item.id,
        "kind": item.kind,
        "prompt": content.get("prompt") or content.get("word") or content.get("concept", "Repasa este punto"),
        "options": content.get("options"),
        "passage": content.get("passage"),
        "audio_url": media_url(content.get("audio_path")),
        "due_date": item.due_date.isoformat(),
    }


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
    return [_out(item) for item in due_items(db, user, limit=20)]


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
    exercise_id = (item.content or {}).get("exercise_id")
    exercise = db.get(Exercise, exercise_id) if exercise_id else None
    if exercise is None:
        expected = (item.content or {}).get("answer") or (item.content or {}).get("translation") or (item.content or {}).get("example", "")
        correct = payload.answer.strip().casefold() == str(expected).strip().casefold()
        feedback = "¡Correcto!" if correct else f"La respuesta correcta es: {expected}"
    else:
        result = score_attempt(exercise, payload.answer)
        correct, feedback = result.correct, result.feedback
        apply_skill_deltas(db, user, result.deltas)
    record_result(db, item, 5 if correct else 1)
    db.commit()
    return {"correct": correct, "feedback": feedback, "next_due": item.due_date.isoformat()}
