"""Seed command: populate the DB with lessons and matching spoken Spanish media.

Idempotent: wipes existing lesson content (and attempts referencing it) and
re-seeds. Run from the project root:

    ./bin/python -m backend.app.seed.load

Previously fetched RTVE news lessons are replayed from
``content/news-cache.json``; pass ``--news N`` to top the cache up to N
lessons from the network before reseeding.
"""

import logging
import shutil
import subprocess
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from gtts import gTTS

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from ..config import settings
from ..db import SessionLocal
from ..models import Attempt, Exercise, Lesson, LessonCompletion, Phrase, Segment, UserState
from ..services.backup import backup_database
from .content import LESSONS

logger = logging.getLogger("vamos.seed")

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


def generate_exercise_audio(
    lesson_data: dict, order_index: int, content_root: Path | None = None
) -> str | None:
    """Generate one authored audio exercise and return its relative media path."""
    exercise = lesson_data["exercises"][order_index]
    if not exercise.get("audio"):
        return None
    root = content_root or Path(settings.content_dir)
    relative = f"seed/{lesson_data['slug']}/exercise-{order_index}.mp3"
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    spoken = exercise.get("audio_text") or exercise["expected_answer"]
    gTTS(spoken, lang="es", tld="es", slow=exercise["type"] == "pronunciation").save(
        str(destination)
    )
    return relative


def generate_media(lesson_data: dict, content_root: Path | None = None) -> None:
    """Create spoken Spanish lesson media matching the authored seed content."""
    root = content_root or Path(settings.content_dir)
    base = root / "seed" / lesson_data["slug"]
    base.mkdir(parents=True, exist_ok=True)
    lines = [line["es"] for segment in lesson_data["segments"] for line in segment["transcript"]]
    source_video = lesson_data.get("source_video")
    if source_video:
        # Seed data stores source paths relative to the content dir (portable
        # across machines); resolve them against the media root at use time.
        source_path = Path(source_video["path"])
        if not source_path.is_absolute():
            source_path = root / source_path
        _run_ffmpeg(
            [
                "-ss", str(source_video["start"]), "-t", str(source_video["end"] - source_video["start"]),
                "-i", str(source_path), "-map", "0:v:0", "-map", "0:a:0",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            ],
            base / "video.mp4",
        )
    else:
        with TemporaryDirectory() as temp_dir:
            narration = Path(temp_dir) / "narration.mp3"
            gTTS(" ".join(lines), lang="es", tld="es", slow=False).save(str(narration))
            duration = _media_duration(narration)
            # Clean video: subtitles are shown by the player's toggleable
            # caption overlay instead of being burned into the frames.
            _run_ffmpeg(
                [
                    "-f", "lavfi", "-i", f"color=c=0x16324f:s=960x540:d={duration:.2f}",
                    "-i", str(narration),
                    "-shortest", "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                ],
                base / "video.mp4",
            )
    for order_index in range(len(lesson_data["exercises"])):
        generate_exercise_audio(lesson_data, order_index, root)


def _media_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return max(float(result.stdout.strip()), 1.0)


def wipe(db: Session, remove_media: bool = True) -> None:
    """Remove lesson rows; media is swapped safely by :func:`seed_db`.

    ``remove_media`` remains for call compatibility but intentionally never
    performs an irreversible filesystem delete inside a DB transaction.
    """
    backup_database(db)
    db.execute(update(UserState).values(current_lesson_id=None, current_step="mira", current_clip_index=0))
    db.execute(delete(Attempt))
    db.execute(delete(LessonCompletion))
    db.execute(delete(Exercise))
    db.execute(delete(Phrase))
    db.execute(delete(Segment))
    db.execute(delete(Lesson))
    db.flush()


def seed_db(db: Session, media: bool = True, lessons: list[dict] | None = None) -> None:
    """Wipe and re-seed all lesson content into the given session.

    ``lessons`` defaults to the import-time LESSONS catalog; callers (e.g.
    load() adding cached news lessons) pass a combined list instead of
    mutating the global.

    With media=False, only DB rows are written (media paths are still set);
    used by the test suite to avoid invoking ffmpeg.
    """
    catalog = LESSONS if lessons is None else lessons
    if not media:
        wipe(db, remove_media=False)
        for lesson_data in catalog:
            _insert_lesson(db, lesson_data, media=False)
        db.commit()
        return

    content_root = Path(settings.content_dir)
    content_root.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".seed-staging-", dir=content_root) as temp_dir:
        staging_root = Path(temp_dir)
        # Finish every fallible download/render before touching DB rows or live media.
        for lesson_data in catalog:
            generate_media(lesson_data, staging_root)

        wipe(db, remove_media=False)
        for lesson_data in catalog:
            _insert_lesson(db, lesson_data, media=False)
        db.flush()
        reconcile_media_timings(db, content_root=staging_root, commit=False)

        live_seed = content_root / "seed"
        staged_seed = staging_root / "seed"
        previous_seed = content_root / f".seed-previous-{uuid4().hex}"
        if live_seed.exists():
            live_seed.rename(previous_seed)
        staged_seed.rename(live_seed)
        try:
            db.commit()
        except Exception:
            db.rollback()
            if live_seed.exists():
                shutil.rmtree(live_seed)
            if previous_seed.exists():
                previous_seed.rename(live_seed)
            raise
        else:
            if previous_seed.exists():
                shutil.rmtree(previous_seed)


def sync_missing_lessons(db: Session, media: bool = True) -> int:
    """Add catalog lessons that are absent without changing attempts or user state."""
    existing = set(db.scalars(select(Lesson.title)).all())
    missing = [lesson for lesson in LESSONS if lesson["title"] not in existing]
    for lesson_data in missing:
        _insert_lesson(db, lesson_data, media)
    # Flush before the enrichment pass: SessionLocal runs with autoflush=False,
    # so the last inserted segment's phrases are still pending and would
    # otherwise be re-inserted by sync_lesson_enrichment's dedup check.
    db.flush()
    sync_lesson_enrichment(db, media=media)
    db.commit()
    if media:
        updated, missing_media = reconcile_media_timings(db)
        if updated:
            logger.info("Reconciled media timings for %d lessons", updated)
        if missing_media:
            logger.warning("Lessons missing media files: %s", ", ".join(missing_media))
    return len(missing)


def sync_lesson_enrichment(db: Session, media: bool = True) -> tuple[int, int]:
    """Add newly authored phrases/exercises without replacing learner history."""
    phrases_added = 0
    exercises_added = 0
    for lesson_data in LESSONS:
        lesson = db.scalar(select(Lesson).where(Lesson.title == lesson_data["title"]))
        if lesson is None:
            continue
        segments = {segment.index: segment for segment in lesson.segments}
        for index, authored in enumerate(lesson_data["segments"]):
            segment = segments.get(index)
            if segment is None:
                continue
            existing = {phrase.text for phrase in segment.phrases}
            for phrase in authored["phrases"]:
                if phrase["text"] not in existing:
                    db.add(Phrase(segment_id=segment.id, **phrase))
                    existing.add(phrase["text"])
                    phrases_added += 1

        existing_by_key = {(exercise.type, exercise.prompt): exercise for exercise in lesson.exercises}
        seen = set(existing_by_key)
        next_order = max((exercise.order_index for exercise in lesson.exercises), default=-1) + 1
        for authored_index, authored in enumerate(lesson_data["exercises"]):
            key = (authored["type"], authored["prompt"])
            relative_audio = (
                f"seed/{lesson_data['slug']}/exercise-{authored_index}.mp3"
                if authored.get("audio") else None
            )
            if key in seen:
                # Reconcile every authored mutable field with the source.
                existing_exercise = existing_by_key.get(key)
                if existing_exercise is not None:
                    existing_exercise.instructions = authored["instructions"]
                    existing_exercise.options = authored["options"]
                    existing_exercise.passage = authored.get("passage")
                    existing_exercise.expected_answer = authored["expected_answer"]
                    existing_exercise.skill_weights = authored["skill_weights"]
                    existing_exercise.audio_path = relative_audio
                    if media and relative_audio and not (Path(settings.content_dir) / relative_audio).is_file():
                        generate_exercise_audio(lesson_data, authored_index)
                continue
            if media and relative_audio:
                generate_exercise_audio(lesson_data, authored_index)
            db.add(
                Exercise(
                    lesson_id=lesson.id,
                    type=authored["type"], instructions=authored["instructions"],
                    prompt=authored["prompt"], passage=authored.get("passage"),
                    audio_path=relative_audio, options=authored["options"],
                    expected_answer=authored["expected_answer"],
                    skill_weights=authored["skill_weights"], order_index=next_order,
                )
            )
            next_order += 1
            seen.add(key)
            exercises_added += 1
    return phrases_added, exercises_added


def refresh_lesson_content(db: Session, title: str, media: bool = True) -> None:
    """Refresh one lesson's media/transcript without deleting attempts or user progress."""
    lesson_data = next((item for item in LESSONS if item["title"] == title), None)
    lesson = db.scalar(select(Lesson).where(Lesson.title == title))
    if lesson_data is None or lesson is None:
        raise ValueError(f"Unknown lesson: {title}")
    if media:
        generate_media(lesson_data)
    lesson.source = lesson_data["source"]
    lesson.duration_seconds = int(lesson_data["segments"][-1]["end"])
    lesson.grammar_tip = lesson_data["grammar_tip"]
    existing = {segment.index: segment for segment in lesson.segments}
    for index, authored in enumerate(lesson_data["segments"]):
        segment = existing.pop(index, None)
        if segment is None:
            segment = Segment(
                lesson_id=lesson.id, index=index,
                start_seconds=authored["start"], end_seconds=authored["end"],
                transcript=authored["transcript"],
            )
            db.add(segment)
            db.flush()
        segment.start_seconds = authored["start"]
        segment.end_seconds = authored["end"]
        segment.transcript = authored["transcript"]
        for phrase in list(segment.phrases):
            db.delete(phrase)
        db.flush()
        for phrase in authored["phrases"]:
            db.add(Phrase(segment_id=segment.id, **phrase))
    for segment in existing.values():
        for phrase in list(segment.phrases):
            db.delete(phrase)
        db.delete(segment)
    db.commit()


def reconcile_media_timings(
    db: Session, content_root: Path | None = None, commit: bool = True
) -> tuple[int, list[str]]:
    """Scale transcript segments to each real video so every caption is reachable."""
    updated = 0
    missing: list[str] = []
    lessons = db.scalars(select(Lesson).where(Lesson.status == "published")).all()
    for lesson in lessons:
        path = (content_root or Path(settings.content_dir)) / lesson.video_path
        if not path.exists():
            missing.append(lesson.title)
            continue
        actual = _media_duration(path)
        authored_end = max((segment.end_seconds for segment in lesson.segments), default=0.0)
        if authored_end <= 0:
            continue
        scale = actual / authored_end
        if abs(scale - 1.0) > 0.01:
            for segment in lesson.segments:
                segment.start_seconds = round(segment.start_seconds * scale, 2)
                segment.end_seconds = round(segment.end_seconds * scale, 2)
            updated += 1
        lesson.duration_seconds = max(1, math.ceil(actual))
    if commit:
        db.commit()
    return updated, missing


def _insert_lesson(db: Session, lesson_data: dict, media: bool) -> None:
    audio_indexes = [i for i, ex in enumerate(lesson_data["exercises"]) if ex.get("audio")]
    if media:
        generate_media(lesson_data)
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
        db.add(Exercise(lesson_id=lesson.id, type=ex["type"], instructions=ex["instructions"], prompt=ex["prompt"], passage=ex.get("passage"), audio_path=audio_paths.get(order_index), options=ex["options"], expected_answer=ex["expected_answer"], skill_weights=ex["skill_weights"], order_index=order_index))


def load(news: int = 0) -> None:
    from .news_content import get_news_lessons

    # Cache-first: a plain reseed replays previously fetched news lessons and
    # never touches the network; --news N tops the cache up to N lessons.
    news_lessons = get_news_lessons(news)
    if news_lessons:
        print(f"Including {len(news_lessons)} RTVE news lessons (content/news-cache.json)")
    # Seed from a local combined catalog; the module-global LESSONS is never mutated.
    lessons = [*LESSONS, *news_lessons]
    db = SessionLocal()
    try:
        seed_db(db, media=True, lessons=lessons)
        counts = db.query(Lesson).count(), db.query(Exercise).count()
        print(f"Seeded {counts[0]} lessons and {counts[1]} exercises into {settings.database_url}")
    finally:
        db.close()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--news",
        type=int,
        default=0,
        metavar="N",
        help="also fetch N random RTVE news lessons (0 = no network access)",
    )
    args = parser.parse_args()
    load(news=args.news)


if __name__ == "__main__":
    main()
