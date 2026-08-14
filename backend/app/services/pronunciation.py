"""Local Spanish speech transcription and phrase-level scoring."""

from difflib import SequenceMatcher
from pathlib import Path
import re
import threading
import unicodedata

from faster_whisper import WhisperModel

from ..config import settings

_model: WhisperModel | None = None
_model_lock = threading.Lock()
_transcribe_lock = threading.Lock()


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = WhisperModel(
                    settings.whisper_model,
                    device=settings.whisper_device,
                    compute_type=settings.whisper_compute_type,
                    local_files_only=True,
                )
    return _model


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return " ".join(re.findall(r"[\wáéíóúüñ]+", text, flags=re.UNICODE))


def transcribe_spanish(audio_path: Path, expected_phrase: str) -> str:
    with _transcribe_lock:
        segments, _ = _get_model().transcribe(
            str(audio_path),
            language="es",
            beam_size=3,
            vad_filter=True,
            initial_prompt=f"Práctica de español. Frase: {expected_phrase}",
        )
        return " ".join(segment.text.strip() for segment in segments).strip()


def score_pronunciation(expected: str, transcription: str) -> dict:
    expected_words = _normalize(expected).split()
    spoken_words = _normalize(transcription).split()
    matcher = SequenceMatcher(None, expected_words, spoken_words)
    scores = [20] * len(expected_words)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for index in range(i1, i2):
                scores[index] = 100
        elif tag == "replace":
            replacements = spoken_words[j1:j2]
            for offset, index in enumerate(range(i1, i2)):
                heard = replacements[min(offset, len(replacements) - 1)] if replacements else ""
                scores[index] = max(20, round(100 * SequenceMatcher(None, expected_words[index], heard).ratio()))

    word_scores = [
        {"word": word, "score": score}
        for word, score in zip(expected_words, scores, strict=True)
    ]
    score = round(sum(scores) / len(scores)) if scores else 0
    weak = [item["word"] for item in word_scores if item["score"] < 70]
    if not spoken_words:
        feedback = "No oímos una frase clara. Acércate al micrófono y vuelve a intentarlo."
    elif score >= 90:
        feedback = "¡Excelente! La frase se entendió con mucha claridad."
    elif score >= 75:
        feedback = "¡Muy bien! Repite una vez más para ganar fluidez."
    elif weak:
        feedback = f"Buen intento. Practica especialmente: {', '.join(weak[:3])}."
    else:
        feedback = "Buen intento. Habla un poco más despacio y vuelve a probar."
    return {
        "score": score,
        "transcription": transcription,
        "feedback": feedback,
        "word_scores": word_scores,
    }
