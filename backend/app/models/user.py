"""User account and per-user loop state."""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    display_name: Mapped[str]
    nickname: Mapped[str | None] = mapped_column(nullable=True)
    interests: Mapped[list[str]] = mapped_column(JSON, default=list)
    placement_completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class UserState(Base):
    """Where the user currently is in the core loop (mira/escucha/habla/adapta)."""

    __tablename__ = "user_state"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    current_lesson_id: Mapped[int | None] = mapped_column(ForeignKey("lessons.id"), nullable=True)
    current_step: Mapped[str] = mapped_column(default="mira")
    current_clip_index: Mapped[int] = mapped_column(default=0)
    # True once the current clip's comprueba quiz has been answered correctly.
    quiz_passed: Mapped[bool] = mapped_column(default=False)
