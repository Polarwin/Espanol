"""Safe, timestamped SQLite backups for production and destructive seed operations."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from ..config import settings

BACKUP_RETENTION = 30


def backup_database_path(source: Path, destination_dir: Path | None = None) -> Path | None:
    if not source.is_file():
        return None
    target_dir = destination_dir or settings.backup_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"vamos-{datetime.now(UTC):%Y%m%dT%H%M%S%fZ}.db"
    with sqlite3.connect(source) as source_db, sqlite3.connect(target) as target_db:
        source_db.backup(target_db)
    target.chmod(0o600)
    backups = sorted(target_dir.glob("vamos-*.db"), key=lambda path: path.stat().st_mtime)
    for old_backup in backups[:-BACKUP_RETENTION]:
        old_backup.unlink()
    return target


def backup_database(db: Session) -> Path | None:
    database = db.get_bind().url.database
    if not database or database == ":memory:":
        return None
    return backup_database_path(Path(database))


if __name__ == "__main__":
    database_url = settings.database_url
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise SystemExit("Automatic backup currently supports SQLite only")
    result = backup_database_path(Path(database_url.removeprefix(prefix)))
    if result is None:
        raise SystemExit("Database file does not exist")
    print(result)
