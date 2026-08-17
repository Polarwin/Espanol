"""FastAPI application entry point."""

import logging
from logging.handlers import RotatingFileHandler
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import auth, capabilities, exercises, lessons, path, placement, progress, review, social

settings.log_file.parent.mkdir(parents=True, exist_ok=True)
request_logger = logging.getLogger("vamos.requests")
request_logger.setLevel(logging.INFO)
request_logger.propagate = False
if not request_logger.handlers:
    handler = RotatingFileHandler(
        settings.log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%dT%H:%M:%S%z")
    )
    request_logger.addHandler(handler)

app = FastAPI(title="¡Vamos! — Spanish Learning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request(request: Request, call_next):
    """Write compact request diagnostics without logging bodies or credentials."""
    request_id = request.headers.get("X-Request-ID") or uuid4().hex[:12]
    started = perf_counter()
    client = request.client.host if request.client else "unknown"
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started) * 1000
        request_logger.exception(
            "request_id=%s client=%s method=%s path=%s status=500 duration_ms=%.1f",
            request_id, client, request.method, request.url.path, duration_ms,
        )
        raise
    duration_ms = (perf_counter() - started) * 1000
    request_logger.info(
        "request_id=%s client=%s method=%s path=%s status=%s duration_ms=%.1f",
        request_id, client, request.method, request.url.path, response.status_code, duration_ms,
    )
    response.headers["X-Request-ID"] = request_id
    return response

app.include_router(auth.router)
app.include_router(auth.me_router)
app.include_router(path.router)
app.include_router(lessons.router)
app.include_router(exercises.router)
app.include_router(progress.router)
app.include_router(social.router)
app.include_router(capabilities.router)
app.include_router(placement.router)
app.include_router(review.router)

settings.content_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.content_dir), name="media")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
