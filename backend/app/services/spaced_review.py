"""SM-2 spaced repetition on top of the review_items table.

Standard SM-2:
- quality >= 3 (pass): repetitions += 1; interval grows 1 -> 6 -> round(prev * EF).
- quality < 3 (fail): repetitions reset to 0; interval back to 1 day.
- Easiness factor: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02)), floored at 1.3.
"""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Exercise, Phrase, ReviewItem, Segment, User

MIN_EASINESS = 1.3
DEFAULT_EASINESS = 2.5

# Map exercise types to review item kinds.
_REVIEW_KINDS = {"vocabulary", "grammar", "pronunciation"}


def week_start_of(day: date) -> date:
    """Monday of the ISO week containing `day`."""
    return day - timedelta(days=day.weekday())


def _apply_sm2(item: ReviewItem, quality: int, today: date) -> None:
    quality = max(0, min(5, quality))
    item.easiness = max(
        MIN_EASINESS,
        item.easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )
    if quality >= 3:
        item.repetitions += 1
        if item.repetitions == 1:
            item.interval_days = 1
        elif item.repetitions == 2:
            item.interval_days = 6
        else:
            item.interval_days = round(item.interval_days * item.easiness)
    else:
        item.repetitions = 0
        item.interval_days = 1
    item.last_reviewed = today
    item.due_date = today + timedelta(days=item.interval_days)


def record_result(db: Session, item: ReviewItem, quality: int, today: date | None = None) -> ReviewItem:
    _apply_sm2(item, quality, today or date.today())
    db.flush()
    return item


def due_items(db: Session, user: User, limit: int | None = None, today: date | None = None) -> list[ReviewItem]:
    today = today or date.today()
    query = (
        select(ReviewItem)
        .where(ReviewItem.user_id == user.id, ReviewItem.due_date <= today)
        .order_by(ReviewItem.due_date, ReviewItem.id)
    )
    if limit is not None:
        query = query.limit(limit)
    return list(db.scalars(query))


def create_review_item(
    db: Session, user: User, kind: str, content: dict, today: date | None = None
) -> ReviewItem:
    """Create a review item due today, skipping exact duplicates (user+kind+content)."""
    existing = db.scalar(
        select(ReviewItem).where(
            ReviewItem.user_id == user.id,
            ReviewItem.kind == kind,
            ReviewItem.content == content,
        )
    )
    if existing is not None:
        return existing
    item = ReviewItem(
        user_id=user.id,
        kind=kind,
        content=content,
        easiness=DEFAULT_EASINESS,
        interval_days=1,
        repetitions=0,
        due_date=today or date.today(),
    )
    db.add(item)
    db.flush()
    return item


def review_item_from_failed_exercise(db: Session, user: User, exercise: Exercise) -> ReviewItem | None:
    """Turn a failed vocabulary/grammar/pronunciation exercise into a review item."""
    if exercise.type not in _REVIEW_KINDS:
        return None
    if exercise.type == "vocabulary":
        content = {"word": exercise.prompt, "translation": exercise.expected_answer}
    else:
        content = {"concept": exercise.prompt, "example": exercise.expected_answer}
    return create_review_item(db, user, exercise.type, content)


def review_items_from_lesson(db: Session, user: User, lesson_id: int) -> int:
    """Add the lesson's key phrases as new vocabulary review items (lesson completed).

    Returns the number of items created (duplicates skipped).
    """
    phrases = db.scalars(
        select(Phrase)
        .join(Segment, Phrase.segment_id == Segment.id)
        .where(Segment.lesson_id == lesson_id)
        .order_by(Phrase.id)
    ).all()
    created = 0
    for phrase in phrases:
        before = len(db.new)
        create_review_item(
            db, user, "vocabulary", {"word": phrase.text, "translation": phrase.translation}
        )
        if len(db.new) > before:
            created += 1
    return created
