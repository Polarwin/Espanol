"""Shared clock: DB columns are naive ``DateTime`` and existing rows are
naive, so timestamps stay naive UTC (``datetime.now(UTC)`` would be aware)."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Current UTC time as a naive datetime, matching the naive columns."""
    return datetime.now(UTC).replace(tzinfo=None)
