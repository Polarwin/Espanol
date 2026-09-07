"""Exercise attempt schemas."""

from pydantic import BaseModel, Field
from ..services.ai.contracts import Correction


class AttemptRequest(BaseModel):
    answer: str = Field(max_length=2000)


class SkillUpdate(BaseModel):
    skill: str
    delta: float


class AttemptResponse(BaseModel):
    correct: bool
    score: float
    feedback: str
    skill_updates: list[SkillUpdate]
    correction: Correction | None = None
