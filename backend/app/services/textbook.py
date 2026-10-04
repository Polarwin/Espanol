"""Private, local textbook retrieval for the local language model.

The index is deliberately a SQLite FTS5 database under content/, so the source
PDFs and extracted text never leave this machine and no vector service is
required. Run tools/index_textbooks.py after adding or replacing a PDF.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from ..config import settings

INDEX_PATH = settings.content_dir / "textbook-index.sqlite3"
_WORD_RE = re.compile(r"[\wáéíóúüñÁÉÍÓÚÜÑ]+", re.UNICODE)


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(INDEX_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def available() -> bool:
    return INDEX_PATH.is_file()


def search(query: str, *, limit: int = 4) -> list[dict[str, str | int]]:
    """Return the most relevant local textbook excerpts for a query."""
    if not query.strip() or not available():
        return []
    terms = _WORD_RE.findall(query.lower())
    if not terms:
        return []
    # Prefix matching handles inflected forms without allowing arbitrary SQL.
    expression = " OR ".join(f'"{term.replace(chr(34), "")}"*' for term in terms[:16])
    try:
        with _connect() as connection:
            rows = connection.execute(
                "SELECT source, page, text FROM chunks WHERE chunks MATCH ? "
                "ORDER BY bm25(chunks) LIMIT ?", (expression, max(1, min(limit, 8)))
            ).fetchall()
    except sqlite3.Error:
        return []
    return [dict(row) for row in rows]


def context(query: str, *, limit: int = 3, max_chars: int = 6000) -> str:
    passages = search(query, limit=limit)
    if not passages:
        return ""
    output: list[str] = []
    remaining = max_chars
    for passage in passages:
        label = f"{passage['source']} · p. {passage['page']}"
        text = str(passage['text']).strip()
        block = f"[{label}]\n{text}"
        if len(block) > remaining:
            block = block[:remaining].rsplit(" ", 1)[0] + "…"
        output.append(block)
        remaining -= len(block) + 2
        if remaining < 100:
            break
    return "\n\n".join(output)
