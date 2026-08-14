"""Generate and cache short Spanish example phrases as MP3 files."""

from hashlib import sha256
from pathlib import Path
from threading import Lock

from gtts import gTTS

from ..config import settings

_generation_lock = Lock()


def spanish_example_audio(phrase: str) -> Path:
    normalized = " ".join(phrase.split()).strip()
    if not normalized:
        raise ValueError("Phrase is empty")

    cache_dir = settings.content_dir / "generated" / "speech"
    cache_dir.mkdir(parents=True, exist_ok=True)
    destination = cache_dir / f"{sha256(normalized.encode('utf-8')).hexdigest()}.mp3"
    if destination.exists() and destination.stat().st_size > 0:
        return destination

    with _generation_lock:
        if destination.exists() and destination.stat().st_size > 0:
            return destination
        temporary = destination.with_suffix(".tmp.mp3")
        try:
            gTTS(normalized, lang="es", tld="es", slow=False).save(str(temporary))
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
    return destination
