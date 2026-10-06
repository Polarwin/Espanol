#!/usr/bin/env python3
"""Generate one daily A2 news pack and deliver private copies to existing users.

Run from project root: ./bin/python tools/daily_reading.py
The private date cache makes reruns resumable and delivery idempotent. The host
cron uses Europe/Madrid; this date calculation follows that timezone explicitly.
"""
import json
import logging
import sys
import time
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import select
from backend.app.config import settings
from backend.app.db import SessionLocal
from backend.app.models import ReadingPractice, User
from backend.app.services import reading

logger = logging.getLogger('daily-reading')


def deliver(db, day, source, pack):
    delivered = 0
    for user_id in db.scalars(select(User.id)).all():
        job_id = sha256(f'daily-reading:{day}:A2:{user_id}'.encode()).hexdigest()[:32]
        if db.get(ReadingPractice, job_id):
            continue
        job = ReadingPractice(id=job_id, user_id=user_id, level='A2', status='ready', stage='Lista',
                              source=source['source'], source_key=source['source_key'],
                              source_title=f'Lectura del día · {day} · {source["source_title"]}',
                              pack=pack, answers={})
        db.add(job)
        delivered += 1
    db.commit()
    return delivered


def run(day=None):
    day = day or datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat()
    with reading.generation_slot():
        directory = settings.backup_dir / 'daily-readings'
        directory.mkdir(parents=True, exist_ok=True)
        cache = directory / f'{day}-A2.json'
        if cache.exists():
            result = json.loads(cache.read_text(encoding='utf-8'))
        else:
            with SessionLocal() as db:
                if not db.scalar(select(User.id).limit(1)):
                    logger.info('No learners yet; skipping generation')
                    return 0
                recent = db.scalars(select(ReadingPractice.source_key)
                                    .where(ReadingPractice.source == 'news')
                                    .order_by(ReadingPractice.created_at.desc()).limit(100)).all()
                source, text, excerpt = reading.select_source(db, 'news', 'A2', set(recent))
            pack, _ = reading.generate_pack(text, reading.model_args('A2'),
                                             lambda stage: logger.info('%s', stage))
            pack.update(source=source['source_title'], **excerpt)
            result = {'source': source, 'pack': pack}
            temporary = cache.with_suffix('.tmp')
            temporary.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
            temporary.replace(cache)
        with SessionLocal() as db:
            count = deliver(db, day, result['source'], result['pack'])
        logger.info('%s: delivered daily A2 reading to %s learners', day, count)
        return count


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    day = datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat()
    # Wait up to an hour for an interactive reading. Failed generations get
    # three attempts, while a successful date cache is never regenerated.
    failures = 0
    deadline = time.monotonic() + 3600
    while True:
        try:
            run(day)
            return
        except BlockingIOError:
            if time.monotonic() >= deadline:
                raise SystemExit('Reading generator remained busy for an hour')
            logger.info('Reading generator busy; retrying in 60 seconds')
        except Exception as error:
            failures += 1
            logger.error('Daily generation attempt %s failed (%s)', failures, type(error).__name__)
            if failures >= 3:
                raise SystemExit('Daily reading failed after three attempts; see daily-reading.log')
        time.sleep(60)


if __name__ == '__main__':
    main()
