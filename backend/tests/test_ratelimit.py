"""Sliding-window rate limiting: unit behavior and the login endpoint limit."""

from fastapi.testclient import TestClient

from backend.app.services.ratelimit import SlidingWindowLimiter
from conftest import USER


def test_limiter_allows_up_to_max_calls_then_blocks() -> None:
    limiter = SlidingWindowLimiter()
    assert limiter.allow("key", 3, 60, now=100.0) is True
    assert limiter.allow("key", 3, 60, now=100.0) is True
    assert limiter.allow("key", 3, 60, now=100.0) is True
    assert limiter.allow("key", 3, 60, now=100.0) is False


def test_limiter_prunes_expired_hits() -> None:
    limiter = SlidingWindowLimiter()
    assert limiter.allow("key", 2, 30, now=100.0) is True
    assert limiter.allow("key", 2, 30, now=110.0) is True
    assert limiter.allow("key", 2, 30, now=120.0) is False  # window full
    assert limiter.allow("key", 2, 30, now=131.0) is True  # the 100.0 hit expired
    assert limiter.allow("other", 2, 30, now=131.0) is True  # keys are independent


def test_login_rate_limited(client: TestClient) -> None:
    client.post("/api/auth/register", json=USER)
    for _ in range(10):
        response = client.post(
            "/api/auth/login",
            json={"email": USER["email"], "password": "wrong-password"},
        )
        assert response.status_code == 401
    blocked = client.post(
        "/api/auth/login",
        json={"email": USER["email"], "password": "wrong-password"},
    )
    assert blocked.status_code == 429
