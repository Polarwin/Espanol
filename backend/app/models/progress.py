"""Per-user progress: skills, attempts, review items, streaks, goals, recaps."""

from datetime import date, datetime

from sqlalchemy import JSON, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base

SKILLS = ("pronunciation", "vocabulary", "grammar", "writing", "listening", "reading", "fluency")


class SkillProgress(Base):
    __tablename__ = "skill_progress"
    __table_args__ = (UniqueConstraint("user_id", "skill", name="uq_skill_progress_user_skill"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    skill: Mapped[str]  # one of SKILLS
    score: Mapped[float] = mapped_column(default=0.0)  # 0-100
    level: Mapped[str] = mapped_column(default="A1")  # e.g. "A1", "A2"
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), index=True)
    answer: Mapped[str] = mapped_column(Text)
    correct: Mapped[bool]
    score: Mapped[float]  # 0-1
    feedback: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class LessonCompletion(Base):
    __tablename__ = "lesson_completions"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_lesson_completion"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    completed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class ReviewItem(Base):
    """SM-2 spaced-repetition item. Scheduling logic arrives in a later phase."""

    __tablename__ = "review_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str]  # "vocabulary" | "grammar" | "pronunciation"
    content: Mapped[dict] = mapped_column(JSON, default=dict)  # {word, translation} | {concept, example}
    easiness: Mapped[float] = mapped_column(default=2.5)
    interval_days: Mapped[int] = mapped_column(default=1)
    repetitions: Mapped[int] = mapped_column(default=0)
    due_date: Mapped[date]
    last_reviewed: Mapped[date | None] = mapped_column(nullable=True)


class Streak(Base):
    __tablename__ = "streaks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    current_days: Mapped[int] = mapped_column(default=0)
    longest_days: Mapped[int] = mapped_column(default=0)
    last_activity_date: Mapped[date | None] = mapped_column(nullable=True)
    recovery_days_used: Mapped[int] = mapped_column(default=0)  # resets weekly


class WeeklyGoal(Base):
    __tablename__ = "weekly_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    week_start: Mapped[date]
    # "lessons" | "listening_minutes" | "sentences_spoken" | "writing_responses"
    kind: Mapped[str]
    target: Mapped[int]
    current: Mapped[int] = mapped_column(default=0)
    # True for the goal the learner chose to display (one per user/week).
    selected: Mapped[bool] = mapped_column(default=False)


class WeeklyRecap(Base):
    __tablename__ = "weekly_recaps"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    week_start: Mapped[date]
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
