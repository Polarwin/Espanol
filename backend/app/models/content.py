"""Lesson content: lessons, segments, phrases, exercises."""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ..services.time import utc_now


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    cefr_level: Mapped[str]
    topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(default="local")  # "local" | "online_reviewed"
    status: Mapped[str] = mapped_column(default="published")  # "published" | "draft" | "review"
    duration_seconds: Mapped[int] = mapped_column(default=0)
    video_path: Mapped[str] = mapped_column(default="")  # relative to content_dir
    # Default grammar tip for the core loop, e.g.
    # {"wrong": "...", "right": "...", "explanation": "..."}
    grammar_tip: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    segments: Mapped[list["Segment"]] = relationship(
        back_populates="lesson", order_by="Segment.index", cascade="all, delete-orphan"
    )
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="lesson", order_by="Exercise.order_index", cascade="all, delete-orphan"
    )


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    index: Mapped[int]
    start_seconds: Mapped[float]
    end_seconds: Mapped[float]
    transcript: Mapped[list[dict]] = mapped_column(JSON, default=list)  # [{"es": ..., "en": ...}]

    lesson: Mapped[Lesson] = relationship(back_populates="segments")
    phrases: Mapped[list["Phrase"]] = relationship(
        back_populates="segment", order_by="Phrase.id", cascade="all, delete-orphan"
    )


class Phrase(Base):
    __tablename__ = "phrases"

    id: Mapped[int] = mapped_column(primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), index=True)
    text: Mapped[str]
    translation: Mapped[str]
    tip: Mapped[str | None] = mapped_column(nullable=True)  # pronunciation tip

    segment: Mapped[Segment] = relationship(back_populates="phrases")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    type: Mapped[str]  # "vocabulary" | "grammar" | "writing" | "listening" | "pronunciation" | "reading"
    instructions: Mapped[str]
    prompt: Mapped[str] = mapped_column(Text)
    passage: Mapped[str | None] = mapped_column(Text, nullable=True)  # reading text
    audio_path: Mapped[str | None] = mapped_column(nullable=True)  # relative to content_dir
    options: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    expected_answer: Mapped[str] = mapped_column(Text)
    skill_weights: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    order_index: Mapped[int] = mapped_column(default=0)

    lesson: Mapped[Lesson] = relationship(back_populates="exercises")
