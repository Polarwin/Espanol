"""Core-loop (/api/path/today) schemas."""

from typing import Literal

from pydantic import BaseModel

from .lessons import TranscriptLine

LoopStep = Literal["mira", "escucha", "habla", "adapta"]


class PathLesson(BaseModel):
    id: int
    title: str
    cefr_level: str
    topics: list[str]


class LoopFeedback(BaseModel):
    pronunciation: float
    fluidez: float
    gramatica: float


class PronunciationTip(BaseModel):
    phrase: str
    tip: str


class GrammarTip(BaseModel):
    wrong: str
    right: str
    explanation: str


class NextSuggestion(BaseModel):
    lesson_id: int | None = None
    label: str
    description: str
    topics: list[str]


class PathToday(BaseModel):
    lesson: PathLesson
    step: LoopStep
    clip_index: int
    total_clips: int
    video_url: str
    subtitle: TranscriptLine
    feedback: LoopFeedback
    pronunciation_tip: PronunciationTip
    grammar_tip: GrammarTip
    next: NextSuggestion
