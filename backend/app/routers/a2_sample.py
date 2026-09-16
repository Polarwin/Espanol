"""Authenticated textbook pilot: no changes to existing lesson completion."""
from typing import Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import A2SampleProgress, Lesson, User
from ..seed.a2_sample import WORDS, GRAMMAR, TITLE
from ..services.ai import providers, vocabulary
from ..services.security import get_current_user
from ..services.ratelimit import rate_limit

router = APIRouter(prefix='/api/sample/a2-unit-1', tags=['A2 sample'])


class StudyState(BaseModel):
    language: Literal['es', 'en'] = 'es'
    reviewed: list[str] = Field(default_factory=list, max_length=200)
    draft: str = Field(default='', max_length=2000)
    original: str = Field(default='', max_length=2000)


class Writing(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


@router.get('')
def sample(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lesson = db.scalar(select(Lesson).where(Lesson.title == TITLE, Lesson.status == 'published'))
    state = db.get(A2SampleProgress, user.id)
    return {'words': WORDS, 'grammar': GRAMMAR, 'lesson_id': lesson.id if lesson else None,
            'state': state.data if state else StudyState().model_dump()}


@router.put('/state')
def save_state(body: StudyState, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    valid = {word['id'] for word in WORDS}
    if any(word not in valid for word in body.reviewed):
        raise HTTPException(422, 'Unknown vocabulary item')
    state = db.get(A2SampleProgress, user.id)
    if state is None:
        state = A2SampleProgress(user_id=user.id)
        db.add(state)
    state.data = body.model_dump()
    db.commit()
    return {'saved': True}


@router.post('/words/{word_id}', dependencies=[Depends(rate_limit(20, 60))])
def explanation(word_id: str, user: User = Depends(get_current_user)):
    word = next((word for word in WORDS if word['id'] == word_id), None)
    if word is None:
        raise HTTPException(404, 'Unknown vocabulary item')
    try:
        return vocabulary.explain(word['text'], word['translation'])
    except (ValueError, httpx.HTTPError, KeyError, IndexError, TypeError):
        raise HTTPException(503, 'La explicación no está disponible. Inténtalo de nuevo.')


@router.post('/writing', dependencies=[Depends(rate_limit(10, 60))])
def writing(body: Writing, user: User = Depends(get_current_user)):
    if not body.text.strip():
        raise HTTPException(422, 'Escribe una frase primero.')
    # This pilot explicitly uses the existing local BARTO worker.
    if not settings.ai_correction_local or settings.ai_correction_adapter != 'barto':
        raise HTTPException(503, 'La revisión local no está disponible.')
    return providers.correct(body.text)


@router.get('/audio/{track}')
def audio(track: int, user: User = Depends(get_current_user)):
    if track not in {1, 2}:
        raise HTTPException(404, 'Unknown track')
    path = settings.vitamina_dir / 'Vitamina A2' / 'Vitamina A2. Libro del alumno. Audio' / f'PISTA {track:02d}.mp3'
    if not path.is_file():
        raise HTTPException(404, 'Audio unavailable')
    return FileResponse(path, media_type='audio/mpeg')
