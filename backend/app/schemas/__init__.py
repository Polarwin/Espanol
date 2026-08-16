"""Pydantic schemas mirroring the frontend API contract."""

from .auth import AuthResponse, LoginRequest, ProfileUpdate, RegisterRequest, UserOut
from .exercises import AttemptRequest, AttemptResponse, SkillUpdate
from .lessons import (
    Assessment,
    AssessmentExercise,
    AssessmentGroup,
    LessonDetail,
    LessonListItem,
    PhraseOut,
    SegmentOut,
    TranscriptLine,
    VocabularyItem,
)
from .path import (
    ClipQuiz,
    ClipQuizResult,
    GrammarTip,
    LoopFeedback,
    NextSuggestion,
    PathLesson,
    PathToday,
    PronunciationTip,
)

__all__ = [
    "Assessment",
    "AssessmentExercise",
    "AssessmentGroup",
    "AttemptRequest",
    "AttemptResponse",
    "AuthResponse",
    "ClipQuiz",
    "ClipQuizResult",
    "GrammarTip",
    "LessonDetail",
    "LessonListItem",
    "LoginRequest",
    "LoopFeedback",
    "NextSuggestion",
    "PathLesson",
    "PathToday",
    "PhraseOut",
    "PronunciationTip",
    "ProfileUpdate",
    "RegisterRequest",
    "SegmentOut",
    "SkillUpdate",
    "TranscriptLine",
    "UserOut",
    "VocabularyItem",
]
