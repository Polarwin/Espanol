"""Exercise attempt route: scoring, skill updates, loop advancement, streaks."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Attempt, Exercise, User
from ..schemas import AttemptRequest, AttemptResponse, SkillUpdate
from ..services import adaptive
from ..services.loop import advance_state, get_or_create_state
from ..services.progress import apply_skill_deltas
from ..services.scoring import score_attempt
from ..services.security import get_current_user
from ..services.streak import record_activity

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.post("/{exercise_id}/attempt", response_model=AttemptResponse)
def post_attempt(
    exercise_id: int,
    payload: AttemptRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AttemptResponse:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    result = score_attempt(exercise, payload.answer)

    db.add(
        Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            answer=payload.answer,
            correct=result.correct,
            score=result.score,
            feedback=result.feedback,
        )
    )
    updates = apply_skill_deltas(db, user, result.deltas)

    # Advance the core loop and record today's activity for the streak.
    state = get_or_create_state(db, user, adaptive.choose_next_lesson(db, user))
    next_lesson = None
    if state.current_step == "adapta":
        next_lesson = adaptive.choose_next_lesson(
            db, user, exclude_lesson_id=state.current_lesson_id
        )
    advance_state(db, user, next_lesson)
    record_activity(db, user)

    db.commit()
    return AttemptResponse(
        correct=result.correct,
        score=result.score,
        feedback=result.feedback,
        skill_updates=[SkillUpdate.model_validate(u) for u in updates],
    )
