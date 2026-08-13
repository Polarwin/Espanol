"""Status endpoints for external content and speech-analysis integration."""

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from ..config import settings
from ..models import User
from ..services.security import get_current_user

router = APIRouter(tags=["capabilities"])


def _source(name: str, path: Path) -> dict:
    # Do not walk network-mounted libraries during a web request. A background
    # ingestion worker will own availability checks and file inventory.
    return {"name": name, "path": str(path), "status": "configured"}


@router.get("/api/content/sources")
def content_sources(_: User = Depends(get_current_user)) -> list[dict]:
    return [_source("Español", settings.watch_dir), _source("Vitamina", settings.vitamina_dir)]


@router.post("/api/pronunciation/evaluate")
def pronunciation_evaluate(audio: UploadFile = File(...), _: User = Depends(get_current_user)) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pronunciation analysis worker is not configured yet")
