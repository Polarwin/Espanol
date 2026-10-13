#!/usr/bin/env python3
"""Add current HTML, flashcards and offline preload to existing published packs."""
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.config import settings
from tools.subtitle_reading import render
from tools.reading_folder_cache import publish_folder_worker
from tools.watch_news_readings import watcher_slot


def main():
    root = settings.reading_static_dir.resolve()
    backup = settings.backup_dir / ('reading-html-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    count = 0
    with watcher_slot(settings.backup_dir / 'news-reading-watcher.sqlite3'):
        publish_folder_worker(root)
        for cache in sorted(root.glob('*/*/*/ejercicio.json')):
            if not cache.resolve().is_relative_to(root):
                continue
            directory = cache.parent
            pack = json.loads(cache.read_text(encoding='utf-8'))
            for field, name in [('audio_file', 'lectura.mp3'), ('pdf_file', 'ejercicio.pdf')]:
                if (directory / name).is_file():
                    pack[field] = name
                else:
                    pack.pop(field, None)
            pages = render(pack)
            saved = backup / directory.relative_to(root)
            saved.mkdir(parents=True, exist_ok=True)
            # Write the service worker last so its install sees a complete set.
            for name, content in pages.items():
                destination = directory / name
                if destination.is_symlink():
                    raise ValueError('Refusing a symlink export')
                if destination.exists():
                    shutil.copy2(destination, saved / name)
                temporary = directory / ('.' + name + '.refresh')
                temporary.write_text(content, encoding='utf-8')
                temporary.replace(destination)
            count += 1
    print(json.dumps({'updated': count, 'backup': str(backup)}))


if __name__ == '__main__':
    main()
