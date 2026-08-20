"""Lesson routes: list, detail, assessment."""

import math

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Exercise, Lesson, LessonCompletion, User
from ..schemas import (
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
from ..routers.path import media_url
from ..services.goals import increment_goal
from ..services.loop import get_or_create_state
from ..services.security import get_current_user
from ..services.streak import record_activity
from ..seed.vocabulary_content import VOCABULARY_BANKS

router = APIRouter(prefix="/api/lessons", tags=["lessons"])

# Assessment groups in this fixed order (pronunciation is practised in the
# "habla" loop step, not in the written assessment).
ASSESSMENT_TYPES: list[tuple[str, str]] = [
    ("vocabulary", "Vocabulario"),
    ("grammar", "Gramática"),
    ("reading", "Lectura"),
    ("writing", "Escritura"),
    ("listening", "Comprensión"),
]

MINUTES_PER_QUESTION = 1.5


def _spanish_vocabulary_support(lesson: Lesson, text: str) -> tuple[str, str]:
    """Give glossary items Spanish-first context without exposing English first."""
    topics = [topic for topic in lesson.topics if "vitamina" not in topic.lower()]
    topic = topics[0] if topics else "esta unidad"
    lowered = text.lower()
    if text.startswith("¿"):
        kind = "Una pregunta útil"
    elif lowered.startswith(("el ", "la ", "los ", "las ", "un ", "una ")):
        kind = "Una palabra que nombra algo"
    elif lowered.split(" ", 1)[0].endswith(("ar", "er", "ir", "arse", "erse", "irse")):
        kind = "Una acción"
    else:
        kind = "Una expresión útil"
    if lesson.cefr_level == "A1":
        definition = f"{kind} para hablar de {topic}."
    else:
        definition = f"{kind} que usamos en situaciones relacionadas con {topic}."

    example = ""
    for segment in lesson.segments:
        for line in segment.transcript:
            if lowered.strip("¿?¡!") in line.get("es", "").lower():
                example = line["es"]
                break
        if example:
            break
    if not example:
        example = f"En esta unidad usamos «{text}» para hablar de {topic}."
    return definition, example


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


@router.post("/{lesson_id}/select")
def select_lesson(
    lesson_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Remember a catalog choice as this learner's current unit."""
    lesson = db.get(Lesson, lesson_id)
    if lesson is None or lesson.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    state = get_or_create_state(db, user, lesson)
    if state.current_lesson_id != lesson.id:
        state.current_lesson_id = lesson.id
        state.current_step = "mira"
        state.current_clip_index = 0
    db.commit()
    return {"selected": True, "lesson_id": lesson.id}


@router.get("/{lesson_id}", response_model=LessonDetail)
def lesson_detail(
    lesson_id: int,
    variation: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LessonDetail:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None or lesson.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    name = (user.nickname or user.display_name).strip()
    interests = user.interests or lesson.topics or ["español"]
    variant = (user.id * 7 + lesson.id * 3 + variation) % 4
    missions = [
        "Escucha primero sin traducir cada palabra; busca la idea principal.",
        "Fíjate en la entonación y repite dos frases con el mismo ritmo.",
        "Busca tres palabras que podrías usar esta semana en una conversación real.",
        "Escucha cómo empieza y termina cada intervención del diálogo.",
    ]
    challenges = [
        "Resume el diálogo en dos frases con tus propias palabras.",
        "Cambia un detalle del diálogo para que se parezca a tu vida.",
        "Imagina que eres uno de los personajes y responde en voz alta.",
        "Usa una frase clave hoy con un compañero o vecino.",
    ]
    all_phrases = [phrase.text for segment in lesson.segments for phrase in segment.phrases]
    focus_phrase = all_phrases[variant % len(all_phrases)] if all_phrases else lesson.title
    return LessonDetail(
        id=lesson.id,
        title=lesson.title,
        cefr_level=lesson.cefr_level,
        topics=lesson.topics,
        source=lesson.source,
        duration_seconds=lesson.duration_seconds,
        video_url=media_url(lesson.video_path) or "",
        personal_welcome=f"{name}, hoy conectamos «{lesson.title}» con tu interés por {interests[variant % len(interests)]}.",
        session_mission=missions[variant],
        closing_challenge=challenges[variant],
        focus_phrase=focus_phrase,
        vocabulary=[
            VocabularyItem(
                text=text,
                translation=translation,
                definition_es=_spanish_vocabulary_support(lesson, text)[0],
                example_es=_spanish_vocabulary_support(lesson, text)[1],
            )
            for text, translation in VOCABULARY_BANKS.get(lesson.title, [])
        ],
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
                    for phrase in (segment.phrases[variant % len(segment.phrases):] + segment.phrases[:variant % len(segment.phrases)] if segment.phrases else [])
                ],
            )
            for segment in lesson.segments
        ],
    )


@router.post("/{lesson_id}/complete")
def complete_lesson(
    lesson_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, int | bool]:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None or lesson.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    completion = db.scalar(
        select(LessonCompletion).where(
            LessonCompletion.user_id == user.id,
            LessonCompletion.lesson_id == lesson_id,
        )
    )
    created = completion is None
    if created:
        db.add(LessonCompletion(user_id=user.id, lesson_id=lesson_id))
        increment_goal(db, user, "lessons")
        record_activity(db, user)
    db.commit()
    total = db.scalar(
        select(func.count()).select_from(LessonCompletion).where(
            LessonCompletion.user_id == user.id
        )
    ) or 0
    return {"saved": True, "new_completion": created, "lessons_completed_total": total}


@router.get("/{lesson_id}/assessment", response_model=Assessment)
def lesson_assessment(lesson_id: int, db: Session = Depends(get_db)) -> Assessment:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None or lesson.status != "published":
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
        passage=exercise.passage,
        audio_url=media_url(exercise.audio_path),
        options=exercise.options,
    )
