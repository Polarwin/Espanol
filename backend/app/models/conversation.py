from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base


class ConversationSession(Base):
    __tablename__ = 'conversation_sessions'
    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id'))
    turn: Mapped[int] = mapped_column(default=0)
    history: Mapped[list] = mapped_column(JSON, default=list)
    last_request: Mapped[str | None]
    last_result: Mapped[dict | None] = mapped_column(JSON)
