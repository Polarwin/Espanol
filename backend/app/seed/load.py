"""Seed command: populate the DB with the hand-made lessons and placeholder media.

Idempotent: wipes existing lesson content (and attempts referencing it) and
re-seeds. Run from the project root:

    ./bin/python -m backend.app.seed.load
"""

import shutil
import subprocess
from pathlib import Path

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from ..config import settings
from ..db import SessionLocal
from ..models import Attempt, Exercise, Lesson, Phrase, Segment, UserState
from .content import LESSONS

VIDEO_SECONDS = 12
AUDIO_SECONDS = 5


def _run_ffmpeg(args: list[str], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *args, str(out)]
    subprocess.run(cmd, check=True)


def _media_paths(slug: str, audio_indexes: list[int]) -> tuple[str, dict[int, str]]:
    video_path = f"seed/{slug}/video.mp4"
    audio_paths = {
        i: f"seed/{slug}/exercise-{i}.mp3" for i in audio_indexes
    }
    return video_path, audio_paths


def generate_media(slug: str, audio_indexes: list[int]) -> None:
    """Create a placeholder video and per-exercise tone audio under content/seed/."""
    base = Path(settings.content_dir) / "seed" / slug
    _run_ffmpeg(
        [
            "-f", "lavfi", "-i", f"color=c=0xf5e6d3:s=640x360:d={VIDEO_SECONDS}",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={VIDEO_SECONDS}",
            "-shortest", "-pix_fmt", "yuv420p",
        ],
        base / "video.mp4",
    )
    for order_index in audio_indexes:
        freq = 440 + 40 * (order_index % 5)
        _run_ffmpeg(
            ["-f", "lavfi", "-i", f"sine=frequency={freq}:duration={AUDIO_SECONDS}"],
            base / f"exercise-{order_index}.mp3",
        )


def wipe(db: Session, remove_media: bool = True) -> None:
    """Remove all lesson content plus rows that reference it."""
    db.execute(update(UserState).values(current_lesson_id=None, current_step="mira", current_clip_index=0))
    db.execute(delete(Attempt))
    db.execute(delete(Exercise))
    db.execute(delete(Phrase))
    db.execute(delete(Segment))
    db.execute(delete(Lesson))
    db.flush()
    if remove_media:
        seed_dir = Path(settings.content_dir) / "seed"
        if seed_dir.exists():
            shutil.rmtree(seed_dir)


def seed_db(db: Session, media: bool = True) -> None:
    """Wipe and re-seed all lesson content into the given session.

    With media=False, only DB rows are written (media paths are still set);
    used by the test suite to avoid invoking ffmpeg.
    """
    wipe(db, remove_media=media)
    for lesson_data in LESSONS:
        _insert_lesson(db, lesson_data, media)
    db.commit()


def sync_missing_lessons(db: Session, media: bool = True) -> int:
    """Add catalog lessons that are absent without changing attempts or user state."""
    existing = set(db.scalars(select(Lesson.title)).all())
    missing = [lesson for lesson in LESSONS if lesson["title"] not in existing]
    for lesson_data in missing:
        _insert_lesson(db, lesson_data, media)
    db.commit()
    return len(missing)


def _insert_lesson(db: Session, lesson_data: dict, media: bool) -> None:
    audio_indexes = [i for i, ex in enumerate(lesson_data["exercises"]) if ex.get("audio")]
    if media:
        generate_media(lesson_data["slug"], audio_indexes)
    video_path, audio_paths = _media_paths(lesson_data["slug"], audio_indexes)
    lesson = Lesson(
        title=lesson_data["title"], cefr_level=lesson_data["cefr_level"],
        topics=lesson_data["topics"], source=lesson_data["source"], status=lesson_data["status"],
        duration_seconds=int(lesson_data["segments"][-1]["end"]), video_path=video_path,
        grammar_tip=lesson_data["grammar_tip"],
    )
    db.add(lesson)
    db.flush()
    for index, seg in enumerate(lesson_data["segments"]):
        segment = Segment(lesson_id=lesson.id, index=index, start_seconds=seg["start"], end_seconds=seg["end"], transcript=seg["transcript"])
        db.add(segment)
        db.flush()
        for phrase in seg["phrases"]:
            db.add(Phrase(segment_id=segment.id, text=phrase["text"], translation=phrase["translation"], tip=phrase["tip"]))
    for order_index, ex in enumerate(lesson_data["exercises"]):
        db.add(Exercise(lesson_id=lesson.id, type=ex["type"], instructions=ex["instructions"], prompt=ex["prompt"], audio_path=audio_paths.get(order_index), options=ex["options"], expected_answer=ex["expected_answer"], skill_weights=ex["skill_weights"], order_index=order_index))


def load() -> None:
    db = SessionLocal()
    try:
        seed_db(db, media=True)
        counts = db.query(Lesson).count(), db.query(Exercise).count()
        print(f"Seeded {counts[0]} lessons and {counts[1]} exercises into {settings.database_url}")
    finally:
        db.close()


def main() -> None:
    load()


if __name__ == "__main__":
    main()
