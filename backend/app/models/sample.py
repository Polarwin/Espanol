from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base


class A2SampleProgress(Base):
    __tablename__ = 'a2_sample_progress'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)


class VocabularyJourney(Base):
    __tablename__ = 'a2_vocabulary_journey'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    revision: Mapped[int] = mapped_column(default=0)
    last_request: Mapped[str | None]
