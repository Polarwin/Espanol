"""Unit tests for RTVE news lesson generation (requests.get is mocked)."""

import re
from pathlib import Path

import pytest

from backend.app.seed import news_content

THEMES = {
    "17100001": ["gobierno", "mercado", "ciudad", "vecinos", "puente", "alcalde"],
    "17100002": ["museo", "pintura", "artista", "galería", "cuadro", "exposición"],
    "17100003": ["volcán", "isla", "erupción", "ceniza", "científicos", "registro"],
    "17100010": ["gobierno", "mercado", "ciudad", "vecinos", "puente", "alcalde"],
    "17100020": ["gobierno", "mercado", "ciudad", "vecinos", "puente", "alcalde"],
    "17100021": ["museo", "pintura", "artista", "galería", "cuadro", "exposición"],
}


def _fake_text(words: list[str], n_sentences: int) -> str:
    sentences = [
        f"La {words[i % len(words)]} número {i} confirma nuevos datos "
        f"sobre la {words[(i + 1) % len(words)]} regional del país."
        for i in range(n_sentences)
    ]
    paragraphs = "".join(f"<p>{s}</p>" for s in sentences)
    return f"<div>{paragraphs}</div>"


def _fake_item(article_id: str, title: str, category: str, n_sentences: int) -> dict:
    return {
        "id": article_id,
        "title": title,
        "mainCategory": category,
        "publicationDate": "17-08-2026 10:00:00",
        "text": _fake_text(THEMES[article_id], n_sentences),
    }


FIXTURE_ITEMS = [
    _fake_item("17100001", "El puente de la ciudad reabre al tráfico", "Noticias/España/Galicia", 16),
    _fake_item("17100002", "Un museo recupera una pintura perdida", "Noticias/Cultura", 16),
    # 28 sentences x ~13 words + markers > 300 words -> C2 by the length rule.
    _fake_item("17100003", "El volcán de la isla sigue en erupción", "Noticias/Mundo", 28),
]


class _FakeResponse:
    def __init__(self, items: list[dict]) -> None:
        self._items = items

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"page": {"items": self._items}}


@pytest.fixture()
def mock_rtve(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    monkeypatch.setattr(
        news_content.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_ITEMS)
    )
    return news_content.fetch_news_lessons(count=10)


def _word_in(word: str, sentence: str) -> bool:
    return re.search(rf"\b{re.escape(word.lower())}\b", sentence.lower()) is not None


def test_lesson_shape(mock_rtve: list[dict]) -> None:
    assert len(mock_rtve) == 3
    for lesson in mock_rtve:
        assert lesson["slug"].startswith("news-")
        assert lesson["title"].startswith("Noticias: ")
        assert lesson["cefr_level"] in ("C1", "C2")
        assert lesson["topics"][0] == "noticias"
        assert lesson["source"] == "rtve"
        assert lesson["status"] == "published"
        assert set(lesson["grammar_tip"]) == {"wrong", "right", "explanation"}
        assert len(lesson["segments"]) == 2
        # Segments are contiguous and every transcript line carries "es"/"en".
        assert lesson["segments"][0]["start"] == 0.0
        assert lesson["segments"][0]["end"] == lesson["segments"][1]["start"]
        assert lesson["segments"][1]["end"] > lesson["segments"][1]["start"]
        for segment in lesson["segments"]:
            assert segment["transcript"], "segment needs transcript lines"
            for line in segment["transcript"]:
                assert line["es"].strip()
                assert line["en"] == ""
        types = [ex["type"] for ex in lesson["exercises"]]
        assert types.count("reading") == 2
        assert "vocabulary" in types and "listening" in types


def test_slug_and_title_are_deterministic(mock_rtve: list[dict]) -> None:
    again = news_content.fetch_news_lessons(count=10)
    assert sorted(l["slug"] for l in mock_rtve) == sorted(l["slug"] for l in again)
    assert sorted(l["title"] for l in mock_rtve) == sorted(l["title"] for l in again)
    assert {l["slug"] for l in mock_rtve} == {
        "news-17100001", "news-17100002", "news-17100003"
    }


def test_vocabulary_cloze_answer_guarantees(mock_rtve: list[dict]) -> None:
    for lesson in mock_rtve:
        vocab = next(ex for ex in lesson["exercises"] if ex["type"] == "vocabulary")
        answer = vocab["expected_answer"]
        assert answer in vocab["options"]
        assert "___" in vocab["prompt"]
        # The unmasked sentence (second transcript line) contains the answer.
        original = lesson["segments"][0]["transcript"][1]["es"]
        assert _word_in(answer, original)
        # Distractors are real article words but do not fit the masked slot.
        distractors = [o for o in vocab["options"] if o != answer]
        assert len(distractors) == 2
        for distractor in distractors:
            assert not _word_in(distractor, original)
            assert any(
                _word_in(distractor, line["es"])
                for seg in lesson["segments"]
                for line in seg["transcript"]
            )


def test_reading_answers_verbatim_and_distractors_foreign(mock_rtve: list[dict]) -> None:
    own_sentences = {
        lesson["slug"]: {
            line["es"] for seg in lesson["segments"] for line in seg["transcript"]
        }
        for lesson in mock_rtve
    }
    for lesson in mock_rtve:
        reading = [ex for ex in lesson["exercises"] if ex["type"] == "reading"]
        assert len(reading) == 2
        for ex in reading:
            assert ex["passage"]
            # The correct option is a verbatim sentence inside the passage.
            assert ex["expected_answer"] in ex["options"]
            assert ex["expected_answer"] in ex["passage"]
            assert ex["expected_answer"] in own_sentences[lesson["slug"]]
            # Distractors come from OTHER articles of the same run.
            for option in ex["options"]:
                if option == ex["expected_answer"]:
                    continue
                assert option not in ex["passage"]
                assert option not in own_sentences[lesson["slug"]]
                assert any(
                    option in sentences
                    for slug, sentences in own_sentences.items()
                    if slug != lesson["slug"]
                )


def test_listening_exercise_speaks_the_lead(mock_rtve: list[dict]) -> None:
    for lesson in mock_rtve:
        listening = next(ex for ex in lesson["exercises"] if ex["type"] == "listening")
        lead = lesson["segments"][0]["transcript"][0]["es"]
        assert listening["audio"] is True
        assert listening["audio_text"] == lead
        assert listening["expected_answer"] in listening["options"]
        # Cloze variant: the masked word is in the spoken lead.
        assert _word_in(listening["expected_answer"], lead)
        assert "___" in listening["prompt"]


def test_cefr_level_heuristic(mock_rtve: list[dict]) -> None:
    levels = {lesson["slug"]: lesson["cefr_level"] for lesson in mock_rtve}
    assert levels["news-17100001"] == "C1"
    assert levels["news-17100002"] == "C1"
    assert levels["news-17100003"] == "C2"  # > 300 words
    opinion = {"category": "Noticias/Opinión", "words": 150}
    assert news_content._cefr_level(opinion) == "C2"
    short = {"category": "Noticias/Sociedad", "words": 150}
    assert news_content._cefr_level(short) == "C1"


def test_network_failure_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(*a: object, **k: object) -> object:
        raise news_content.requests.ConnectionError("offline")

    monkeypatch.setattr(news_content.requests, "get", _boom)
    assert news_content.fetch_news_lessons(count=5) == []


def test_non_spanish_articles_are_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    galician = {
        "id": "17100099",
        "title": "Sen servizos, sen casas nos concellos",
        "mainCategory": "Noticias/España/Galicia",
        "text": "".join(
            f"<p>A ponte número {i} confirma novos datos sobre a comarca galega do país e da provincia.</p>"
            for i in range(16)
        ),
    }
    monkeypatch.setattr(
        news_content.requests,
        "get",
        lambda *a, **k: _FakeResponse([*FIXTURE_ITEMS, galician]),
    )
    lessons = news_content.fetch_news_lessons(count=10)
    assert len(lessons) == 3
    assert all(lesson["slug"] != "news-17100099" for lesson in lessons)


def test_grammar_tip_matches_whole_words_only() -> None:
    # "perro" must not trigger the «pero» connector.
    tip = news_content._grammar_tip("El perro corre por el parque con energía.")
    assert "«pero»" not in tip["right"]
    # A real standalone connector is still found.
    tip = news_content._grammar_tip("La medida es útil, pero genera debate.")
    assert "«pero»" in tip["right"]


def _lesson_from_items(monkeypatch: pytest.MonkeyPatch, items: list[dict]) -> list[dict]:
    monkeypatch.setattr(
        news_content.requests, "get", lambda *a, **k: _FakeResponse(items)
    )
    return news_content.fetch_news_lessons(count=10)


def test_empty_title_falls_back_to_article_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    item = _fake_item("17100010", "", "Noticias/España", 16)
    lessons = _lesson_from_items(monkeypatch, [*FIXTURE_ITEMS, item])
    lesson = next(lesson for lesson in lessons if lesson["slug"] == "news-17100010")
    assert lesson["title"] == "Noticias: Artículo 17100010 · 17100010"


def test_truncated_identical_titles_do_not_collide(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    long_title = (
        "El puente de la ciudad reabre al tráfico tras meses de obras y muchas "
        "celebraciones vecinales"
    )
    first = _fake_item("17100020", long_title, "Noticias/España", 16)
    second = _fake_item("17100021", long_title, "Noticias/España", 16)
    lessons = _lesson_from_items(monkeypatch, [first, second, FIXTURE_ITEMS[1]])
    news = [lesson for lesson in lessons if lesson["slug"].startswith("news-1710002")]
    assert len(news) == 2
    titles = [lesson["title"] for lesson in news]
    assert len(set(titles)) == 2
    assert all(title.startswith("Noticias: ") for title in titles)
    assert {lesson["slug"].removeprefix("news-") for lesson in news} == {
        "17100020",
        "17100021",
    }
    for lesson in news:
        assert lesson["slug"].removeprefix("news-") in lesson["title"]


def test_cached_news_lessons_replay_without_network(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cache = tmp_path / "news-cache.json"
    monkeypatch.setattr(
        news_content.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_ITEMS)
    )
    fetched = news_content.get_news_lessons(count=3, cache_path=cache)
    assert len(fetched) == 3
    assert news_content.load_cached_news_lessons(cache) == fetched

    def _no_fetch(count: int = 10) -> list[dict]:
        raise AssertionError("the network must not be touched when the cache suffices")

    monkeypatch.setattr(news_content, "fetch_news_lessons", _no_fetch)
    assert news_content.get_news_lessons(count=3, cache_path=cache) == fetched
    assert news_content.get_news_lessons(count=0, cache_path=cache) == fetched


def test_short_cache_is_topped_up_and_merged_without_duplicates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cache = tmp_path / "news-cache.json"
    monkeypatch.setattr(
        news_content.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_ITEMS)
    )
    first = news_content.get_news_lessons(count=2, cache_path=cache)
    assert len(first) == 2
    second = news_content.get_news_lessons(count=3, cache_path=cache)
    assert len(second) == 3
    slugs = [lesson["slug"] for lesson in news_content.load_cached_news_lessons(cache)]
    assert len(slugs) == len(set(slugs))


def test_fetch_failure_keeps_existing_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cache = tmp_path / "news-cache.json"
    monkeypatch.setattr(
        news_content.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_ITEMS[:1])
    )
    cached = news_content.get_news_lessons(count=1, cache_path=cache)
    assert len(cached) == 1

    def _boom(*a: object, **k: object) -> object:
        raise news_content.requests.ConnectionError("offline")

    monkeypatch.setattr(news_content.requests, "get", _boom)
    assert news_content.get_news_lessons(count=5, cache_path=cache) == cached
