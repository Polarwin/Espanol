"""Short A1-B1 placement test used before the adaptive path begins."""

import random

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Lesson, SkillProgress, User, UserState
from ..schemas.placement import PlacementQuestion, PlacementResult, PlacementSubmission
from ..services import adaptive
from ..services.security import get_current_user

router = APIRouter(prefix="/api/placement", tags=["placement"])

QUESTIONS = [
    {"id": "v1", "skill": "vocabulary", "prompt": "¿Qué significa «la mañana»?", "options": ["morning", "afternoon", "night"], "answer": "morning", "level": "A1"},
    {"id": "g1", "skill": "grammar", "prompt": "Yo ___ de Valencia.", "options": ["soy", "eres", "es"], "answer": "soy", "level": "A1"},
    {"id": "l1", "skill": "listening", "prompt": "Lee como si lo escucharas: «Son las ocho y media». ¿Qué hora es?", "options": ["8:30", "8:15", "9:30"], "answer": "8:30", "level": "A1"},
    {"id": "r1", "skill": "reading", "prompt": "Lee: «María vive en Sevilla con su gato». ¿Quién vive con María?", "options": ["Su gato", "Su hermana", "Su madre"], "answer": "Su gato", "level": "A1"},
    {"id": "v2", "skill": "vocabulary", "prompt": "«Quedar con amigos» significa…", "options": ["meet friends", "call friends", "help friends"], "answer": "meet friends", "level": "A2"},
    {"id": "g2", "skill": "grammar", "prompt": "Mañana nosotros ___ a visitar el museo.", "options": ["vamos", "hemos", "somos"], "answer": "vamos", "level": "A2"},
    {"id": "l2", "skill": "listening", "prompt": "«Aunque llueva, iremos al mercado». ¿Qué harán?", "options": ["Irán al mercado", "Se quedarán en casa", "No lo saben"], "answer": "Irán al mercado", "level": "A2"},
    {"id": "r2", "skill": "reading", "prompt": "Lee: «Ayer compré entradas para el concierto del sábado». ¿Cuándo es el concierto?", "options": ["El sábado", "Ayer", "El domingo"], "answer": "El sábado", "level": "A2"},
    {"id": "v3", "skill": "vocabulary", "prompt": "¿Qué palabra se parece más a «sin embargo»?", "options": ["no obstante", "además", "por eso"], "answer": "no obstante", "level": "B1"},
    {"id": "g3", "skill": "grammar", "prompt": "Si tuviera tiempo, ___ más español.", "options": ["estudiaría", "estudiaré", "estudio"], "answer": "estudiaría", "level": "B1"},
    {"id": "r3", "skill": "reading", "prompt": "Lee: «Aunque el tren salió con retraso, llegamos a tiempo a la entrevista». ¿Cómo llegaron a la entrevista?", "options": ["A tiempo", "Tarde", "No llegaron"], "answer": "A tiempo", "level": "B1"},
]


@router.get("", response_model=list[PlacementQuestion])
def questions(_: User = Depends(get_current_user)) -> list[dict]:
    shuffled = random.sample(QUESTIONS, k=len(QUESTIONS))
    return [{key: value for key, value in question.items() if key not in {"answer", "level"}} for question in shuffled]


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
    by_skill: dict[str, list[bool]] = {}
    correct = 0
    for question in QUESTIONS:
        passed = payload.answers.get(question["id"]) == question["answer"]
        correct += int(passed)
        by_skill.setdefault(question["skill"], []).append(passed)
    levels: dict[str, str] = {}
    scores: dict[str, float] = {}
    for skill, results in by_skill.items():
        count = sum(results)
        levels[skill] = "B1" if count == len(results) else "A2" if count >= 2 else "A1"
        scores[skill] = round(35 + 20 * count, 1)
    overall = "B1" if correct >= 7 else "A2" if correct >= 4 else "A1"
    for skill in ("pronunciation", "fluency", "writing"):
        levels[skill] = overall
        scores[skill] = 70.0 if overall == "B1" else 55.0 if overall == "A2" else 40.0
    _finish(db, user, overall, levels, scores)
    return PlacementResult(overall_level=overall, skill_levels=levels, correct=correct, total=len(QUESTIONS))


@router.post("/skip", response_model=PlacementResult)
def skip(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PlacementResult:
    levels = {skill: "A1" for skill in ("vocabulary", "grammar", "listening", "reading", "pronunciation", "fluency", "writing")}
    scores = {skill: 35.0 for skill in levels}
    _finish(db, user, "A1", levels, scores)
    return PlacementResult(overall_level="A1", skill_levels=levels, correct=0, total=len(QUESTIONS))
