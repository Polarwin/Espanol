#!/usr/bin/env python3
"""Move existing flat packs into LEVEL/YYYY-MM-DD folders without regenerating."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.reading_layout import LEVELS, local_day


def plan_moves(root):
    root = root.resolve()
    plans = []
    for directory in sorted(root.iterdir()):
        if directory.name.startswith('.') or directory.name in LEVELS or not directory.is_dir():
            continue
        if directory.is_symlink():
            raise ValueError(f'Refusing symlink: {directory}')
        cache = directory / 'ejercicio.json'
        if not cache.is_file():
            continue
        pack = json.loads(cache.read_text(encoding='utf-8'))
        level = pack.get('level')
        if level not in LEVELS:
            continue
        # MP3 mtime records audio creation; source-video timestamps are not the
        # generation date. Preserve an explicit publication date when available.
        reference = directory / 'lectura.mp3'
        day = pack.get('published_date') or local_day((reference if reference.exists() else cache).stat().st_mtime)
        datetime.strptime(day, '%Y-%m-%d')
        destination = root / level / day / directory.name
        if not destination.resolve().is_relative_to(root) or destination.exists():
            raise ValueError(f'Unsafe or occupied destination: {destination}')
        plans.append((directory, destination, dict(pack, published_date=day,
                                                  export_path=str(destination.relative_to(root)))))
    return plans


def organize(root, backup, apply=False):
    plans = plan_moves(root)
    if apply:
        backup.mkdir(parents=True, exist_ok=False)
        manifest = [{'old': str(old), 'new': str(new)} for old, new, _ in plans]
        (backup / 'moves.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
        for old, new, pack in plans:
            cache = old / 'ejercicio.json'
            (backup / (old.name + '.json')).write_bytes(cache.read_bytes())
            new.parent.mkdir(parents=True, exist_ok=True)
            temporary = old / '.ejercicio.json.layout'
            temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(cache)
            old.rename(new)
    return [{'old': str(old), 'new': str(new)} for old, new, _ in plans]


def main():
    from backend.app.config import settings
    from tools.watch_news_readings import connect, watcher_slot, reconcile_publications
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    ledger = settings.backup_dir / 'news-reading-watcher.sqlite3'
    with watcher_slot(ledger):
        moves = organize(settings.reading_static_dir,
                         settings.backup_dir / ('reading-layout-' + datetime.now().strftime('%Y%m%d-%H%M%S')),
                         apply=args.apply)
        if args.apply:
            for level in LEVELS:
                (settings.reading_static_dir / level).mkdir(exist_ok=True)
            with connect(ledger) as db:
                reconcile_publications(db, settings.reading_static_dir)
    print(json.dumps({'applied': args.apply, 'count': len(moves), 'moves': moves}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
