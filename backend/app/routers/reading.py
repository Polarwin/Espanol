from typing import Literal
from uuid import uuid4
from hashlib import sha256
import json
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ReadingPractice, User
from ..services.security import get_current_user
from ..services.ratelimit import rate_limit
from ..services import reading
from ..config import settings
from tools.reading_audio import ensure_audio

router = APIRouter(prefix='/api/reading', tags=['reading'])


class GenerateRequest(BaseModel):
    source: Literal['auto', 'library', 'news'] = 'auto'
    level: Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] = 'A2'


class AnswersRequest(BaseModel):
    answers: dict[str, str] = Field(max_length=12)


def owned(db, user, job_id):
    job = db.get(ReadingPractice, job_id)
    if not job or job.user_id != user.id:
        raise HTTPException(404, 'Lectura no encontrada')
    return job


def data(job, full=True):
    result = {key: getattr(job, key) for key in
              ('id', 'status', 'stage', 'level', 'source', 'source_title', 'error', 'created_at')}
    if full:
        result.update(pack=job.pack, answers=job.answers)
    return result


@router.get('')
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    with reading.lock:
        jobs = db.scalars(select(ReadingPractice).where(ReadingPractice.user_id == user.id)
                          .order_by(ReadingPractice.created_at.desc()).limit(30)).all()
        reading.recover(db, jobs)
        return [data(j, False) for j in jobs]


@router.post('', dependencies=[Depends(rate_limit(10, 60))])
def create(body: GenerateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    with reading.lock:
        jobs = db.scalars(select(ReadingPractice).where(ReadingPractice.user_id == user.id)
                          .order_by(ReadingPractice.created_at.desc()).limit(30)).all()
        reading.recover(db, jobs)
        for job in jobs:
            if job.id in reading.active:
                return data(job)
        if reading.active:
            raise HTTPException(409, 'El generador está ocupado. Inténtalo en unos minutos.')
        try:
            source, text, excerpt = reading.select_source(db, body.source, body.level,
                                                          {j.source_key for j in jobs[:10]})
        except ValueError:
            raise HTTPException(422, 'No hay textos o subtítulos disponibles en esa fuente.')
        job = ReadingPractice(id=uuid4().hex, user_id=user.id, level=body.level, **source)
        db.add(job)
        db.commit()
        reading.active.add(job.id)
        try:
            reading.executor.submit(reading.generate, job.id, text, excerpt)
        except RuntimeError:
            reading.active.discard(job.id)
            job.status, job.error = 'failed', 'Servicio reiniciándose. Inténtalo de nuevo.'
            db.commit()
        return data(job)


@router.get('/{job_id}')
def get(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    with reading.lock:
        job = owned(db, user, job_id)
        reading.recover(db, [job])
        return data(job)


@router.put('/{job_id}/answers')
def save(job_id: str, body: AnswersRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = owned(db, user, job_id)
    if job.status != 'ready':
        raise HTTPException(409, 'La lectura todavía no está lista')
    valid = {str(i) for i in range(len(job.pack['questions']))}
    if any(key not in valid or len(value) > 4000 for key, value in body.answers.items()):
        raise HTTPException(422, 'Respuestas no válidas')
    job.answers = body.answers
    db.commit()
    return data(job)


@router.post('/{job_id}/audio', dependencies=[Depends(rate_limit(30, 60))])
def audio(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = owned(db, user, job_id)
    if job.status != 'ready' or not job.pack:
        raise HTTPException(409, 'La lectura todavía no está lista')
    root = settings.reading_static_dir.resolve()
    key = job.pack.get('video_key')
    if key:
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}|[a-f0-9]{24}', str(key)):
            raise HTTPException(404, 'Audio no disponible')
        if job.level not in {'A1', 'A2', 'B1', 'B2', 'C1', 'C2'}:
            raise HTTPException(404, 'Audio no disponible')
        directory = root / f'news-{key}-{job.level.lower()}'
    else:
        # Export only generated text, never learner answers or identity.
        key = sha256(job.pack['reading'].encode()).hexdigest()
        directory = root / f'app-audio-{key}'
    path = directory / 'lectura.mp3'
    if not path.resolve().is_relative_to(root):
        raise HTTPException(404, 'Audio no disponible')
    if not path.is_file():
        if job.pack.get('video_key'):
            raise HTTPException(404, 'El audio se ha eliminado o todavía no está disponible')
        try:
            with reading.generation_slot():
                directory.mkdir(parents=True, exist_ok=True)
                if not path.is_file():
                    cache = directory / 'ejercicio.json'
                    if cache.is_symlink():
                        raise ValueError('Invalid audio cache')
                    cache.write_text(json.dumps({'reading': job.pack['reading']}, ensure_ascii=False), encoding='utf-8')
                    ensure_audio(directory)
        except BlockingIOError:
            raise HTTPException(409, 'El generador está ocupado. Inténtalo en unos minutos.')
        except Exception:
            raise HTTPException(503, 'No se pudo preparar el audio local. Inténtalo de nuevo.')
    return FileResponse(path, media_type='audio/mpeg', filename='lectura.mp3',
                        headers={'Cache-Control': 'private, no-store'})
