"""Phrase matching for local pronunciation feedback."""

from backend.app.services.pronunciation import score_pronunciation


def test_exact_pronunciation_ignores_case_and_punctuation() -> None:
    result = score_pronunciation("¡Buenos días, María!", "buenos días María")
    assert result["score"] == 100
    assert result["feedback"].startswith("¡Excelente!")


def test_missing_word_receives_targeted_feedback() -> None:
    result = score_pronunciation(
        "Este sábado voy a visitar Madrid",
        "Este sábado voy visitar Madrid",
    )
    assert result["score"] < 100
    assert {item["word"] for item in result["word_scores"] if item["score"] < 70} == {"a"}
    assert "a" in result["feedback"]
