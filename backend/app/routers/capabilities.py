"""Status endpoints for external content and speech-analysis integration."""

from pathlib import Path
import tempfile
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..config import settings
from ..db import get_db
from ..models import Lesson, User, UserState, ConversationSession
from ..services.ai.providers import respond as ai_respond, correct as ai_correct
from ..seed.conversation_content import CONVERSATION_SCENARIOS
from ..seed.vocabulary_content import VOCABULARY_BANKS
from ..services.goals import increment_goal
from ..services.progress import apply_skill_deltas
from ..services.pronunciation import score_pronunciation, transcribe_spanish
from ..services.ratelimit import rate_limit
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
    # Video lessons ("… · Vídeo") share their base unit's vocabulary bank.
    bank_title = lesson.title.removesuffix(" · Vídeo")
    vocabulary = [
        text
        for text, _ in VOCABULARY_BANKS.get(
            lesson.title, VOCABULARY_BANKS.get(bank_title, [])
        )
    ]
    topics = [topic for topic in lesson.topics if "vitamina" not in topic.lower()]
    topic = topics[0] if topics else lesson.title.lower()
    scenario = CONVERSATION_SCENARIOS.get(lesson.title)
    if scenario is None and lesson.title.endswith(" · Vídeo"):
        scenario = {
            "role": "compañera",
            "scene": f"Comentar el vídeo: {bank_title}",
            "opening": f"¿Qué te ha parecido el vídeo sobre {topic}?",
            "prompts": [
                "¿Qué idea del vídeo te ha llamado más la atención?",
                "¿Estás de acuerdo con lo que dice? ¿Por qué?",
                "¿Qué más te gustaría saber sobre el tema?",
            ],
            "closing": "Gracias por comentar el vídeo conmigo.",
        }
    if scenario is None:
        scenario = {
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


@router.post("/api/pronunciation/evaluate", dependencies=[Depends(rate_limit(max_calls=30, window_seconds=60))])
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


@router.post("/api/speech/example", response_class=FileResponse, dependencies=[Depends(rate_limit(max_calls=30, window_seconds=60))])
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
    profile = _conversation_profile(lesson, (user.nickname or user.display_name).strip())
    session = ConversationSession(id=uuid4().hex, user_id=user.id, lesson_id=lesson.id, turn=0,
        history=[{'role': 'assistant', 'content': profile['greeting']}])
    db.add(session)
    db.commit()
    return {**profile, 'session_id': session.id}


@router.post("/api/conversation/respond", dependencies=[Depends(rate_limit(max_calls=30, window_seconds=60))])
async def conversation_respond(
    audio: UploadFile | None = File(None),
    turn: int = Form(0, ge=0, le=3),
    session_id: str | None = Form(None, max_length=64),
    request_id: str | None = Form(None, max_length=64),
    text: str | None = Form(None, max_length=2000),
    lesson_id: int | None = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    session = db.get(ConversationSession, session_id) if session_id else None
    if session_id and (session is None or session.user_id != user.id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    if session:
        if lesson_id is not None and lesson_id != session.lesson_id:
            raise HTTPException(status_code=409, detail="Conversation lesson mismatch")
        if request_id and session.last_request == request_id:
            return session.last_result
        if session.turn != turn:
            raise HTTPException(status_code=409, detail="Conversation turn mismatch")
        lesson_id = session.lesson_id
    lesson = _conversation_lesson(db, user, lesson_id)
    profile = _conversation_profile(lesson, (user.nickname or user.display_name).strip())
    history = list(session.history) if session else [{'role': 'assistant', 'content': profile['greeting']}]
    # Release the read transaction while speech and model inference run.
    db.commit()
    transcript = (text or '').strip()
    if not transcript:
        if audio is None:
            raise HTTPException(status_code=400, detail="Send text or audio")
        data = await audio.read(10 * 1024 * 1024 + 1)
        if not data or len(data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Invalid audio")
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp:
                temp.write(data)
                temp_path = Path(temp.name)
            transcript = await run_in_threadpool(transcribe_spanish, temp_path,
                f"Una conversación en español sobre {profile['topic']}")
        finally:
            if temp_path:
                temp_path.unlink(missing_ok=True)
    transcript = transcript.strip()
    if not transcript or len(transcript) > 2000:
        raise HTTPException(status_code=422, detail="Send a shorter, nonempty response")
    # Speech transcripts can contain ASR errors: detailed correction belongs to
    # confirmed writing, not automatic accusations about spoken grammar.
    correction = {'has_error': False, 'original': transcript, 'corrected': '',
        'explanation': 'Puedes practicar esta respuesta también por escrito.', 'status': 'not_assessed'}
    reply, feedback, suggestions = _conversation_reply(
        transcript, turn, (user.nickname or user.display_name).strip(), profile, correction)
    writing_correction = await run_in_threadpool(ai_correct, transcript) if text else None
    fallback = False
    if turn < 3:
        reply, fallback = await run_in_threadpool(ai_respond, profile, history, transcript, reply)
    feedback = 'Sigue practicando con tus propias palabras.' if turn < 3 else 'Has completado la práctica.'
    result = {'transcript': transcript, 'reply': reply, 'feedback': feedback,
        'correction': correction, 'suggestions': suggestions, 'turn': turn + 1,
        'complete': turn >= 3, 'fallback': fallback, 'session_id': session_id,
        'writing_correction': writing_correction.model_dump() if writing_correction else None}
    if session:
        claimed = db.execute(update(ConversationSession).where(
            ConversationSession.id == session.id, ConversationSession.turn == turn
        ).values(turn=turn+1, history=[*history, {'role': 'user', 'content': transcript},
            {'role': 'assistant', 'content': reply}], last_request=request_id, last_result=result))
        if claimed.rowcount != 1:
            db.rollback()
            db.refresh(session)
            if request_id and session.last_request == request_id:
                return session.last_result
            raise HTTPException(status_code=409, detail="Conversation already advanced")
    apply_skill_deltas(db, user, {"fluency": 1.5, "writing": 0.5} if text else {"fluency": 1.5, "listening": 0.5, "pronunciation": 0.5})
    increment_goal(db, user, "writing_responses" if text else "sentences_spoken")
    record_activity(db, user)
    db.commit()
    return result
