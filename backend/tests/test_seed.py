"""Seed catalog integrity: no global mutation, portable media paths."""

from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import Lesson
from backend.app.seed.content import LESSONS
from backend.app.seed.load import seed_db


def test_seed_db_works_on_a_local_catalog_without_mutating_lessons(
    db_session: Session,
) -> None:
    before = len(LESSONS)
    extra = dict(LESSONS[0], title="Noticias: de prueba · 1", slug="news-test-1")
    seed_db(db_session, media=False, lessons=[*LESSONS, extra])
    assert db_session.scalar(select(func.count()).select_from(Lesson)) == before + 1
    # A second in-process seed must not accumulate duplicates in the global.
    seed_db(db_session, media=False, lessons=[*LESSONS, extra])
    assert db_session.scalar(select(func.count()).select_from(Lesson)) == before + 1
    assert len(LESSONS) == before


def test_source_video_paths_are_relative_to_the_content_dir() -> None:
    paths = [
        lesson["source_video"]["path"]
        for lesson in LESSONS
        if lesson.get("source_video")
    ]
    assert paths
    assert all(not Path(path).is_absolute() for path in paths)
