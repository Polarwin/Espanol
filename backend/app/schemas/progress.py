"""Progress and weekly recap API schemas."""

from pydantic import BaseModel


class SkillScoreOut(BaseModel):
    skill: str
    label: str
    score: float


class StreakOut(BaseModel):
    days: int
    recovery_days_left: int


class GoalOut(BaseModel):
    label: str
    current: int
    target: int


class ProgressOut(BaseModel):
    skills: list[SkillScoreOut]
    streak: StreakOut
    weekly_goal: GoalOut
    lessons_completed_total: int
    completed_lesson_ids: list[int]


class ImprovementOut(BaseModel):
    skill: str
    label: str
    delta: float


class WeeklyRecapOut(BaseModel):
    minutes: int
    lessons_completed: int
    words_learned: int
    improvements: list[ImprovementOut]
    achievement: str
    recommendation: str
