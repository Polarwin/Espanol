#!/usr/bin/env python3
"""Watch finalized news videos; keep all generated files in the static folder.

Only identities, file signatures, retry times and delivery status live in the
private SQLite ledger. Removing static output never resets a completed video.
"""
import argparse
from contextlib import contextmanager
import fcntl
from hashlib import sha256
import json
import logging
from pathlib import Path
import re
import sqlite3
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import select
from backend.app.config import settings
from backend.app.db import SessionLocal
from backend.app.models import ReadingPractice, User
from backend.app.services import reading
from tools.subtitle_reading import clean_subtitles, render, make_pdf, TIMING, seconds
from tools.reading_audio import ensure_audio

log = logging.getLogger('news-reading-watcher')
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.webm', '.m4v', '.mov'}


def video_key(path, root):
    match = re.search(r'\[([A-Za-z0-9_-]{11})\]$', path.stem)
    return match[1] if match else sha256(str(path.relative_to(root).with_suffix('')).encode()).hexdigest()[:24]


def videos(root):
    root = root.resolve()
    result = {}
    for path in sorted(root.rglob('*')):
        if path.suffix.lower() not in VIDEO_EXTENSIONS or re.search(r'\.f\d+$', path.stem):
            continue
        if not path.is_file() or not path.resolve().is_relative_to(root):
            continue
        result.setdefault(video_key(path, root), path)
    return result


def sidecar(video, root):
    for extension in ('.es-orig.vtt', '.es.vtt', '.es-orig.srt', '.es.srt', '.vtt', '.srt'):
        path = video.with_suffix(extension)
        if path.is_file() and path.resolve().is_relative_to(root.resolve()):
            return path
    return None


def signature(video, subtitle):
    # yt-dlp writes subtitle sidecars before finishing/merging the video.
    if not subtitle:
        return None
    for path in video.parent.iterdir():
        if path.name.startswith(video.stem + '.') and path.suffix in {'.part', '.ytdl', '.tmp', '.temp'}:
            return None
    stats = [video.stat(), subtitle.stat()]
    if any(s.st_size == 0 for s in stats) or stats[1].st_size > 8_000_000:
        return None
    return json.dumps([subtitle.name, *[(s.st_size, s.st_mtime_ns) for s in stats]])


def connect(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
    db.execute('''CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY, path TEXT NOT NULL, status TEXT NOT NULL,
        signature TEXT, changed REAL NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
        retry_at REAL NOT NULL DEFAULT 0, error TEXT)''')
    db.commit()
    return db


@contextmanager
def watcher_slot(ledger):
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.with_suffix('.lock').open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def initialize(db, root, now):
    if db.execute("SELECT 1 FROM meta WHERE key='initialized'").fetchone():
        return
    if not root.is_dir():
        raise FileNotFoundError('News folder unavailable; refusing to baseline an empty mount')
    existing = videos(root)
    for key, path in existing.items():
        db.execute('INSERT OR IGNORE INTO videos(id,path,status,changed) VALUES (?,?,?,?)',
                   (key, str(path.relative_to(root)), 'baseline', now))
    db.execute("INSERT INTO meta VALUES ('initialized', ?)", (str(now),))
    db.commit()
    log.info('Initialized: %s existing videos excluded; watching new arrivals', len(existing))


def discover(db, root, now):
    found = videos(root)
    for key, video in found.items():
        row = db.execute('SELECT * FROM videos WHERE id=?', (key,)).fetchone()
        if row and row['status'] in {'done', 'baseline'}:
            continue
        try:
            sig = signature(video, sidecar(video, root))
        except OSError:
            continue
        relative = str(video.relative_to(root))
        if not row:
            db.execute('INSERT INTO videos(id,path,status,signature,changed) VALUES (?,?,?,?,?)',
                       (key, relative, 'pending', sig, now))
            log.info('Detected new video: %s', key)
        elif row['signature'] != sig:
            db.execute("UPDATE videos SET path=?, signature=?, changed=?, status='pending', attempts=0, retry_at=0, error=NULL WHERE id=?",
                       (relative, sig, now, key))
        elif row['path'] != relative:
            db.execute('UPDATE videos SET path=? WHERE id=?', (relative, key))
    db.commit()
    return found


def deliver(key, title, pack):
    """Private answer rows; deterministic IDs make crash recovery safe."""
    with SessionLocal() as db:
        count = 0
        for user_id in db.scalars(select(User.id)).all():
            job_id = sha256(f'news-video:{key}:A2:{user_id}'.encode()).hexdigest()[:32]
            if db.get(ReadingPractice, job_id):
                continue
            db.add(ReadingPractice(id=job_id, user_id=user_id, level='A2', source='news',
                                   source_key=key, source_title=title, pack=pack, answers={},
                                   status='ready', stage='Lista'))
            count += 1
        db.commit()
    return count


def publish(key, video, subtitle, root, output):
    output.mkdir(parents=True, exist_ok=True)
    destination = output / f'news-{key}-a2'
    staging = output / f'.news-{key}-a2.pending'
    # Never follow a pre-existing output symlink or overwrite unrelated folders.
    for directory in (destination, staging):
        if directory.is_symlink():
            raise ValueError('Output directory must not be a symlink')
    work = destination if destination.exists() else staging
    work.mkdir(exist_ok=True)
    cache = work / 'ejercicio.json'
    if cache.exists():
        pack = json.loads(cache.read_text(encoding='utf-8'))
        if pack.get('video_key') != key:
            raise ValueError('Output belongs to a different source')
    else:
        if destination.exists() or any(p.name != '.ejercicio.json.tmp' for p in work.iterdir()):
            raise ValueError('Refusing to overwrite existing output')
        raw = subtitle.read_text(encoding='utf-8-sig')
        # Use this newly detected video, never a random older news source.
        duration = min(300, max((seconds(m['end']) for m in TIMING.finditer(raw)), default=0))
        transcript = clean_subtitles(raw, 0, duration)
        pack, audit = reading.generate_pack(transcript, reading.model_args('A2'),
                                            lambda stage: log.info('%s: %s', key, stage))
        pack.update(source=video.stem, subtitle_source=str(subtitle.relative_to(root)),
                    video_key=key, start=0, duration=duration)
        # Cache the successful LLM result before optional PDF/export steps.
        temporary = work / '.ejercicio.json.tmp'
        temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(cache)
        (work / 'subtitulos.txt').write_text(transcript, encoding='utf-8')
        (work / 'resumenes.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    if work == staging:
        ensure_audio(work)
        for name, content in render(pack).items():
            (work / name).write_text(content, encoding='utf-8')
        make_pdf(work.resolve(), None)
        work.rename(destination)
    count = deliver(key, video.stem, pack)
    log.info('%s: ready in %s; delivered to %s accounts', key, destination, count)


def scan(db, root, output, now=None, stable_seconds=120):
    now = time.time() if now is None else now
    initialize(db, root, now)
    if not root.is_dir():
        log.warning('News folder unavailable; keeping tracking records unchanged')
        return
    found = discover(db, root, now)
    rows = db.execute("SELECT * FROM videos WHERE status='pending' AND signature IS NOT NULL AND changed<=? AND retry_at<=? ORDER BY changed",
                      (now - stable_seconds, now)).fetchall()
    for row in rows:
        video = found.get(row['id'])
        if not video:
            continue
        try:
            with reading.generation_slot():
                sub = sidecar(video, root)
                if signature(video, sub) != row['signature']:
                    continue
                publish(row['id'], video, sub, root, output)
            db.execute("UPDATE videos SET status='done', error=NULL WHERE id=?", (row['id'],))
            db.commit()
        except BlockingIOError:
            log.info('Local reading generator busy; will retry on next scan')
            return
        except Exception as error:
            attempts = row['attempts'] + 1
            db.execute('UPDATE videos SET attempts=?, retry_at=?, status=?, error=? WHERE id=?',
                       (attempts, now + 600 * attempts, 'failed' if attempts >= 3 else 'pending',
                        type(error).__name__, row['id']))
            db.commit()
            log.error('%s: attempt %s failed (%s)', row['id'], attempts, type(error).__name__)
        # One job per scan; keeps retries and folder discovery moving fairly.
        return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=settings.reading_news_dir)
    parser.add_argument('--output', type=Path, default=Path('/srv/files/static/SpanishReading'))
    parser.add_argument('--ledger', type=Path, default=settings.backup_dir / 'news-reading-watcher.sqlite3')
    parser.add_argument('--initialize', action='store_true', help='Baseline existing videos without generation')
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    if args.initialize and args.ledger.exists():
        with connect(args.ledger) as db:
            if db.execute("SELECT 1 FROM meta WHERE key='initialized'").fetchone():
                log.info('Watcher already initialized; preserving pending and completed records')
                return
    with watcher_slot(args.ledger), connect(args.ledger) as db:
        if args.initialize:
            initialize(db, args.root.resolve(), time.time())
            return
        while True:
            try:
                scan(db, args.root.resolve(), args.output.resolve())
            except Exception as error:
                log.error('Folder scan failed (%s); retrying in 60 seconds', type(error).__name__)
                if args.once:
                    raise
            if args.once:
                return
            time.sleep(60)


if __name__ == '__main__':
    main()
