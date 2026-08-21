"""Weekly recap: compute and store the week's learning summary."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Attempt, Exercise, Lesson, User, WeeklyGoal, WeeklyRecap
from . import adaptive
from .goals import goal_label
from .scoring import FAILURE_DELTA, SUCCESS_DELTA
from .spaced_review import week_start_of

SKILL_LABELS = {
    "pronunciation": "Pronunciación",
    "vocabulary": "Vocabulario",
    "grammar": "Gramática",
    "writing": "Escritura",
    "listening": "Comprensión",
    "reading": "Lectura",
    "fluency": "Fluidez",
}

MINUTES_PER_ATTEMPT = 2  # rough practice-time estimate per exercise attempt


def _week_attempts(db: Session, user: User, week_start: date) -> list[Attempt]:
    week_end = week_start.fromordinal(week_start.toordinal() + 7)
    return list(
        db.scalars(
            select(Attempt).where(
                Attempt.user_id == user.id,
                func.date(Attempt.created_at) >= week_start,
                func.date(Attempt.created_at) < week_end,
            )
        )
    )


def _weekly_skill_deltas(attempts: list[Attempt], db: Session) -> dict[str, float]:
    """Reconstruct per-skill score deltas from this week's attempts."""
    deltas: dict[str, float] = {}
    for attempt in attempts:
        exercise = db.get(Exercise, attempt.exercise_id)
        if exercise is None:
            continue
        for skill, weight in (exercise.skill_weights or {}).items():
            if attempt.correct:
                delta = SUCCESS_DELTA * weight * attempt.score
            else:
                delta = FAILURE_DELTA * weight
            deltas[skill] = round(deltas.get(skill, 0.0) + delta, 2)
    return deltas


def build_recap(db: Session, user: User, today: date | None = None) -> dict:
    """Compute the recap for the current ISO week (also used for storage)."""
    week_start = week_start_of(today or date.today())
    attempts = _week_attempts(db, user, week_start)

    minutes = len(attempts) * MINUTES_PER_ATTEMPT

    lessons_goal = db.scalar(
        select(WeeklyGoal).where(
            WeeklyGoal.user_id == user.id,
            WeeklyGoal.week_start == week_start,
            WeeklyGoal.kind == "lessons",
        )
    )
    lessons_completed = lessons_goal.current if lessons_goal else 0

    # One bulk fetch instead of a per-attempt db.get(Exercise, …).
    exercises_by_id = (
        {
            exercise.id: exercise
            for exercise in db.scalars(
                select(Exercise).where(
                    Exercise.id.in_({a.exercise_id for a in attempts})
                )
            )
        }
        if attempts
        else {}
    )
    vocab_exercise_ids = {
        a.exercise_id
        for a in attempts
        if a.correct
        and (exercise := exercises_by_id.get(a.exercise_id)) is not None
        and exercise.type == "vocabulary"
    }
    words_learned = len(vocab_exercise_ids)

    deltas = _weekly_skill_deltas(attempts, db)
    improvements = [
        {"skill": skill, "label": SKILL_LABELS.get(skill, skill), "delta": delta}
        for skill, delta in sorted(deltas.items(), key=lambda kv: kv[1], reverse=True)
        if delta > 0
    ]

    achievement = _achievement(db, user, lessons_completed, words_learned, week_start)
    recommendation = _recommendation(db, user)

    return {
        "minutes": minutes,
        "lessons_completed": lessons_completed,
        "words_learned": words_learned,
        "improvements": improvements,
        "achievement": achievement,
        "recommendation": recommendation,
    }


def _achievement(db: Session, user: User, lessons_completed: int, words_learned: int, week_start: date) -> str:
    if lessons_completed > 0:
        lesson = db.scalar(
            select(Lesson)
            .join(Exercise, Exercise.lesson_id == Lesson.id)
            .join(Attempt, Attempt.exercise_id == Exercise.id)
            .where(Attempt.user_id == user.id, func.date(Attempt.created_at) >= week_start)
            .order_by(Attempt.created_at.desc())
            .limit(1)
        )
        level = lesson.cefr_level if lesson else "A2"
        if lessons_completed == 1:
            return f"Entendiste una conversación {level} completa"
        return f"Completaste {lessons_completed} lecciones esta semana"
    if words_learned > 0:
        return f"Aprendiste {words_learned} palabras útiles esta semana"
    return "Diste el primer paso: practicar un poco ya cuenta"


def _recommendation(db: Session, user: User) -> str:
    weak = adaptive.weakest_skill(db, user)
    weak_label = SKILL_LABELS.get(weak, weak).lower()
    lesson = adaptive.choose_next_lesson(db, user)
    if lesson and lesson.topics:
        topics = " y ".join(lesson.topics)
        return f"La próxima semana practicaremos {weak_label} con lecciones de {topics}"
    return f"La próxima semana practicaremos {weak_label} con lecciones nuevas"


def get_or_store_recap(db: Session, user: User, today: date | None = None) -> dict:
    """Build the recap and persist it in weekly_recaps (one row per user/week)."""
    today = today or date.today()
    week_start = week_start_of(today)
    data = build_recap(db, user, today)
    recap = db.scalar(
        select(WeeklyRecap).where(
            WeeklyRecap.user_id == user.id, WeeklyRecap.week_start == week_start
        )
    )
    if recap is None:
        recap = WeeklyRecap(user_id=user.id, week_start=week_start, data=data)
        db.add(recap)
    else:
        recap.data = data
    db.flush()
    return data
