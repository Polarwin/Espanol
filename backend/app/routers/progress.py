"""Authenticated progress and weekly recap routes."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import SkillProgress, User
from ..schemas.progress import ProgressOut, WeeklyRecapOut
from ..services.goals import goal_payload, selected_goal
from ..services.recap import get_or_store_recap
from ..services.security import get_current_user
from ..services.streak import MAX_RECOVERY_DAYS_PER_WEEK, get_or_create_streak

router = APIRouter(tags=["progress"])

LABELS = {
    "pronunciation": "Pronunciación", "fluency": "Fluidez", "grammar": "Gramática",
    "vocabulary": "Vocabulario", "listening": "Comprensión auditiva", "writing": "Escritura",
}


@router.get("/api/progress", response_model=ProgressOut)
def progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    skills = db.scalars(select(SkillProgress).where(SkillProgress.user_id == user.id)).all()
    streak = get_or_create_streak(db, user)
    goal = selected_goal(db, user)
    db.commit()
    return {
        "skills": [{"skill": s.skill, "label": LABELS.get(s.skill, s.skill), "score": s.score} for s in skills],
        "streak": {"days": streak.current_days, "recovery_days_left": max(0, MAX_RECOVERY_DAYS_PER_WEEK - streak.recovery_days_used)},
        "weekly_goal": goal_payload(goal),
    }


@router.get("/api/recap/weekly", response_model=WeeklyRecapOut)
def weekly_recap(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    data = get_or_store_recap(db, user)
    db.commit()
    return data
