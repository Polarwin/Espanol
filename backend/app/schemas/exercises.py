"""Exercise attempt schemas."""

from pydantic import BaseModel


class AttemptRequest(BaseModel):
    answer: str


class SkillUpdate(BaseModel):
    skill: str
    delta: float


class AttemptResponse(BaseModel):
    correct: bool
    score: float
    feedback: str
    skill_updates: list[SkillUpdate]
