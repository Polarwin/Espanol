"""Adaptive lesson selection and coaching notes.

The next lesson is chosen for the user's weakest skills (skills do not advance
together) and personal interests, at an appropriate CEFR level.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Attempt, Exercise, Lesson, SkillProgress, User
from .progress import DEFAULT_SKILL_SCORES, get_skill_scores

CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

_TYPE_LABELS = {
    "vocabulary": "el vocabulario",
    "grammar": "la gramática",
    "writing": "la escritura",
    "listening": "la comprensión auditiva",
    "pronunciation": "la pronunciación",
}


def weakest_skill(db: Session, user: User) -> str:
    scores = get_skill_scores(db, user)
    if not scores:
        scores = DEFAULT_SKILL_SCORES
    return min(scores, key=lambda s: scores[s])


def _user_cefr_index(db: Session, user: User) -> int:
    levels = db.scalars(select(SkillProgress.level).where(SkillProgress.user_id == user.id)).all()
    if not levels:
        return 0
    # Use the median-ish level: sort and take the middle.
    ordered = sorted(
        (CEFR_ORDER.index(level) if level in CEFR_ORDER else 0) for level in levels
    )
    return ordered[len(ordered) // 2]


def _lesson_score(db: Session, user: User, lesson: Lesson, weak: str, user_cefr: int) -> float:
    interests = set(user.interests or [])
    topic_overlap = len(interests & set(lesson.topics or []))
    weak_targeting = sum(
        (ex.skill_weights or {}).get(weak, 0.0) for ex in lesson.exercises
    )
    lesson_cefr = CEFR_ORDER.index(lesson.cefr_level) if lesson.cefr_level in CEFR_ORDER else 0
    cefr_penalty = 0.0
    if lesson_cefr > user_cefr + 1:
        cefr_penalty = -10.0  # too hard for now
    elif lesson_cefr < user_cefr:
        cefr_penalty = -1.0  # a bit too easy
    return topic_overlap * 2.0 + weak_targeting * 1.5 + cefr_penalty


def choose_next_lesson(
    db: Session, user: User, exclude_lesson_id: int | None = None
) -> Lesson | None:
    """Pick the published lesson that best targets the user's weakest skills
    and interests at an appropriate CEFR level."""
    lessons = db.scalars(
        select(Lesson).where(Lesson.status == "published").order_by(Lesson.id)
    ).all()
    if not lessons:
        return None
    candidates = [l for l in lessons if l.id != exclude_lesson_id] or lessons
    weak = weakest_skill(db, user)
    user_cefr = _user_cefr_index(db, user)
    return max(
        candidates,
        key=lambda lesson: (_lesson_score(db, user, lesson, weak, user_cefr), -lesson.id),
    )


def _recent_failed_exercises(db: Session, user: User, limit: int = 20) -> list[Exercise]:
    attempts = db.scalars(
        select(Attempt)
        .where(Attempt.user_id == user.id, Attempt.correct.is_(False))
        .order_by(Attempt.created_at.desc())
        .limit(limit)
    ).all()
    seen: set[int] = set()
    exercises: list[Exercise] = []
    for attempt in attempts:
        if attempt.exercise_id in seen:
            continue
        exercise = db.get(Exercise, attempt.exercise_id)
        if exercise is not None:
            seen.add(exercise.id)
            exercises.append(exercise)
    return exercises


def concept_chips(db: Session, user: User) -> list[str]:
    """Concept chips derived from recently failed exercises (lesson topics +
    skill area), e.g. ["planes", "la gramática", "viajes"]."""
    chips: list[str] = []
    for exercise in _recent_failed_exercises(db, user):
        lesson = db.get(Lesson, exercise.lesson_id)
        for topic in (lesson.topics if lesson else []) or []:
            if topic not in chips:
                chips.append(topic)
        label = _TYPE_LABELS.get(exercise.type)
        if label and label not in chips:
            chips.append(label)
    return chips[:5]


def adaptive_note(db: Session, user: User) -> str:
    """Short coaching note, e.g. 'Necesitas más práctica con la gramática y
    el vocabulario de planes.'"""
    chips = concept_chips(db, user)
    if not chips:
        return "Vas muy bien: seguimos subiendo el ritmo con cosas nuevas."
    if len(chips) == 1:
        concepts = chips[0]
    else:
        concepts = ", ".join(chips[:-1]) + " y " + chips[-1]
    return f"Necesitas más práctica con {concepts}."


def next_suggestion(db: Session, user: User, exclude_lesson_id: int | None = None) -> dict:
    """The 'next' payload for /api/path/today: {label, description, topics}."""
    lesson = choose_next_lesson(db, user, exclude_lesson_id=exclude_lesson_id)
    if lesson is None:
        return {"label": "Siguiente: repaso", "description": adaptive_note(db, user), "topics": []}
    return {
        "label": f"Siguiente: {lesson.title}",
        "description": adaptive_note(db, user),
        "topics": lesson.topics or [],
    }
