"""Status endpoints for external content and speech-analysis integration."""

from pathlib import Path
import re
import tempfile
import unicodedata

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..config import settings
from ..db import get_db
from ..models import Lesson, User, UserState
from ..seed.conversation_content import CONVERSATION_SCENARIOS
from ..seed.vocabulary_content import VOCABULARY_BANKS
from ..services.goals import increment_goal
from ..services.progress import apply_skill_deltas
from ..services.pronunciation import score_pronunciation, transcribe_spanish
from ..services.security import get_current_user
from ..services.speech import spanish_example_audio
from ..services.streak import record_activity

router = APIRouter(tags=["capabilities"])


class SpeechExampleRequest(BaseModel):
    phrase: str = Field(min_length=1, max_length=300)


def _conversation_lesson(db: Session, user: User, lesson_id: int | None) -> Lesson:
    lesson = db.get(Lesson, lesson_id) if lesson_id else None
    if lesson is None:
        state = db.scalar(select(UserState).where(UserState.user_id == user.id))
        lesson = db.get(Lesson, state.current_lesson_id) if state and state.current_lesson_id else None
    if lesson is None or lesson.status != "published":
        lesson = db.scalar(select(Lesson).where(Lesson.status == "published").order_by(Lesson.id))
    if lesson is None:
        raise HTTPException(status_code=404, detail="No lesson available")
    return lesson


def _conversation_profile(lesson: Lesson, name: str) -> dict:
    vocabulary = [text for text, _ in VOCABULARY_BANKS.get(lesson.title, [])]
    topics = [topic for topic in lesson.topics if "vitamina" not in topic.lower()]
    topic = topics[0] if topics else lesson.title.lower()
    scenario = CONVERSATION_SCENARIOS.get(lesson.title) or {
        "role": "compañera",
        "scene": f"Hablar de {topic}",
        "opening": f"¿Qué experiencia tienes con {topic}?",
        "prompts": [f"Cuéntame un ejemplo sobre {topic}.", "¿Por qué es importante para ti?", "¿Qué recomendarías?"],
        "closing": "Gracias por compartir tus ideas.",
    }
    return {
        "lesson_id": lesson.id,
        "title": lesson.title,
        "cefr_level": lesson.cefr_level,
        "topic": topic,
        "scene": scenario["scene"],
        "goal": f"Representa la situación «{scenario['scene']}» durante cuatro turnos.",
        "greeting": f"¡Hola, {name}! Soy Ana, tu {scenario['role']}. {scenario['opening']}",
        "vocabulary": vocabulary[:4],
        "prompts": scenario["prompts"],
        "closing": scenario["closing"],
    }


def _plain(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(char) != "Mn")


def _conversation_correction(transcript: str, lesson: Lesson) -> dict:
    """Return one clear, level-appropriate correction without interrupting the role-play."""
    original = transcript.strip()
    grammar = lesson.grammar_tip or {}
    wrong, right = grammar.get("wrong", ""), grammar.get("right", "")
    if wrong and right:
        heard, target = set(_plain(original).split()), set(_plain(wrong).split())
        if target and len(heard & target) / len(target) >= 0.7:
            return {"has_error": True, "original": original, "corrected": right, "explanation": grammar.get("explanation", "Esta forma es más natural en español.")}

    patterns = [
        (r"\bsoy (\d{1,3}) a(?:n|ñ)os\b", r"tengo \1 años", "Para decir la edad usamos tener, no ser."),
        (r"\bme gusta (los|las)\b", r"me gustan \1", "Gustar concuerda con la cosa que gusta: en plural, gustan."),
        (r"\b(yo|t[uú]|[eé]l|ella) gusto\b", r"me gusta", "Con gustar decimos me gusta, te gusta o le gusta."),
        (r"\b(yo )?soy de acuerdo\b", r"estoy de acuerdo", "La expresión fija es estar de acuerdo."),
        (r"\bdepende de que\b", r"depende de", "Después de depende de añadimos directamente el nombre o la situación."),
        (r"\bvamos (?!a\b)([a-záéíóúñ]+(?:ar|er|ir))\b", r"vamos a \1", "Para hablar de un plan usamos ir a + infinitivo."),
        (r"\btengo (hambre|sed|fr[ií]o|calor)\b", lambda m: f"tengo {m.group(1).replace('frio', 'frío')}", "Estas expresiones usan tener; recuerda la tilde de frío."),
    ]
    normalized = _plain(original)
    for pattern, replacement, explanation in patterns:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            corrected = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
            corrected = corrected[:1].upper() + corrected[1:]
            return {"has_error": True, "original": original, "corrected": corrected, "explanation": explanation}
    return {"has_error": False, "original": original, "corrected": "", "explanation": "Tu frase se entiende bien. Sigue ampliando la respuesta."}


def _conversation_reply(transcript: str, turn: int, name: str, profile: dict, correction: dict) -> tuple[str, str, list[str]]:
    address = f", {name}" if name else ""
    words = profile["vocabulary"] or [profile["topic"]]
    if turn == 0:
        feedback = "Practica la versión corregida y continúa." if correction["has_error"] else "Tu respuesta se entiende. Intenta incorporar una palabra de la unidad."
        return profile["prompts"][0], feedback, [f"Para mí, {words[0]}...", f"Un ejemplo de {words[0]} es..."]
    if turn == 1:
        word = words[min(1, len(words) - 1)]
        return profile["prompts"][1], "Bien: has ampliado tu respuesta. Intenta añadir dónde, cuándo o por qué.", [f"En mi caso, {word}...", "Esto es importante porque..."]
    if turn == 2:
        return profile["prompts"][2], "Muy bien: ya mantienes la conversación y justificas tus ideas.", ["Lo recomiendo porque...", "En esta situación, yo..."]
    return f"{profile['closing']} ¡Muy bien{address}!", "Conversación completada. Has representado una situación real de la unidad.", ["Quiero practicar otra vez.", "Voy a usar estas palabras esta semana."]


def _source(name: str, path: Path) -> dict:
    # Do not walk network-mounted libraries during a web request. A background
    # ingestion worker will own availability checks and file inventory.
    return {"name": name, "path": str(path), "status": "configured"}


@router.get("/api/content/sources")
def content_sources(_: User = Depends(get_current_user)) -> list[dict]:
    return [_source("Español", settings.watch_dir), _source("Vitamina", settings.vitamina_dir)]


@router.post("/api/pronunciation/evaluate")
async def pronunciation_evaluate(
    audio: UploadFile = File(...),
    phrase: str = Form(..., min_length=1, max_length=300),
    phrase_id: str = Form(""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    data = await audio.read(10 * 1024 * 1024 + 1)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio is empty")
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Audio is too large")

    suffix = Path(audio.filename or "recording.webm").suffix or ".webm"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(data)
            temp_path = Path(temp.name)
        transcription = await run_in_threadpool(transcribe_spanish, temp_path, phrase)
        result = score_pronunciation(phrase, transcription)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech analysis is temporarily unavailable",
        ) from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    normalized_score = result["score"] / 100
    apply_skill_deltas(
        db,
        user,
        {
            "pronunciation": 2.0 * normalized_score if normalized_score >= 0.6 else -1.0,
            "fluency": normalized_score,
        },
    )
    increment_goal(db, user, "sentences_spoken")
    record_activity(db, user)
    db.commit()
    return result


@router.post("/api/speech/example", response_class=FileResponse)
async def speech_example(
    payload: SpeechExampleRequest,
    _: User = Depends(get_current_user),
) -> FileResponse:
    try:
        audio_path = await run_in_threadpool(spanish_example_audio, payload.phrase)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Example audio is temporarily unavailable",
        ) from exc
    return FileResponse(audio_path, media_type="audio/mpeg", filename="ejemplo-espanol.mp3")


@router.get("/api/conversation/setup")
def conversation_setup(
    lesson_id: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    lesson = _conversation_lesson(db, user, lesson_id)
    return _conversation_profile(lesson, (user.nickname or user.display_name).strip())


@router.post("/api/conversation/respond")
async def conversation_respond(
    audio: UploadFile = File(...),
    turn: int = Form(0),
    lesson_id: int | None = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    data = await audio.read(10 * 1024 * 1024 + 1)
    if not data or len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Invalid audio")
    lesson = _conversation_lesson(db, user, lesson_id)
    profile = _conversation_profile(lesson, (user.nickname or user.display_name).strip())
    suffix = Path(audio.filename or "recording.webm").suffix or ".webm"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(data)
            temp_path = Path(temp.name)
        transcript = await run_in_threadpool(
            transcribe_spanish, temp_path,
            f"Una conversación en español sobre {profile['topic']}: {', '.join(profile['vocabulary'])}",
        )
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    correction = _conversation_correction(transcript, lesson)
    reply, feedback, suggestions = _conversation_reply(
        transcript, turn, (user.nickname or user.display_name).strip(), profile, correction
    )
    apply_skill_deltas(db, user, {"fluency": 1.5, "listening": 0.5, "pronunciation": 0.5})
    increment_goal(db, user, "sentences_spoken")
    record_activity(db, user)
    db.commit()
    return {"transcript": transcript, "reply": reply, "feedback": feedback, "correction": correction, "suggestions": suggestions, "turn": turn + 1, "complete": turn >= 3}
