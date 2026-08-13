"""Flexible streak tracking.

Rules (kept deliberately simple, per the product strategy):
- Activity on the same day leaves the streak unchanged.
- Activity the day after the last activity increments the streak.
- Missing 1-2 days is forgiven by spending recovery days (max 2 per ISO week);
  the streak then continues instead of resetting.
- Missing more than the available recovery days resets the streak to 1.
- recovery_days_used resets at the start of each new ISO week.
"""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Streak, User

MAX_RECOVERY_DAYS_PER_WEEK = 2


def get_or_create_streak(db: Session, user: User) -> Streak:
    streak = db.scalar(select(Streak).where(Streak.user_id == user.id))
    if streak is None:
        streak = Streak(user_id=user.id)
        db.add(streak)
        db.flush()
    return streak


def record_activity(db: Session, user: User, today: date | None = None) -> Streak:
    """Record one day of learning activity and update the flexible streak."""
    today = today or date.today()
    streak = get_or_create_streak(db, user)
    last = streak.last_activity_date

    if last == today:
        return streak

    # New ISO week: recovery budget resets before we spend any of it.
    if last is None or last.isocalendar()[:2] != today.isocalendar()[:2]:
        streak.recovery_days_used = 0

    if last is not None:
        missed = (today - last - timedelta(days=1)).days
    else:
        missed = 0

    if missed <= 0:
        streak.current_days += 1
    elif missed <= MAX_RECOVERY_DAYS_PER_WEEK and streak.recovery_days_used + missed <= MAX_RECOVERY_DAYS_PER_WEEK:
        streak.recovery_days_used += missed
        streak.current_days += 1
    else:
        streak.current_days = 1
        streak.recovery_days_used = 0

    streak.longest_days = max(streak.longest_days, streak.current_days)
    streak.last_activity_date = today
    db.flush()
    return streak
