"""Exercise scoring: normalized text comparison, option matching, writing heuristic."""

import re
import unicodedata
from dataclasses import dataclass

from ..models import Exercise

SUCCESS_DELTA = 2.0  # per unit of skill weight, scaled by score
FAILURE_DELTA = -1.0  # per unit of skill weight
MIN_WRITING_WORDS = 3

_PUNCTUATION = re.compile(r"[¿?¡!.,;:\"'()\-—]")


def normalize(text: str) -> str:
    """Case/accent/punctuation-insensitive normalization for text answers."""
    text = text.strip().lower()
    text = "".join(
        ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn"
    )
    text = _PUNCTUATION.sub(" ", text)
    return " ".join(text.split())


@dataclass
class ScoreResult:
    correct: bool
    score: float  # 0-1
    feedback: str
    deltas: dict[str, float]  # per-skill signed delta, weighted by exercise.skill_weights


def score_attempt(exercise: Exercise, answer: str) -> ScoreResult:
    answer = answer.strip()
    if exercise.type == "writing":
        correct, score, feedback = _score_writing(answer)
    elif exercise.options:
        correct = answer == exercise.expected_answer.strip()
        score = 1.0 if correct else 0.0
        feedback = _feedback(correct, exercise.expected_answer)
    else:
        correct = normalize(answer) == normalize(exercise.expected_answer)
        score = 1.0 if correct else 0.0
        feedback = _feedback(correct, exercise.expected_answer)

    if correct:
        deltas = {
            skill: round(SUCCESS_DELTA * weight * score, 2)
            for skill, weight in (exercise.skill_weights or {}).items()
        }
    else:
        deltas = {
            skill: round(FAILURE_DELTA * weight, 2)
            for skill, weight in (exercise.skill_weights or {}).items()
        }
    return ScoreResult(correct=correct, score=score, feedback=feedback, deltas=deltas)


def _score_writing(answer: str) -> tuple[bool, float, str]:
    words = len(answer.split())
    if words >= MIN_WRITING_WORDS:
        return True, 0.8, "¡Bien escrito! Tu respuesta ha sido aceptada."
    if words > 0:
        return False, 0.0, "Escribe un poco más: tu respuesta es demasiado corta."
    return False, 0.0, "La respuesta está vacía. Inténtalo de nuevo."


def _feedback(correct: bool, expected_answer: str) -> str:
    if correct:
        return "¡Correcto!"
    return f"Casi. La respuesta correcta es: {expected_answer}"
