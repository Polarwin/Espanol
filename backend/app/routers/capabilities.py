"""Status endpoints for external content and speech-analysis integration."""

from pathlib import Path
import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..config import settings
from ..db import get_db
from ..models import User
from ..services.goals import increment_goal
from ..services.progress import apply_skill_deltas
from ..services.pronunciation import score_pronunciation, transcribe_spanish
from ..services.security import get_current_user
from ..services.speech import spanish_example_audio
from ..services.streak import record_activity

router = APIRouter(tags=["capabilities"])


class SpeechExampleRequest(BaseModel):
    phrase: str = Field(min_length=1, max_length=300)


def _conversation_reply(transcript: str, turn: int, name: str = "") -> tuple[str, str, list[str]]:
    text = transcript.lower()
    address = f", {name}" if name else ""
    if turn == 0:
        if any(word in text for word in ("bien", "genial", "fenomenal")):
            return f"¡Me alegro{address}! Yo también estoy muy bien. ¿Qué planes tienes para este fin de semana?", "Muy natural. También puedes decir «Estoy bastante bien». ", ["Voy a descansar.", "Voy a salir con amigos."]
        return f"Espero que estés bien{address}. ¿Qué planes tienes para este fin de semana?", "Para responder al saludo: «Estoy bien, gracias». ", ["Estoy bien, gracias.", "Muy bien, ¿y tú?"]
    if turn == 1:
        if any(word in text for word in ("amigo", "vecino", "familia", "quedar")):
            return "¡Qué buen plan! ¿Dónde vais a quedar?", "Bien dicho. Usa «voy a quedar con…» para hablar de personas.", ["Vamos a quedar en un café.", "Quedamos en el centro."]
        if any(word in text for word in ("casa", "descans", "leer", "película")):
            return "Suena tranquilo. ¿Prefieres descansar en casa o salir un poco?", "Tu idea se entiende bien. Intenta añadir «porque». ", ["Prefiero quedarme en casa.", "Quiero salir un poco."]
        return "Interesante. Cuéntame un poco más: ¿con quién vas a hacerlo?", "Prueba la estructura «Voy a + infinitivo». ", ["Voy a visitar Madrid.", "Voy a cocinar con mi familia."]
    if turn == 2:
        return "Perfecto. Si quieres, podemos tomar algo juntos el domingo. ¿Te apetece?", "Muy bien: has mantenido la conversación. ", ["Sí, me apetece mucho.", "Lo siento, el domingo no puedo."]
    return f"¡Estupendo{address}! Entonces hablamos luego. Que tengas un buen fin de semana.", "Conversación completada. Has saludado, explicado planes y respondido a una invitación.", ["¡Igualmente!", "Hasta luego."]


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


@router.post("/api/conversation/respond")
async def conversation_respond(
    audio: UploadFile = File(...),
    turn: int = Form(0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    data = await audio.read(10 * 1024 * 1024 + 1)
    if not data or len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Invalid audio")
    suffix = Path(audio.filename or "recording.webm").suffix or ".webm"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(data)
            temp_path = Path(temp.name)
        transcript = await run_in_threadpool(
            transcribe_spanish, temp_path, "Una conversación natural entre vecinos en español"
        )
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    reply, feedback, suggestions = _conversation_reply(
        transcript, turn, (user.nickname or user.display_name).strip()
    )
    apply_skill_deltas(db, user, {"fluency": 1.5, "listening": 0.5, "pronunciation": 0.5})
    increment_goal(db, user, "sentences_spoken")
    record_activity(db, user)
    db.commit()
    return {"transcript": transcript, "reply": reply, "feedback": feedback, "suggestions": suggestions, "turn": turn + 1, "complete": turn >= 3}
