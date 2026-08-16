"""Skill-progress helpers: defaults for new users and clamped updates."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import SkillProgress, User

# Fixed starting scores (0-100) so the core-loop feedback panel has sensible
# values for brand-new users.
DEFAULT_SKILL_SCORES: dict[str, float] = {
    "pronunciation": 82.0,
    "fluency": 74.0,
    "grammar": 90.0,
    "vocabulary": 70.0,
    "writing": 65.0,
    "listening": 75.0,
    "reading": 72.0,
}

MIN_SCORE = 0.0
MAX_SCORE = 100.0


def init_skill_progress(db: Session, user: User) -> None:
    """Create one skill_progress row per skill with the default scores."""
    for skill, score in DEFAULT_SKILL_SCORES.items():
        db.add(SkillProgress(user_id=user.id, skill=skill, score=score, level="A1"))
    db.flush()


def apply_skill_deltas(db: Session, user: User, deltas: dict[str, float]) -> list[dict]:
    """Apply signed deltas to skill scores, clamped to 0-100.

    Returns the applied updates as [{"skill": ..., "delta": ...}].
    """
    updates: list[dict] = []
    if not deltas:
        return updates
    rows = {
        row.skill: row
        for row in db.scalars(
            select(SkillProgress).where(
                SkillProgress.user_id == user.id, SkillProgress.skill.in_(list(deltas))
            )
        )
    }
    for skill, delta in deltas.items():
        row = rows.get(skill)
        if row is None:
            row = SkillProgress(user_id=user.id, skill=skill, score=0.0, level="A1")
            db.add(row)
        applied = round(delta, 2)
        row.score = max(MIN_SCORE, min(MAX_SCORE, row.score + applied))
        row.updated_at = datetime.utcnow()
        updates.append({"skill": skill, "delta": applied})
    db.flush()
    return updates


def get_skill_scores(db: Session, user: User) -> dict[str, float]:
    rows = db.scalars(select(SkillProgress).where(SkillProgress.user_id == user.id)).all()
    return {row.skill: row.score for row in rows}
