"""Flexible streak behavior: increments, recovery days, weekly reset."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from backend.app.models import User
from backend.app.services.security import hash_password
from backend.app.services.streak import record_activity

MONDAY = date(2025, 1, 6)  # ISO week 2 of 2025


def _user(db_session: Session) -> User:
    user = User(
        email="streak@example.com",
        password_hash=hash_password("x"),
        display_name="Streak",
        interests=[],
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_consecutive_days_increment(db_session: Session) -> None:
    user = _user(db_session)
    record_activity(db_session, user, MONDAY)
    streak = record_activity(db_session, user, MONDAY + timedelta(days=1))
    assert streak.current_days == 2
    assert streak.longest_days == 2
    assert streak.recovery_days_used == 0


def test_same_day_does_not_double_count(db_session: Session) -> None:
    user = _user(db_session)
    record_activity(db_session, user, MONDAY)
    streak = record_activity(db_session, user, MONDAY)
    assert streak.current_days == 1


def test_one_missed_day_uses_recovery(db_session: Session) -> None:
    user = _user(db_session)
    record_activity(db_session, user, MONDAY)
    record_activity(db_session, user, MONDAY + timedelta(days=1))
    # Wednesday is missed; activity on Thursday spends one recovery day.
    streak = record_activity(db_session, user, MONDAY + timedelta(days=3))
    assert streak.current_days == 3
    assert streak.recovery_days_used == 1


def test_recovery_budget_exceeded_resets(db_session: Session) -> None:
    user = _user(db_session)
    record_activity(db_session, user, MONDAY)
    # One recovery day already spent (Wednesday missed).
    record_activity(db_session, user, MONDAY + timedelta(days=3))
    # Now three days missed (Fri, Sat, Sun -> 3 > 2 budget left) before Monday week 3.
    streak = record_activity(db_session, user, MONDAY + timedelta(days=7))
    assert streak.current_days == 1
    assert streak.longest_days == 2


def test_recovery_days_reset_weekly(db_session: Session) -> None:
    user = _user(db_session)
    record_activity(db_session, user, MONDAY)
    # Tuesday is missed; activity on Wednesday spends one recovery day.
    streak = record_activity(db_session, user, MONDAY + timedelta(days=2))  # recovery 1
    assert streak.recovery_days_used == 1
    # Next activity is the following Monday: new ISO week, budget resets first,
    # then the missed days (Wed-Sun = 4) still exceed the fresh budget of 2.
    streak = record_activity(db_session, user, MONDAY + timedelta(days=7))
    assert streak.current_days == 1

    # Within a fresh week, two missed days fit the budget exactly.
    record_activity(db_session, user, MONDAY + timedelta(days=7))
    streak = record_activity(db_session, user, MONDAY + timedelta(days=10))  # Thu week 3
    assert streak.current_days == 2
    assert streak.recovery_days_used == 2
