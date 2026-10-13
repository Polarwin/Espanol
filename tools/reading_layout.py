"""Shared locations for dated reading exports and legacy audio lookup."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LEVELS = ('A1', 'A2', 'B1', 'B2')


def local_day(timestamp=None):
    return datetime.fromtimestamp(timestamp, ZoneInfo('Europe/Madrid')).date().isoformat() if timestamp is not None else datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat()


def find_export(root, key, level):
    root = Path(root).resolve()
    name = f'news-{key}-{level.lower()}'
    for path in [root / name, *sorted((root / level).glob(f'????-??-??/{name}'))]:
        if path.is_dir() and path.resolve().is_relative_to(root):
            return path
    return None


def export_directory(root, key, level, day=None):
    root = Path(root).resolve()
    existing = find_export(root, key, level)
    if existing:
        return existing
    path = root / level / (day or local_day()) / f'news-{key}-{level.lower()}'
    if not path.resolve().is_relative_to(root):
        raise ValueError('Export path escapes the static root')
    return path
