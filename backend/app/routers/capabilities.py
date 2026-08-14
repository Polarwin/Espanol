"""Status endpoints for external content and speech-analysis integration."""

from pathlib import Path
import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..config import settings
from ..db import get_db
from ..models import User
from ..services.goals import increment_goal
from ..services.progress import apply_skill_deltas
from ..services.pronunciation import score_pronunciation, transcribe_spanish
from ..services.security import get_current_user
from ..services.streak import record_activity

router = APIRouter(tags=["capabilities"])


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
