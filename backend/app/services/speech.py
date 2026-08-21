"""Generate and cache short Spanish example phrases as MP3 files."""

from hashlib import sha256
from pathlib import Path
from threading import Lock

from gtts import gTTS

from ..config import settings

_generation_lock = Lock()


def _prune_cache(cache_dir: Path, keep: Path | None = None) -> None:
    files = sorted(
        (path for path in cache_dir.glob("*.mp3") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    kept = 0
    retained_bytes = 0
    for path in files:
        size = path.stat().st_size
        allowed = (
            path == keep
            or (
                kept < settings.speech_cache_max_files
                and retained_bytes + size <= settings.speech_cache_max_bytes
            )
        )
        if allowed:
            kept += 1
            retained_bytes += size
            continue
        path.unlink(missing_ok=True)


def spanish_example_audio(phrase: str) -> Path:
    normalized = " ".join(phrase.split()).strip()
    if not normalized:
        raise ValueError("Phrase is empty")

    cache_dir = settings.content_dir / "generated" / "speech"
    cache_dir.mkdir(parents=True, exist_ok=True)
    destination = cache_dir / f"{sha256(normalized.encode('utf-8')).hexdigest()}.mp3"
    if destination.exists() and destination.stat().st_size > 0:
        destination.touch()
        return destination

    with _generation_lock:
        if destination.exists() and destination.stat().st_size > 0:
            return destination
        temporary = destination.with_suffix(".tmp.mp3")
        try:
            gTTS(normalized, lang="es", tld="es", slow=False).save(str(temporary))
            temporary.replace(destination)
            _prune_cache(cache_dir, keep=destination)
        finally:
            temporary.unlink(missing_ok=True)
    return destination
