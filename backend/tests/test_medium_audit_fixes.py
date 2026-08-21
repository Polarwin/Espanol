"""Regression coverage for the remaining medium-severity audit fixes."""

import json
import os
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models import Exercise, Lesson
from backend.app.seed import load as seed_load
from backend.app.seed.content import LESSONS
from backend.app.seed.load import seed_db, sync_lesson_enrichment
from backend.app.seed.video_fetch import _cached_transcript, _source_sha256
from backend.app.services import speech


def test_failed_media_staging_preserves_live_db_and_media(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "content_dir", tmp_path)
    marker = tmp_path / "seed" / "existing" / "video.mp4"
    marker.parent.mkdir(parents=True)
    marker.write_bytes(b"working media")
    before = db_session.scalar(select(func.count()).select_from(Lesson))

    def fail_generation(_lesson: dict, _root: Path | None = None) -> None:
        raise RuntimeError("simulated renderer failure")

    monkeypatch.setattr(seed_load, "generate_media", fail_generation)
    with pytest.raises(RuntimeError, match="renderer failure"):
        seed_db(db_session, media=True)
    assert marker.read_bytes() == b"working media"
    assert db_session.scalar(select(func.count()).select_from(Lesson)) == before


def test_enrichment_reconciles_all_fields_and_generates_missing_audio(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "content_dir", tmp_path)
    lesson_data = next(
        lesson for lesson in LESSONS if any(item.get("audio") for item in lesson["exercises"])
    )
    authored_index, authored = next(
        (index, item) for index, item in enumerate(lesson_data["exercises"]) if item.get("audio")
    )
    lesson = db_session.scalar(select(Lesson).where(Lesson.title == lesson_data["title"]))
    exercise = next(item for item in lesson.exercises if item.prompt == authored["prompt"])
    exercise.instructions = "stale"
    exercise.expected_answer = "stale"
    exercise.skill_weights = {"grammar": 99}
    exercise.audio_path = None

    def fake_audio(data: dict, index: int, content_root: Path | None = None) -> str:
        relative = f"seed/{data['slug']}/exercise-{index}.mp3"
        destination = (content_root or tmp_path) / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"audio")
        return relative

    monkeypatch.setattr(seed_load, "generate_exercise_audio", fake_audio)
    sync_lesson_enrichment(db_session, media=True)
    expected_path = f"seed/{lesson_data['slug']}/exercise-{authored_index}.mp3"
    assert exercise.instructions == authored["instructions"]
    assert exercise.expected_answer == authored["expected_answer"]
    assert exercise.skill_weights == authored["skill_weights"]
    assert exercise.audio_path == expected_path
    assert (tmp_path / expected_path).read_bytes() == b"audio"


def test_transcript_cache_is_bound_to_video_hash(tmp_path: Path) -> None:
    first = tmp_path / "first.mp4"
    second = tmp_path / "second.mp4"
    first.write_bytes(b"first video")
    second.write_bytes(b"second video")
    segments = [{"start": 0, "end": 1, "text": "hola"}]
    cache = tmp_path / "unit.transcript.json"
    cache.write_text(json.dumps({"source_sha256": _source_sha256(first), "segments": segments}))
    assert _cached_transcript(cache, _source_sha256(first)) == segments
    assert _cached_transcript(cache, _source_sha256(second)) is None


def test_speech_cache_prunes_old_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "speech_cache_max_files", 2)
    monkeypatch.setattr(settings, "speech_cache_max_bytes", 100)
    files = []
    for index in range(4):
        path = tmp_path / f"{index}.mp3"
        path.write_bytes(b"x" * 10)
        os.utime(path, (index + 1, index + 1))
        files.append(path)
    speech._prune_cache(tmp_path, keep=files[-1])
    assert sorted(path.name for path in tmp_path.glob("*.mp3")) == ["2.mp3", "3.mp3"]
