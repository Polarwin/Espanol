"""Core loop route: GET /api/path/today."""

import random
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Attempt, Exercise, Lesson, Segment, User
from ..schemas import (
    ClipQuiz,
    ClipQuizResult,
    CaptionCue,
    GrammarTip,
    LoopFeedback,
    NextSuggestion,
    PathLesson,
    PathToday,
    PronunciationTip,
    TranscriptLine,
)
from ..services import adaptive
from ..services.loop import advance_state, get_or_create_state
from ..services.progress import DEFAULT_SKILL_SCORES, get_skill_scores
from ..services.security import get_current_user
from ..services.streak import record_activity

router = APIRouter(prefix="/api/path", tags=["path"])


class AdvancePathRequest(BaseModel):
    step: Literal["mira", "escucha", "comprueba", "habla", "adapta", "conversa"]


class ClipQuizAnswer(BaseModel):
    choice: str

_DEFAULT_PRONUNCIATION_TIP = PronunciationTip(phrase="fin de semana", tip="Suaviza la d entre vocales")
_DEFAULT_GRAMMAR_TIP = GrammarTip(
    wrong="¿Qué planes tú tienes?",
    right="¿Qué planes tienes?",
    explanation="El pronombre no es necesario aquí.",
)


def media_url(path: str | None) -> str | None:
    return f"/media/{path}" if path else None


@router.get("/today", response_model=PathToday)
def path_today(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PathToday:
    state = get_or_create_state(db, user, adaptive.choose_next_lesson(db, user))
    lesson = db.get(Lesson, state.current_lesson_id) if state.current_lesson_id else None
    if lesson is None:
        lesson = adaptive.choose_next_lesson(db, user)
        if lesson is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No lessons available"
            )
        state.current_lesson_id = lesson.id
        state.current_step = "mira"
        state.current_clip_index = 0
        db.commit()

    segments = lesson.segments
    total_clips = len(segments)
    clip_index = min(state.current_clip_index, max(total_clips - 1, 0))
    segment: Segment | None = segments[clip_index] if segments else None

    subtitle = TranscriptLine(es="", en="")
    if segment is not None and segment.transcript:
        subtitle = TranscriptLine.model_validate(segment.transcript[0])
    captions: list[CaptionCue] = []
    if segment is not None and segment.transcript:
        span = max(0.2, segment.end_seconds - segment.start_seconds)
        captions = [
            CaptionCue(
                start=segment.start_seconds + (index * span) / len(segment.transcript),
                end=segment.start_seconds + ((index + 1) * span) / len(segment.transcript),
                text=line["es"],
            )
            for index, line in enumerate(segment.transcript)
        ]

    scores = get_skill_scores(db, user)
    feedback = LoopFeedback(
        pronunciation=scores.get("pronunciation", DEFAULT_SKILL_SCORES["pronunciation"]),
        fluidez=scores.get("fluency", DEFAULT_SKILL_SCORES["fluency"]),
        gramatica=scores.get("grammar", DEFAULT_SKILL_SCORES["grammar"]),
    )

    quiz_data = _clip_quiz(db, lesson, clip_index) if state.current_step == "comprueba" else None

    return PathToday(
        lesson=PathLesson(
            id=lesson.id, title=lesson.title, cefr_level=lesson.cefr_level, topics=lesson.topics
        ),
        step=state.current_step,  # type: ignore[arg-type]
        clip_index=clip_index,
        total_clips=total_clips,
        video_url=media_url(lesson.video_path) or "",
        subtitle=subtitle,
        captions=captions,
        clip_start=segment.start_seconds if segment else 0,
        clip_end=segment.end_seconds if segment else lesson.duration_seconds,
        quiz=ClipQuiz(**quiz_data) if quiz_data else None,
        feedback=feedback,
        pronunciation_tip=_pronunciation_tip(lesson, segment),
        grammar_tip=_grammar_tip(db, user, lesson),
        next=NextSuggestion.model_validate(
            adaptive.next_suggestion(db, user, exclude_lesson_id=lesson.id)
        ),
    )


@router.post("/advance", response_model=PathToday)
def path_advance(
    payload: AdvancePathRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PathToday:
    """Complete the visible loop stage and return the newly active stage.

    The expected stage makes retries and double taps idempotent: a stale tap
    returns the current path without skipping another stage.
    """
    state = get_or_create_state(db, user, adaptive.choose_next_lesson(db, user))
    if state.current_step == payload.step:
        next_lesson = None
        if state.current_step == "conversa":
            next_lesson = adaptive.choose_next_lesson(
                db, user, exclude_lesson_id=state.current_lesson_id
            )
        advance_state(db, user, next_lesson)
        record_activity(db, user)
        db.commit()
    return path_today(user, db)


@router.post("/quiz", response_model=ClipQuizResult)
def path_quiz(
    payload: ClipQuizAnswer,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClipQuizResult:
    """Check the answer to the current clip's comprehension quiz."""
    state = get_or_create_state(db, user, adaptive.choose_next_lesson(db, user))
    lesson = db.get(Lesson, state.current_lesson_id) if state.current_lesson_id else None
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lesson available")
    quiz_data = _clip_quiz(db, lesson, state.current_clip_index)
    if quiz_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No quiz available")
    correct = payload.choice == quiz_data["answer"]
    return ClipQuizResult(correct=correct, correct_answer=quiz_data["answer"])


def _clip_quiz(db: Session, lesson: Lesson, clip_index: int) -> dict | None:
    """Build a deterministic meaning-check quiz for the clip's first line.

    Options are English translations: the correct one plus two distractors from
    the same lesson (or, if needed, other lessons at the same level).
    """
    segments = lesson.segments
    if not segments:
        return None
    segment = segments[min(clip_index, len(segments) - 1)]
    if not segment.transcript:
        return None
    line = segment.transcript[0]
    correct = line["en"]

    pool: list[str] = []
    for seg in segments:
        for item in seg.transcript:
            if item["en"] != correct:
                pool.append(item["en"])
    if len(set(pool)) < 2:
        others = db.scalars(
            select(Lesson)
            .where(Lesson.cefr_level == lesson.cefr_level, Lesson.id != lesson.id)
            .order_by(Lesson.id)
        ).all()
        for other in others:
            for seg in other.segments:
                for item in seg.transcript:
                    if item["en"] != correct:
                        pool.append(item["en"])
            if len(set(pool)) >= 2:
                break

    distractors = list(dict.fromkeys(pool))[:2]
    if len(distractors) < 2:
        return None
    options = [correct, *distractors]
    random.Random(f"{lesson.id}:{clip_index}").shuffle(options)
    return {
        "prompt": f"¿Qué significa «{line['es']}»?",
        "options": options,
        "answer": correct,
    }


def _pronunciation_tip(lesson: Lesson, segment: Segment | None) -> PronunciationTip:
    candidates = (segment.phrases if segment else []) + [
        phrase for seg in lesson.segments for phrase in seg.phrases
    ]
    for phrase in candidates:
        if phrase.tip:
            return PronunciationTip(phrase=phrase.text, tip=phrase.tip)
    return _DEFAULT_PRONUNCIATION_TIP


def _grammar_tip(db: Session, user: User, lesson: Lesson) -> GrammarTip:
    """Most recent relevant grammar mistake, falling back to the lesson default."""
    attempt = db.scalar(
        select(Attempt)
        .join(Exercise, Attempt.exercise_id == Exercise.id)
        .where(
            Attempt.user_id == user.id,
            Attempt.correct.is_(False),
            Exercise.type == "grammar",
        )
        .order_by(Attempt.created_at.desc())
        .limit(1)
    )
    if attempt is not None:
        exercise = db.get(Exercise, attempt.exercise_id)
        if exercise is not None:
            mistake_lesson = db.get(Lesson, exercise.lesson_id)
            default = (mistake_lesson.grammar_tip if mistake_lesson else None) or {}
            return GrammarTip(
                wrong=exercise.prompt,
                right=exercise.expected_answer,
                explanation=default.get("explanation", "Repasa esta forma gramatical."),
            )
    if lesson.grammar_tip:
        return GrammarTip.model_validate(lesson.grammar_tip)
    return _DEFAULT_GRAMMAR_TIP
