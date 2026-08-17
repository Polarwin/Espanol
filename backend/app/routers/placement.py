"""Adaptive A1-B2 placement test sampled fresh from seeded lesson content.

Every block is drawn at random from the published exercises of that level
(grammar, vocabulary, reading with passage, listening with real audio), so no
two tests are the same and the test stays in sync with the seeded content.
"""

import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Exercise, Lesson, SkillProgress, User, UserState
from ..schemas.placement import (
    LevelSelection,
    PlacementGradeResult,
    PlacementGradeSubmission,
    PlacementQuestion,
    PlacementResult,
    PlacementSubmission,
)
from ..services import adaptive
from ..services.security import get_current_user
from .path import media_url

router = APIRouter(prefix="/api/placement", tags=["placement"])

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
PASS_RATIO = 0.7
SKILL_PASS_RATIO = 0.5
LEVEL_SCORES = {"A1": 40.0, "A2": 55.0, "B1": 70.0, "B2": 85.0, "C1": 92.0, "C2": 97.0}


def _pool(db: Session, level: str, skill: str) -> list[Exercise]:
    """Multiple-choice exercises of one skill at one level.

    Filtered in Python: some legacy rows store JSON ``null`` instead of SQL
    NULL, which ``isnot(None)`` would not catch.
    """
    rows = db.scalars(
        select(Exercise)
        .join(Lesson)
        .where(
            Lesson.cefr_level == level,
            Lesson.status == "published",
            Exercise.type == skill,
        )
    ).all()
    return [row for row in rows if row.options]


def _pick(rows: list[Exercise], count: int) -> list[Exercise]:
    return random.sample(rows, k=min(count, len(rows))) if rows else []


def _pick_reading(rows: list[Exercise], count: int) -> list[Exercise]:
    """Reading questions come in pairs sharing one passage — sample per lesson."""
    by_lesson: dict[int, list[Exercise]] = {}
    for row in rows:
        by_lesson.setdefault(row.lesson_id, []).append(row)
    if not by_lesson:
        return []
    group = random.choice(list(by_lesson.values()))
    return _pick(group, count)


def _sample_block(db: Session, level: str) -> list[dict]:
    rows = (
        _pick(_pool(db, level, "grammar"), 2)
        + _pick(_pool(db, level, "vocabulary"), 2)
        + _pick_reading(_pool(db, level, "reading"), 2)
        + _pick(_pool(db, level, "listening"), 2)
    )
    random.shuffle(rows)
    return [
        {
            "id": f"ex-{row.id}",
            "skill": row.type,
            "prompt": row.prompt,
            "options": row.options,
            "passage": row.passage if row.type == "reading" else None,
            "audio_url": media_url(row.audio_path) if row.type == "listening" else None,
        }
        for row in rows
    ]


def _grade(db: Session, answers: dict[str, str]) -> tuple[dict[str, list[bool]], dict[str, dict[str, list[bool]]], int, int]:
    """Recompute results from the DB so the client cannot inflate its level."""
    ids = [int(key[3:]) for key in answers if key.startswith("ex-") and key[3:].isdigit()]
    rows = (
        db.execute(select(Exercise, Lesson.cefr_level).join(Lesson).where(Exercise.id.in_(ids))).all()
        if ids
        else []
    )
    per_level: dict[str, list[bool]] = {}
    per_skill: dict[str, dict[str, list[bool]]] = {}
    correct = 0
    for exercise, level in rows:
        passed = answers[f"ex-{exercise.id}"] == exercise.expected_answer
        correct += int(passed)
        per_level.setdefault(level, []).append(passed)
        per_skill.setdefault(exercise.type, {}).setdefault(level, []).append(passed)
    return per_level, per_skill, correct, len(rows)


def _passed(results: list[bool], ratio: float) -> bool:
    return bool(results) and sum(results) / len(results) >= ratio


@router.get("", response_model=list[PlacementQuestion])
def questions(
    level: str = Query(default="A2"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    if level not in LEVELS:
        raise HTTPException(status_code=400, detail=f"Nivel desconocido: {level}")
    return _sample_block(db, level)


@router.post("/grade", response_model=PlacementGradeResult)
def grade(
    payload: PlacementGradeSubmission,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlacementGradeResult:
    per_level, _, correct, total = _grade(db, payload.answers)
    results = per_level.get(payload.level, [])
    return PlacementGradeResult(
        level=payload.level,
        correct=correct,
        total=total,
        passed=_passed(results, PASS_RATIO),
    )


def _random_lesson_for_level(db: Session, level: str) -> Lesson | None:
    """Choose a random published lesson at the level, falling back downward."""
    order = ["A1", "A2", "B1", "B2", "C1", "C2"]
    target_index = order.index(level) if level in order else 0
    for candidate_level in reversed(order[: target_index + 1]):
        lessons = db.scalars(
            select(Lesson).where(
                Lesson.cefr_level == candidate_level, Lesson.status == "published"
            )
        ).all()
        if lessons:
            return random.choice(lessons)
    return None


def _finish(db: Session, user: User, overall: str, levels: dict[str, str], scores: dict[str, float]) -> None:
    rows = db.scalars(select(SkillProgress).where(SkillProgress.user_id == user.id)).all()
    for row in rows:
        row.level = levels.get(row.skill, levels.get("grammar", "A1"))
        row.score = scores.get(row.skill, scores.get("grammar", 50.0))
    user.placement_completed = True
    state = db.get(UserState, user.id)
    lesson = _random_lesson_for_level(db, overall) or adaptive.choose_next_lesson(db, user)
    if state is None:
        state = UserState(user_id=user.id)
        db.add(state)
    state.current_lesson_id = lesson.id if lesson else None
    state.current_step = "mira"
    state.current_clip_index = 0
    db.commit()


@router.post("", response_model=PlacementResult)
def submit(payload: PlacementSubmission, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PlacementResult:
    per_level, per_skill, correct, total = _grade(db, payload.answers)
    passed_levels = [level for level in LEVELS if _passed(per_level.get(level, []), PASS_RATIO)]
    overall = passed_levels[-1] if passed_levels else "A1"
    levels: dict[str, str] = {}
    scores: dict[str, float] = {}
    for skill in ("vocabulary", "grammar", "listening", "reading"):
        by_level = per_skill.get(skill, {})
        skill_levels = [level for level in LEVELS if _passed(by_level.get(level, []), SKILL_PASS_RATIO)]
        level = skill_levels[-1] if skill_levels else overall
        levels[skill] = level
        scores[skill] = LEVEL_SCORES[level]
    for skill in ("pronunciation", "fluency", "writing"):
        levels[skill] = overall
        scores[skill] = LEVEL_SCORES[overall]
    _finish(db, user, overall, levels, scores)
    return PlacementResult(overall_level=overall, skill_levels=levels, correct=correct, total=total)


SKILLS = ("vocabulary", "grammar", "listening", "reading", "pronunciation", "fluency", "writing")


@router.post("/skip", response_model=PlacementResult)
def skip(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PlacementResult:
    levels = {skill: "A1" for skill in SKILLS}
    scores = {skill: 35.0 for skill in levels}
    _finish(db, user, "A1", levels, scores)
    return PlacementResult(overall_level="A1", skill_levels=levels, correct=0, total=0)


@router.post("/manual", response_model=PlacementResult)
def manual(payload: LevelSelection, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PlacementResult:
    """Pick a level directly, without taking the test."""
    if payload.level not in LEVELS:
        raise HTTPException(status_code=400, detail=f"Nivel desconocido: {payload.level}")
    levels = {skill: payload.level for skill in SKILLS}
    scores = {skill: LEVEL_SCORES[payload.level] for skill in SKILLS}
    _finish(db, user, payload.level, levels, scores)
    return PlacementResult(overall_level=payload.level, skill_levels=levels, correct=0, total=0)
