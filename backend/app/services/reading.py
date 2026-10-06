"""Single-process, bounded local generation; source paths never come from clients."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import fcntl
from hashlib import sha256
import logging
from pathlib import Path
import random
import re
import sqlite3
from threading import RLock
from types import SimpleNamespace

from sqlalchemy import select

from tools.subtitle_reading import clean_subtitles, generate_pack, TIMING, seconds
from ..config import settings
from ..db import SessionLocal
from ..models import Exercise, Lesson, ReadingPractice
from . import textbook

lock = RLock()
active: set[str] = set()
executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='reading')
logger = logging.getLogger(__name__)


@contextmanager
def generation_slot():
    """Coordinate the API worker and scheduled generator on this host."""
    settings.backup_dir.mkdir(parents=True, exist_ok=True)
    with (settings.backup_dir / 'reading-generation.lock').open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def model_args(level):
    return SimpleNamespace(level=level, questions=5, vocabulary=8, context_size=settings.reading_context_size,
                           max_output_tokens=2000, context_margin=512, max_source_chars=11000,
                           api='http://127.0.0.1:8349/v1', model=settings.reading_model,
                           timeout=240, debug_dir=None)


def subtitle_candidates(root):
    root = Path(root).resolve()
    found = {}
    if not root.is_dir():
        return []
    for path in root.rglob('*'):
        if path.suffix.lower() not in {'.vtt', '.srt'} or not path.resolve().is_relative_to(root):
            continue
        # Prefer the original Spanish captions, and do not sample English sidecars.
        if re.search(r'\.(?:en|fr|de)(?:-orig)?\.', path.name):
            continue
        stem = re.sub(r'(?:\.es(?:-orig)?)?\.(?:vtt|srt)$', '', str(path))
        priority = 0 if path.name.endswith('.es-orig.vtt') else 1 if path.name.endswith('.es.vtt') else 2
        if stem not in found or priority < found[stem][0]:
            found[stem] = (priority, path)
    return [item[1] for item in found.values()]


def select_source(db, kind, level, recent):
    pools = {}
    if kind in {'auto', 'library'}:
        rows = db.execute(select(Exercise.id, Exercise.passage, Lesson.title).join(Lesson)
                          .where(Lesson.status == 'published', Lesson.cefr_level == level,
                                 Exercise.passage.is_not(None))).all()
        items, seen_passages = [], set()
        for row in rows:
            passage = row.passage or ''
            key = sha256(' '.join(passage.split()).encode()).hexdigest()
            if len(passage.split()) >= 30 and key not in seen_passages:
                items.append(('text', f'passage:{key}', row.title, passage))
                seen_passages.add(key)
        items += [('subtitle', str(p), p.stem, p) for p in subtitle_candidates(settings.watch_dir)]
        # Indexed Ke/Vitamina pages are already extracted locally. Select real
        # prose, avoiding tiny OCR fragments; level is adapted by the generator.
        if textbook.available():
            try:
                with sqlite3.connect(f'file:{textbook.INDEX_PATH}?mode=ro', uri=True) as connection:
                    for source, page, text in connection.execute('SELECT source, page, text FROM chunks'):
                        if len(text.split()) >= 80:
                            items.append(('text', f'book:{source}:{page}', f'{Path(source).name} · p. {page}', text))
            except sqlite3.Error:
                logger.warning('Reading textbook index unavailable')
        pools['library'] = items
    if kind in {'auto', 'news'}:
        pools['news'] = [('subtitle', str(p), p.stem, p) for p in subtitle_candidates(settings.reading_news_dir)]
    pools = {k: v for k, v in pools.items() if v}
    while pools:
        selected_kind = random.choice(list(pools))
        items = pools[selected_kind]
        unseen = [x for x in items if sha256(x[1].encode()).hexdigest() not in recent]
        item = random.choice(unseen or items)
        items.remove(item)
        if not items:
            del pools[selected_kind]
        typ, key, title, value = item
        start, duration = 0, 180
        try:
            if typ == 'subtitle':
                if value.stat().st_size > 8_000_000:
                    continue
                raw = value.read_text(encoding='utf-8-sig')
                timings = list(TIMING.finditer(raw))
                if not timings:
                    continue
                end = max(seconds(t['end']) for t in timings)
                start = random.uniform(0, max(0, end - duration))
                value = clean_subtitles(raw, start, duration)
            if len(value.encode('utf-8')) > 60_000:
                continue
            return dict(source=selected_kind, source_key=sha256(key.encode()).hexdigest(),
                        source_title=re.sub(r'\.es(?:-orig)?$', '', title)), value, {
                            'start': round(start), 'duration': duration if typ == 'subtitle' else 0}
        except (OSError, UnicodeError, ValueError):
            continue
    raise ValueError('No usable sources')


def generate(job_id, text, excerpt):
    def progress(stage):
        with SessionLocal() as db:
            job = db.get(ReadingPractice, job_id)
            job.status, job.stage = 'running', stage
            db.commit()
    try:
        with SessionLocal() as db:
            job = db.get(ReadingPractice, job_id)
            args = model_args(job.level)
            title = job.source_title
        with generation_slot():
            pack, _ = generate_pack(text, args, progress)
        pack.update(source=title, **excerpt)
        with SessionLocal() as db:
            job = db.get(ReadingPractice, job_id)
            job.pack, job.status, job.stage = pack, 'ready', 'Lista'
            db.commit()
    except Exception as error:
        # Do not log subtitle text, learner answers, or model response bodies.
        logger.warning('Local reading generation failed for job %s (%s)', job_id, type(error).__name__)
        with SessionLocal() as db:
            job = db.get(ReadingPractice, job_id)
            job.status = 'failed'
            job.error = 'El modelo local no pudo completar una lectura válida. Puede estar ocupado. Inténtalo de nuevo.'
            db.commit()
    finally:
        with lock:
            active.discard(job_id)


def recover(db, jobs):
    """Single API worker: jobs without a live future were interrupted by restart."""
    for job in jobs:
        if job.status in {'queued', 'running'} and job.id not in active:
            job.status = 'failed'
            job.error = 'La generación se interrumpió al reiniciar el servicio. Puedes crear otra lectura.'
    db.commit()
