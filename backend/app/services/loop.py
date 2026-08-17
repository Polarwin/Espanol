"""User position in the core loop (mira -> escucha -> comprueba -> habla per clip, then adapta -> conversa)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Lesson, User, UserState

STEPS = ("mira", "escucha", "comprueba", "habla", "adapta", "conversa")


def get_or_create_state(db: Session, user: User, first_lesson: Lesson | None) -> UserState:
    state = db.get(UserState, user.id)
    if state is None:
        state = UserState(
            user_id=user.id,
            current_lesson_id=first_lesson.id if first_lesson else None,
            current_step="mira",
            current_clip_index=0,
        )
        db.add(state)
        db.flush()
    return state


def advance_state(db: Session, user: User, next_lesson: Lesson | None = None) -> UserState:
    """Advance the user one tick through the loop.

    mira -> escucha -> comprueba -> habla -> (next clip's mira) ... -> adapta
    after the last clip, then conversa closes the lesson with the role-play.
    When conversa completes, the user moves on to the next lesson at mira/0.
    """
    state = db.get(UserState, user.id)
    if state is None or state.current_lesson_id is None:
        return state
    lesson = db.get(Lesson, state.current_lesson_id)
    if lesson is None:
        return state
    total_clips = len(lesson.segments)

    if state.current_step == "mira":
        state.current_step = "escucha"
    elif state.current_step == "escucha":
        state.current_step = "comprueba"
    elif state.current_step == "comprueba":
        state.current_step = "habla"
    elif state.current_step == "habla":
        if state.current_clip_index + 1 < total_clips:
            state.current_clip_index += 1
            state.current_step = "mira"
        else:
            state.current_step = "adapta"
    elif state.current_step == "adapta":
        state.current_step = "conversa"
    else:  # conversa -> move on to the next lesson
        if next_lesson is not None:
            state.current_lesson_id = next_lesson.id
        state.current_step = "mira"
        state.current_clip_index = 0
    db.flush()
    return state
