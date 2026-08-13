"""Placement-test request and response schemas."""

from pydantic import BaseModel


class PlacementQuestion(BaseModel):
    id: str
    skill: str
    prompt: str
    options: list[str]


class PlacementSubmission(BaseModel):
    answers: dict[str, str]


class PlacementResult(BaseModel):
    overall_level: str
    skill_levels: dict[str, str]
    correct: int
    total: int
