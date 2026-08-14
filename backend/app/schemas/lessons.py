"""Lesson and assessment schemas."""

from pydantic import BaseModel


class TranscriptLine(BaseModel):
    es: str
    en: str


class LessonListItem(BaseModel):
    id: int
    title: str
    cefr_level: str
    topics: list[str]
    source: str
    duration_seconds: int


class PhraseOut(BaseModel):
    id: int
    text: str
    translation: str


class VocabularyItem(BaseModel):
    text: str
    translation: str


class SegmentOut(BaseModel):
    id: int
    index: int
    video_url: str
    start_seconds: float
    end_seconds: float
    transcript: list[TranscriptLine]
    phrases: list[PhraseOut]


class LessonDetail(BaseModel):
    id: int
    title: str
    cefr_level: str
    topics: list[str]
    source: str
    duration_seconds: int
    video_url: str
    personal_welcome: str
    session_mission: str
    closing_challenge: str
    focus_phrase: str
    vocabulary: list[VocabularyItem]
    segments: list[SegmentOut]


class AssessmentExercise(BaseModel):
    id: int
    prompt: str
    audio_url: str | None
    options: list[str] | None


class AssessmentGroup(BaseModel):
    type: str
    label: str
    instructions: str
    exercises: list[AssessmentExercise]


class Assessment(BaseModel):
    duration_minutes: int
    total_questions: int
    groups: list[AssessmentGroup]
