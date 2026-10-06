from datetime import datetime

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from ..services.time import utc_now


class ReadingPractice(Base):
    __tablename__ = 'reading_practices'
    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    status: Mapped[str] = mapped_column(default='queued')
    stage: Mapped[str] = mapped_column(default='En espera')
    level: Mapped[str]
    source: Mapped[str]
    source_key: Mapped[str]
    source_title: Mapped[str]
    pack: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
