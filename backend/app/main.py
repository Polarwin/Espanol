"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import auth, capabilities, exercises, lessons, path, placement, progress, social

app = FastAPI(title="¡Vamos! — Spanish Learning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(auth.me_router)
app.include_router(path.router)
app.include_router(lessons.router)
app.include_router(exercises.router)
app.include_router(progress.router)
app.include_router(social.router)
app.include_router(capabilities.router)
app.include_router(placement.router)

settings.content_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.content_dir), name="media")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
