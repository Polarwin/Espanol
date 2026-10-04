from pathlib import Path

from backend.app.services import textbook


def test_textbook_search_is_local_and_bounded(tmp_path, monkeypatch):
    index = tmp_path / 'textbook.sqlite3'
    import sqlite3
    with sqlite3.connect(index) as db:
        db.execute('CREATE VIRTUAL TABLE chunks USING fts5(source, page UNINDEXED, text)')
        db.execute("INSERT INTO chunks VALUES ('grammar.pdf', 12, 'A mí me gusta leer y practicar español.')")
    monkeypatch.setattr(textbook, 'INDEX_PATH', index)
    results = textbook.search('gustar practicar', limit=1)
    assert len(results) == 1
    assert results[0]['source'] == 'grammar.pdf'
    assert 'practicar español' in results[0]['text']
    assert len(textbook.context('gustar')) < 6000


def test_textbook_missing_index_is_safe(tmp_path, monkeypatch):
    monkeypatch.setattr(textbook, 'INDEX_PATH', Path(tmp_path) / 'missing.sqlite3')
    assert textbook.search('gramática') == []
    assert textbook.context('gramática') == ''
