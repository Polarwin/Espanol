"""Seed command: populate the DB with lessons and matching spoken Spanish media.

Idempotent: wipes existing lesson content (and attempts referencing it) and
re-seeds. Run from the project root:

    ./bin/python -m backend.app.seed.load
"""

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from gtts import gTTS

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from ..config import settings
from ..db import SessionLocal
from ..models import Attempt, Exercise, Lesson, Phrase, Segment, UserState
from .content import LESSONS

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


def generate_media(lesson_data: dict) -> None:
    """Create spoken Spanish lesson media matching the authored seed content."""
    base = Path(settings.content_dir) / "seed" / lesson_data["slug"]
    base.mkdir(parents=True, exist_ok=True)
    lines = [line["es"] for segment in lesson_data["segments"] for line in segment["transcript"]]
    source_video = lesson_data.get("source_video")
    if source_video:
        _run_ffmpeg(
            [
                "-ss", str(source_video["start"]), "-t", str(source_video["end"] - source_video["start"]),
                "-i", source_video["path"], "-map", "0:v:0", "-map", "0:a:0",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            ],
            base / "video.mp4",
        )
    else:
        with TemporaryDirectory() as temp_dir:
            narration = Path(temp_dir) / "narration.mp3"
            subtitles = Path(temp_dir) / "subtitles.srt"
            gTTS(" ".join(lines), lang="es", tld="es", slow=False).save(str(narration))
            duration = _media_duration(narration)
            subtitles.write_text(_srt(lines, duration), encoding="utf-8")
            _run_ffmpeg(
                [
                    "-f", "lavfi", "-i", f"color=c=0x16324f:s=960x540:d={duration:.2f}",
                    "-i", str(narration),
                    "-vf", f"subtitles={subtitles}:force_style='FontName=DejaVu Sans,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=3,Outline=1,MarginV=42'",
                    "-shortest", "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                ],
                base / "video.mp4",
            )
    for order_index, exercise in enumerate(lesson_data["exercises"]):
        if exercise.get("audio"):
            spoken = exercise["expected_answer"]
            gTTS(spoken, lang="es", tld="es", slow=exercise["type"] == "pronunciation").save(
                str(base / f"exercise-{order_index}.mp3")
            )


def _media_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return max(float(result.stdout.strip()), 1.0)


def _srt(lines: list[str], duration: float) -> str:
    per_line = duration / max(len(lines), 1)
    blocks = []
    for index, line in enumerate(lines, start=1):
        blocks.append(f"{index}\n{_srt_time((index - 1) * per_line)} --> {_srt_time(index * per_line)}\n{line}\n")
    return "\n".join(blocks)


def _srt_time(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


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
    sync_lesson_enrichment(db)
    db.commit()
    return len(missing)


def sync_lesson_enrichment(db: Session) -> tuple[int, int]:
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

        existing_exercises = {(exercise.type, exercise.prompt) for exercise in lesson.exercises}
        next_order = max((exercise.order_index for exercise in lesson.exercises), default=-1) + 1
        for authored in lesson_data["exercises"]:
            key = (authored["type"], authored["prompt"])
            if key in existing_exercises:
                continue
            db.add(
                Exercise(
                    lesson_id=lesson.id,
                    type=authored["type"], instructions=authored["instructions"],
                    prompt=authored["prompt"], audio_path=None, options=authored["options"],
                    expected_answer=authored["expected_answer"],
                    skill_weights=authored["skill_weights"], order_index=next_order,
                )
            )
            next_order += 1
            existing_exercises.add(key)
            exercises_added += 1
    return phrases_added, exercises_added


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
