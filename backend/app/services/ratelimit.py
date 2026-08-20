"""In-memory sliding-window rate limiting for sensitive or expensive endpoints."""

import threading
import time
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException, Request, status


class SlidingWindowLimiter:
    """Per-key sliding window of call timestamps, pruned on each check."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def allow(
        self, key: str, max_calls: int, window_seconds: int, now: float | None = None
    ) -> bool:
        """Record a call for `key`; return False once `max_calls` is exceeded in the window."""
        now = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and hits[0] <= now - window_seconds:
                hits.popleft()
            if len(hits) >= max_calls:
                return False
            hits.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_limiter = SlidingWindowLimiter()


def reset_rate_limits() -> None:
    """Clear all recorded hits (test isolation)."""
    _limiter.reset()


def rate_limit(max_calls: int, window_seconds: int) -> Callable[[Request], None]:
    """FastAPI dependency: 429 when a client exceeds `max_calls` per window on this route."""

    def dependency(request: Request) -> None:
        host = request.client.host if request.client else "unknown"
        key = f"{host}:{request.url.path}"
        if not _limiter.allow(key, max_calls, window_seconds):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiadas solicitudes. Inténtalo de nuevo en un minuto.",
            )

    return dependency
