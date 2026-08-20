"""Regression tests for production secrets and destructive-operation backups."""

import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.config import Settings
from backend.app.models import Lesson, LessonCompletion
from backend.app.seed.load import wipe
from backend.app.services.backup import backup_database_path


def test_production_rejects_committed_development_secret() -> None:
    with pytest.raises(ValueError, match="Production requires"):
        Settings(environment="production", jwt_secret_file=None, _env_file=None)


def test_sqlite_backup_is_complete_and_private(tmp_path: Path) -> None:
    source = tmp_path / "source.db"
    with sqlite3.connect(source) as database:
        database.execute("CREATE TABLE example (value TEXT NOT NULL)")
        database.execute("INSERT INTO example VALUES ('preserved')")
    target = backup_database_path(source, tmp_path / "backups")
    assert target is not None
    assert target.stat().st_mode & 0o077 == 0
    with sqlite3.connect(target) as database:
        assert database.execute("SELECT value FROM example").fetchone() == ("preserved",)


def test_wipe_removes_stale_lesson_completions(db_session: Session) -> None:
    lesson_id = db_session.scalar(select(Lesson.id).limit(1))
    db_session.add(LessonCompletion(user_id=1, lesson_id=lesson_id))
    db_session.flush()
    wipe(db_session, remove_media=False)
    assert db_session.scalar(select(func.count()).select_from(LessonCompletion)) == 0
