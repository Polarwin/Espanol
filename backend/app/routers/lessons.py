"""Lesson routes: list, detail, assessment."""

import math

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Exercise, Lesson
from ..schemas import (
    Assessment,
    AssessmentExercise,
    AssessmentGroup,
    LessonDetail,
    LessonListItem,
    PhraseOut,
    SegmentOut,
    TranscriptLine,
)
from ..routers.path import media_url

router = APIRouter(prefix="/api/lessons", tags=["lessons"])

# Assessment groups in this fixed order (pronunciation is practised in the
# "habla" loop step, not in the written assessment).
ASSESSMENT_TYPES: list[tuple[str, str]] = [
    ("vocabulary", "Vocabulario"),
    ("grammar", "Gramática"),
    ("writing", "Escritura"),
    ("listening", "Comprensión"),
]

MINUTES_PER_QUESTION = 1.5


@router.get("", response_model=list[LessonListItem])
def list_lessons(db: Session = Depends(get_db)) -> list[LessonListItem]:
    lessons = db.scalars(
        select(Lesson).where(Lesson.status == "published").order_by(Lesson.id)
    ).all()
    return [
        LessonListItem(
            id=lesson.id,
            title=lesson.title,
            cefr_level=lesson.cefr_level,
            topics=lesson.topics,
            source=lesson.source,
            duration_seconds=lesson.duration_seconds,
        )
        for lesson in lessons
    ]


@router.get("/{lesson_id}", response_model=LessonDetail)
def lesson_detail(lesson_id: int, db: Session = Depends(get_db)) -> LessonDetail:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return LessonDetail(
        id=lesson.id,
        title=lesson.title,
        cefr_level=lesson.cefr_level,
        topics=lesson.topics,
        source=lesson.source,
        duration_seconds=lesson.duration_seconds,
        video_url=media_url(lesson.video_path) or "",
        segments=[
            SegmentOut(
                id=segment.id,
                index=segment.index,
                video_url=media_url(lesson.video_path) or "",
                start_seconds=segment.start_seconds,
                end_seconds=segment.end_seconds,
                transcript=[TranscriptLine.model_validate(line) for line in segment.transcript],
                phrases=[
                    PhraseOut(id=phrase.id, text=phrase.text, translation=phrase.translation)
                    for phrase in segment.phrases
                ],
            )
            for segment in lesson.segments
        ],
    )


@router.get("/{lesson_id}/assessment", response_model=Assessment)
def lesson_assessment(lesson_id: int, db: Session = Depends(get_db)) -> Assessment:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    groups: list[AssessmentGroup] = []
    total_questions = 0
    for ex_type, label in ASSESSMENT_TYPES:
        exercises = [ex for ex in lesson.exercises if ex.type == ex_type]
        if not exercises:
            continue
        total_questions += len(exercises)
        groups.append(
            AssessmentGroup(
                type=ex_type,
                label=label,
                instructions=exercises[0].instructions,
                exercises=[_assessment_exercise(ex) for ex in exercises],
            )
        )
    return Assessment(
        duration_minutes=max(5, math.ceil(total_questions * MINUTES_PER_QUESTION)),
        total_questions=total_questions,
        groups=groups,
    )


def _assessment_exercise(exercise: Exercise) -> AssessmentExercise:
    return AssessmentExercise(
        id=exercise.id,
        prompt=exercise.prompt,
        audio_url=media_url(exercise.audio_path),
        options=exercise.options,
    )
