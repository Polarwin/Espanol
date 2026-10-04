#!/usr/bin/env python3
"""OCR the private Ke PDFs and build the local FTS5 textbook index.

Usage: ./bin/python tools/index_textbooks.py [--ocr]
Without --ocr, existing text layers are used. Scanned pages are rendered and
OCR'd with the installed Spanish Tesseract language when --ocr is supplied.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import subprocess
import tempfile
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
KE = ROOT / "Ke"
INDEX = ROOT / "content" / "textbook-index.sqlite3"
CHUNK_CHARS = 2200
OVERLAP = 300


def ocr_pdf(pdf: Path, temporary: Path) -> PdfReader:
    output = temporary / f"{pdf.stem}.ocr.pdf"
    subprocess.run([
        "ocrmypdf", "--deskew", "--force-ocr", "--language", "spa",
        str(pdf), str(output),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return PdfReader(str(output))


def chunks(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    result: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + CHUNK_CHARS)
        if end < len(text):
            split = max(text.rfind(". ", start, end), text.rfind("; ", start, end), text.rfind(" ", start, end))
            if split > start + CHUNK_CHARS // 2:
                end = split + 1
        result.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - OVERLAP, start + 1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ocr", action="store_true", help="OCR pages with no usable text layer")
    args = parser.parse_args()
    pdfs = sorted(KE.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {KE}")
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(INDEX)
    connection.execute("DROP TABLE IF EXISTS chunks")
    connection.execute("CREATE VIRTUAL TABLE chunks USING fts5(source, page UNINDEXED, text)")
    total_pages = total_chunks = 0
    with tempfile.TemporaryDirectory(prefix="textbook-ocr-") as temporary:
        temporary_path = Path(temporary)
        for pdf in pdfs:
            reader = PdfReader(str(pdf))
            if args.ocr:
                try:
                    reader = ocr_pdf(pdf, temporary_path)
                except (subprocess.SubprocessError, OSError):
                    pass
            for number, page in enumerate(reader.pages, 1):
                text = (page.extract_text() or "").strip()
                page_chunks = chunks(text)
                connection.executemany(
                    "INSERT INTO chunks(source, page, text) VALUES (?, ?, ?)",
                    [(pdf.name, number, item) for item in page_chunks],
                )
                total_pages += 1
                total_chunks += len(page_chunks)
                if total_pages % 25 == 0:
                    print(f"{total_pages} pages, {total_chunks} chunks", flush=True)
    connection.commit()
    connection.close()
    print(f"Indexed {total_pages} pages into {total_chunks} chunks: {INDEX}")


if __name__ == "__main__":
    main()
