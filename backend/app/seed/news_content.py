"""C1/C2 lessons generated on the fly from RTVE news articles.

Articles come from the RTVE public API listing:

    https://www.rtve.es/api/noticias.json?size=60&page=<n>

Quirks found while probing the API (August 2026):

- ``page`` (1-based) or ``offset`` paginate; the ``number`` parameter is
  silently ignored and always returns the first page.
- The listing mixes press notes, orchestra program sheets and weather
  summaries with real news, so we keep only items whose ``mainCategory``
  starts with ``Noticias/`` and whose plain text is 120-400 words long.
  Roughly 6 such articles exist per 60-item page, so we read several pages.
- Thematic listing endpoints under ``api.rtve.es/api/tematicas/...`` all
  return 404; the general listing above is the working source.
- ``page.items[].text`` is HTML; it is stripped with stdlib html.parser.

CEFR heuristic: pieces whose category mentions "opinión" or that run over
300 words are marked C2 (longer, denser prose); everything else is C1.

Every exercise answer is guaranteed by construction from the article text:
clozes mask a word taken verbatim from a real sentence, and reading/listening
questions use verbatim sentences as correct options with sentences from
OTHER articles fetched in the same run as distractors. Nothing is invented.
"""

import json
import random
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import requests

from ..config import settings

LISTING_URL = "https://www.rtve.es/api/noticias.json"
PAGE_SIZE = 60
DEFAULT_PAGES = 4
MIN_WORDS = 120
MAX_WORDS = 400
C2_WORD_THRESHOLD = 300
SECONDS_PER_WORD = 0.49  # matches the gTTS pacing used in curriculum_content._unit
MIN_SENTENCES = 4

# Ordered from most to least interesting; "que" appears in every Spanish
# text, so the grammar tip always has a factual connector to point at.
CONNECTORS = [
    "sin embargo", "no obstante", "además", "por lo tanto", "por el contrario",
    "mientras tanto", "a pesar de", "de hecho", "aunque", "mientras",
    "porque", "según", "también", "pero", "que",
]

# Function words excluded when picking cloze candidates and distractors.
STOPWORDS = {
    "a", "al", "con", "de", "del", "el", "en", "es", "la", "las", "lo",
    "los", "por", "para", "que", "se", "su", "sus", "un", "una", "y", "o",
    "como", "más", "pero", "sin", "sobre", "tras", "este", "esta", "estos",
    "estas", "ese", "esa", "esos", "esas", "aquel", "han", "has", "hay",
    "ser", "son", "fue", "era", "desde", "hasta", "entre", "donde", "cuando",
    "porque", "aunque", "según", "también", "muy", "ya", "no", "sí", "les",
    "nos", "me", "te", "le", "ello", "ello", "cada", "otro", "otra", "otros",
    "otras", "todo", "toda", "todos", "todas", "puede", "pueden", "podría",
    "debe", "deben", "haber", "hacer", "hace", "está", "están", "estaba",
    "durante", "contra", "hacia", "según", "unos", "unas", "dos", "tres",
    "gran", "nuevo", "nueva", "primer", "primera", "parte", "años", "año",
}


class _HTMLStripper(HTMLParser):
    """Collects text nodes; block-level tags become sentence boundaries."""

    BLOCK_TAGS = {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "tr"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append(" . ")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _strip_html(html: str) -> str:
    stripper = _HTMLStripper()
    stripper.feed(html or "")
    return re.sub(r"\s+", " ", " ".join(stripper.parts).replace("\xa0", " ")).strip(" .")


def _split_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?…])\s+", text)
    return [s.strip() for s in sentences if len(s.split()) >= 5]


# RTVE also publishes items in co-official languages (Galician, Catalan).
# Frequent Spanish function words vs. Galician/Catalan-only ones tell them
# apart reliably at article length.
_ES_MARKERS = {"el", "la", "los", "las", "y", "del", "está", "son", "pero"}
_NON_ES_MARKERS = {
    "e", "os", "as", "do", "da", "na", "i", "els", "les", "amb", "però",
    "són", "està", "dun", "dunha",
}


def _is_spanish(text: str) -> bool:
    words = re.findall(r"[a-záéíóúüñ]+", text.lower())
    es = sum(1 for word in words if word in _ES_MARKERS)
    non_es = sum(1 for word in words if word in _NON_ES_MARKERS)
    return es >= 5 and non_es <= max(2, es // 3)


def _fetch_articles(pages: int = DEFAULT_PAGES) -> list[dict[str, Any]]:
    """Fetch and normalize usable news articles; empty list on any failure."""
    seen: set[str] = set()
    articles: list[dict[str, Any]] = []
    for page in range(1, pages + 1):
        try:
            response = requests.get(
                LISTING_URL, params={"size": PAGE_SIZE, "page": page}, timeout=30
            )
            response.raise_for_status()
            items = response.json().get("page", {}).get("items", [])
        except (requests.RequestException, ValueError):
            break
        if not items:
            break
        for item in items:
            article_id = str(item.get("id", ""))
            category = item.get("mainCategory") or ""
            if not article_id or article_id in seen:
                continue
            if not category.startswith("Noticias/"):
                continue
            text = _strip_html(item.get("text") or "")
            if not _is_spanish(text):
                continue
            words = len(text.split())
            sentences = _split_sentences(text)
            if not (MIN_WORDS <= words <= MAX_WORDS):
                continue
            if len(sentences) < MIN_SENTENCES:
                continue
            seen.add(article_id)
            articles.append(
                {
                    "id": article_id,
                    "title": (item.get("title") or "").strip(),
                    "category": category,
                    "text": text,
                    "words": words,
                    "sentences": sentences,
                }
            )
    return articles


def _short_title(title: str, limit: int = 60) -> str:
    if len(title) <= limit:
        return title
    cut = title[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + "…"


def _category_tail(category: str) -> str:
    tail = category.split("/")[-1].strip().lower().replace(" ", "-")
    return tail or "general"


def _cefr_level(article: dict[str, Any]) -> str:
    if "opini" in article["category"].lower() or article["words"] > C2_WORD_THRESHOLD:
        return "C2"
    return "C1"


def _grammar_tip(text: str) -> dict[str, str]:
    lower = text.lower()
    # Word boundaries: «pero» must not match inside «perro».
    connector = next(
        (c for c in CONNECTORS if re.search(rf"\b{re.escape(c)}\b", lower)), "que"
    )
    return {
        "wrong": "En las noticias en español no se usan conectores.",
        "right": f"Esta noticia usa el conector «{connector}».",
        "explanation": (
            f"Localiza «{connector}» en el texto: los conectores organizan "
            "las ideas en la prosa periodística."
        ),
    }


def _content_words(article: dict[str, Any], min_length: int = 6) -> list[str]:
    """Distinct lowercase content words of the article, in order of appearance."""
    found: list[str] = []
    for word in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", article["text"].lower()):
        if len(word) >= min_length and word not in STOPWORDS and word not in found:
            found.append(word)
    return found


def _cloze(
    sentence: str, candidates: list[str]
) -> tuple[str, list[str], str] | None:
    """Mask the first candidate word present in the sentence.

    Returns (prompt, options, answer); distractors are content words from the
    same article that do NOT appear in the sentence, so the original word is
    the only verbatim-correct option.
    """
    lower = sentence.lower()
    sentence_words = set(re.findall(r"[a-záéíóúüñ]+", lower))
    for word in candidates:
        match = re.search(rf"\b{re.escape(word)}\b", lower)
        if not match:
            continue
        distractors = [
            w for w in candidates if w != word and w not in sentence_words
        ][:2]
        if len(distractors) < 2:
            continue
        prompt = sentence[: match.start()] + "___" + sentence[match.end() :]
        return prompt, [word, *distractors], word
    return None


def _segments(article: dict[str, Any]) -> list[dict[str, Any]]:
    sentences = article["sentences"]
    half = (len(sentences) + 1) // 2
    chunks = [sentences[:half], sentences[half:]]
    segments: list[dict[str, Any]] = []
    start = 0.0
    for chunk in chunks:
        duration = sum(len(s.split()) for s in chunk) * SECONDS_PER_WORD
        phrase_text = " ".join(chunk[0].split()[:8]).rstrip(",;:") + "…"
        segments.append(
            {
                "start": start,
                "end": start + duration,
                "transcript": [{"es": s, "en": ""} for s in chunk],
                "phrases": [
                    {
                        "text": phrase_text,
                        "translation": "",
                        "tip": "Frase destacada de la noticia.",
                    }
                ],
            }
        )
        start += duration
    return segments


def _other_sentences(
    pool: list[list[str]], limit: int = 4
) -> list[str]:
    flat = [s for sentences in pool for s in sentences]
    return flat[:limit]


def _build_lesson(
    article: dict[str, Any], other_pools: list[list[str]]
) -> dict[str, Any] | None:
    sentences = article["sentences"]
    candidates = _content_words(article)
    lead = sentences[0]
    passage = " ".join(sentences[:3])

    vocab = _cloze(sentences[1], candidates)
    listening_cloze = _cloze(lead, candidates)
    if vocab is None:
        return None  # cannot guarantee a correct-by-construction cloze

    exercises: list[dict[str, Any]] = [
        {
            "type": "vocabulary",
            "instructions": "Completa la frase de la noticia con la palabra correcta.",
            "prompt": vocab[0],
            "options": vocab[1],
            "expected_answer": vocab[2],
            "skill_weights": {"vocabulary": 1.0},
        },
    ]

    distractors = [s for s in _other_sentences(other_pools) if s not in sentences]
    if len(distractors) >= 4:
        instructions = "Lee el texto y elige la opción correcta."
        exercises.append(
            {
                "type": "reading",
                "instructions": instructions,
                "prompt": "¿Qué frase aparece en el texto?",
                "passage": passage,
                "options": [sentences[0], distractors[0], distractors[1]],
                "expected_answer": sentences[0],
                "skill_weights": {"reading": 1.0},
            }
        )
        exercises.append(
            {
                "type": "reading",
                "instructions": instructions,
                "prompt": "¿Cuál de estas afirmaciones es correcta según el texto?",
                "passage": passage,
                "options": [sentences[2], distractors[2], distractors[3]],
                "expected_answer": sentences[2],
                "skill_weights": {"reading": 1.0},
            }
        )

    if listening_cloze is not None:
        exercises.append(
            {
                "type": "listening",
                "instructions": "Escucha el audio y completa la frase.",
                "prompt": listening_cloze[0],
                "options": listening_cloze[1],
                "expected_answer": listening_cloze[2],
                "audio": True,
                "audio_text": lead,
                "skill_weights": {"listening": 1.0},
            }
        )
    elif len(distractors) >= 2:
        exercises.append(
            {
                "type": "listening",
                "instructions": "Escucha el audio y elige la frase que has oído.",
                "prompt": "¿Qué frase has escuchado?",
                "options": [lead, distractors[0], distractors[1]],
                "expected_answer": lead,
                "audio": True,
                "audio_text": lead,
                "skill_weights": {"listening": 1.0},
            }
        )

    # Empty titles fall back to the article id; the id suffix keeps titles
    # unique even when two articles share a 60-char truncated title (lesson
    # dedup keys on title).
    title = article["title"] or f"Artículo {article['id']}"
    return {
        "slug": f"news-{article['id']}",
        "title": f"Noticias: {_short_title(title)} · {article['id']}",
        "cefr_level": _cefr_level(article),
        "topics": ["noticias", _category_tail(article["category"])],
        "source": "rtve",
        "status": "published",
        "grammar_tip": _grammar_tip(article["text"]),
        "segments": _segments(article),
        "exercises": exercises,
    }


def fetch_news_lessons(count: int = 10) -> list[dict[str, Any]]:
    """Fetch RTVE news and build up to `count` lesson dicts.

    Articles are drawn with random.sample, so every run brings different news.
    Slug ("news-<id>") and title are deterministic per article, so re-running
    against the same article does not duplicate rows (sync_missing_lessons
    keys on title).
    """
    articles = _fetch_articles()
    if not articles:
        return []
    selected = random.sample(articles, min(count, len(articles)))
    lessons: list[dict[str, Any]] = []
    for article in selected:
        other_pools = [a["sentences"] for a in selected if a["id"] != article["id"]]
        lesson = _build_lesson(article, other_pools)
        if lesson is not None:
            lessons.append(lesson)
    return lessons


# Fetched news lessons are persisted to ``content/news-cache.json`` (tracked
# in git) so a plain reseed replays them instead of silently shrinking the
# catalog; the network is only touched when the cache is missing or short.


def news_cache_path() -> Path:
    return Path(settings.content_dir) / "news-cache.json"


def load_cached_news_lessons(cache_path: Path | None = None) -> list[dict[str, Any]]:
    """Read the persisted news lessons; empty list when absent or unreadable."""
    path = cache_path or news_cache_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def save_news_cache(
    lessons: list[dict[str, Any]], cache_path: Path | None = None
) -> None:
    path = cache_path or news_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(lessons, ensure_ascii=False, indent=1), encoding="utf-8")


def get_news_lessons(
    count: int = 0, cache_path: Path | None = None
) -> list[dict[str, Any]]:
    """Cache-first news lessons for seeding.

    Replays the cache when it holds at least ``count`` lessons (or when
    ``count`` is 0 — a plain reseed never touches the network); otherwise
    fetches from RTVE and merges new articles into the cache.
    """
    cached = load_cached_news_lessons(cache_path)
    if len(cached) >= count or count <= 0:
        return cached
    fetched = fetch_news_lessons(count)
    if not fetched:
        return cached
    known = {lesson["slug"] for lesson in cached}
    merged = cached + [lesson for lesson in fetched if lesson["slug"] not in known]
    save_news_cache(merged, cache_path)
    return merged
