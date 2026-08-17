"""Placement-test request and response schemas."""

from pydantic import BaseModel


class PlacementQuestion(BaseModel):
    id: str
    skill: str
    prompt: str
    options: list[str]
    passage: str | None = None
    audio_url: str | None = None


class PlacementSubmission(BaseModel):
    answers: dict[str, str]


class PlacementGradeSubmission(BaseModel):
    level: str
    answers: dict[str, str]


class LevelSelection(BaseModel):
    level: str


class PlacementGradeResult(BaseModel):
    level: str
    correct: int
    total: int
    passed: bool


class PlacementResult(BaseModel):
    overall_level: str
    skill_levels: dict[str, str]
    correct: int
    total: int
