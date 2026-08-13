"""Weekly personal goals: labels, selection, and counter increments."""

from datetime import date

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..models import User, WeeklyGoal
from .spaced_review import week_start_of

GOAL_KINDS = ("lessons", "listening_minutes", "sentences_spoken", "writing_responses")

_NUMBERS_ES = {1: "una", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve", 10: "diez", 20: "veinte", 30: "treinta"}


def _num(n: int) -> str:
    return _NUMBERS_ES.get(n, str(n))


def goal_label(kind: str, target: int) -> str:
    n = _num(target)
    match kind:
        case "lessons":
            noun = "lección" if target == 1 else "lecciones"
            return f"Completa {n} {noun}"
        case "listening_minutes":
            return f"Practica {n} minutos de escucha"
        case "sentences_spoken":
            return f"Di {n} frases en español"
        case "writing_responses":
            return f"Escribe {n} respuestas"
        case _:
            return f"Objetivo: {n}"


def get_or_create_goal(
    db: Session, user: User, kind: str, target: int, week_start: date, selected: bool = False
) -> WeeklyGoal:
    goal = db.scalar(
        select(WeeklyGoal).where(
            WeeklyGoal.user_id == user.id,
            WeeklyGoal.week_start == week_start,
            WeeklyGoal.kind == kind,
        )
    )
    if goal is None:
        goal = WeeklyGoal(
            user_id=user.id, week_start=week_start, kind=kind, target=target, selected=selected
        )
        db.add(goal)
        db.flush()
    return goal


def selected_goal(db: Session, user: User, today: date | None = None) -> WeeklyGoal:
    """The goal to display for the current week, creating the default if needed."""
    week_start = week_start_of(today or date.today())
    goal = db.scalar(
        select(WeeklyGoal).where(
            WeeklyGoal.user_id == user.id,
            WeeklyGoal.week_start == week_start,
            WeeklyGoal.selected.is_(True),
        )
    )
    if goal is None:
        goal = get_or_create_goal(db, user, "lessons", 3, week_start, selected=True)
    return goal


def choose_goal(db: Session, user: User, kind: str, target: int, today: date | None = None) -> WeeklyGoal:
    week_start = week_start_of(today or date.today())
    db.execute(
        update(WeeklyGoal)
        .where(WeeklyGoal.user_id == user.id, WeeklyGoal.week_start == week_start)
        .values(selected=False)
    )
    goal = get_or_create_goal(db, user, kind, target, week_start)
    goal.target = target
    goal.selected = True
    db.flush()
    return goal


def increment_goal(db: Session, user: User, kind: str, amount: int = 1, today: date | None = None) -> None:
    """Increment the counter for a goal kind this week (created lazily if missing).

    New lazily-created rows keep selected=False so they never replace the
    learner's chosen display goal.
    """
    week_start = week_start_of(today or date.today())
    goal = db.scalar(
        select(WeeklyGoal).where(
            WeeklyGoal.user_id == user.id,
            WeeklyGoal.week_start == week_start,
            WeeklyGoal.kind == kind,
        )
    )
    if goal is None:
        goal = WeeklyGoal(user_id=user.id, week_start=week_start, kind=kind, target=0)
        db.add(goal)
        db.flush()
    goal.current += amount
    db.flush()


def goal_payload(goal: WeeklyGoal) -> dict:
    return {"label": goal_label(goal.kind, goal.target), "current": goal.current, "target": goal.target}
