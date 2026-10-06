import json
import shutil
from unittest.mock import Mock

import pytest
from sqlalchemy import select

from backend.app.models import ReadingPractice
from tools import watch_news_readings as watcher


@pytest.fixture
def setup(tmp_path, monkeypatch):
    root, output = tmp_path / 'news', tmp_path / 'static'
    root.mkdir()
    monkeypatch.setattr(watcher.reading.settings, 'backup_dir', tmp_path / 'private')
    db = watcher.connect(tmp_path / 'private' / 'watcher.sqlite3')
    watcher.initialize(db, root, 0)
    yield root, output, db
    db.close()


def add_video(root, key='abcdefghijk', subtitles=True):
    video = root / f'Noticia [{key}].mp4'
    video.write_bytes(b'video fixture')
    if subtitles:
        video.with_suffix('.es.vtt').write_text('WEBVTT\n\n00:00:00.000 --> 00:01:00.000\n' + 'Una noticia para leer en español. ' * 20)
    return video


def test_baseline_and_late_subtitles(setup, monkeypatch):
    root, output, db = setup
    calls = Mock()
    monkeypatch.setattr(watcher, 'publish', calls)
    video = add_video(root, subtitles=False)
    watcher.scan(db, root, output, now=10)
    watcher.scan(db, root, output, now=500)
    calls.assert_not_called()
    add_video(root)
    watcher.scan(db, root, output, now=510)
    watcher.scan(db, root, output, now=600)
    calls.assert_not_called()
    watcher.scan(db, root, output, now=640)
    calls.assert_called_once()
    assert calls.call_args.args[1] == video
    watcher.scan(db, root, output, now=900)
    assert calls.call_count == 1


def test_initial_baseline_excludes_old_files(tmp_path):
    add_video(tmp_path)
    db = watcher.connect(tmp_path / 'state.sqlite3')
    watcher.initialize(db, tmp_path, 10)
    assert db.execute('SELECT status FROM videos').fetchone()['status'] == 'baseline'
    db.close()


def test_partial_and_changing_downloads(setup, monkeypatch):
    root, output, db = setup
    calls = Mock()
    monkeypatch.setattr(watcher, 'publish', calls)
    video = add_video(root)
    partial = video.with_suffix('.mp4.part')
    partial.touch()
    watcher.scan(db, root, output, now=10)
    watcher.scan(db, root, output, now=500)
    calls.assert_not_called()
    partial.unlink()
    watcher.scan(db, root, output, now=510)
    video.write_bytes(b'changed video fixture')
    watcher.scan(db, root, output, now=620)
    watcher.scan(db, root, output, now=700)
    calls.assert_not_called()
    watcher.scan(db, root, output, now=750)
    calls.assert_called_once()


def test_static_cleanup_restart_and_rename_do_not_regenerate(setup, monkeypatch):
    root, output, db = setup
    calls = Mock(side_effect=lambda *args: output.mkdir(exist_ok=True))
    monkeypatch.setattr(watcher, 'publish', calls)
    video = add_video(root)
    watcher.scan(db, root, output, now=10)
    watcher.scan(db, root, output, now=140)
    calls.assert_called_once()
    shutil.rmtree(output)  # Only this test's temporary generated-output fixture.
    video.rename(root / 'New title [abcdefghijk].mp4')
    with watcher.connect(root.parent / 'private' / 'watcher.sqlite3') as reopened:
        watcher.scan(reopened, root, output, now=1000)
    assert not output.exists() and calls.call_count == 1


def test_bounded_failure_and_busy_retry(setup, monkeypatch):
    root, output, db = setup
    add_video(root)
    calls = Mock(side_effect=BlockingIOError())
    monkeypatch.setattr(watcher, 'publish', calls)
    watcher.scan(db, root, output, now=10)
    watcher.scan(db, root, output, now=140)
    assert db.execute('SELECT attempts FROM videos').fetchone()[0] == 0
    calls.side_effect = ValueError('invalid model output')
    for now in (150, 800, 2100):
        watcher.scan(db, root, output, now=now)
    row = db.execute('SELECT * FROM videos').fetchone()
    assert row['status'] == 'failed' and row['attempts'] == 3
    watcher.scan(db, root, output, now=10000)
    assert calls.call_count == 4


def test_publish_pdf_resume_and_private_answers(setup, monkeypatch, db_session, client, auth_headers):
    root, output, ledger = setup
    video = add_video(root)
    class BorrowSession:
        def __enter__(self): return db_session
        def __exit__(self, *args): pass
    monkeypatch.setattr(watcher, 'SessionLocal', BorrowSession)
    generator = Mock(return_value=({'title': 'Noticia', 'reading': 'Un texto.', 'translation': 'A text.',
                                    'level': 'A2', 'questions': [{'question': '¿Qué?', 'suggested_answer': 'Una noticia.'}],
                                    'vocabulary': [{'term': 'texto', 'spanish': 'Una explicación.', 'english': 'An explanation.'}],
                                    'review_status': 'draft'}, []))
    monkeypatch.setattr(watcher.reading, 'generate_pack', generator)
    pdf = Mock(side_effect=OSError('PDF unavailable'))
    monkeypatch.setattr(watcher, 'make_pdf', pdf)
    watcher.scan(ledger, root, output, now=10)
    watcher.scan(ledger, root, output, now=140)
    assert (output / '.news-abcdefghijk-a2.pending/ejercicio.json').exists()
    assert ledger.execute('SELECT status FROM videos').fetchone()[0] == 'pending'
    pdf.side_effect = lambda directory, browser: (directory / 'ejercicio.pdf').write_bytes(b'test PDF')
    watcher.scan(ledger, root, output, now=800)
    generator.assert_called_once()
    destination = output / 'news-abcdefghijk-a2'
    assert all((destination / name).is_file() for name in ['ejercicio.pdf', 'ejercicio.html', 'traduccion.html', 'respuestas.html', 'ejercicio.json', 'subtitulos.txt'])
    job = db_session.scalar(select(ReadingPractice))
    job.answers = {'0': 'Mi respuesta'}
    db_session.commit()
    watcher.deliver('abcdefghijk', video.stem, json.loads((destination / 'ejercicio.json').read_text()))
    assert job.answers == {'0': 'Mi respuesta'}
    assert ledger.execute('SELECT status FROM videos').fetchone()[0] == 'done'


def test_reject_outside_symlinks(setup):
    root, output, db = setup
    outside = root.parent / 'outside.mp4'
    outside.write_bytes(b'outside')
    (root / 'escape.mp4').symlink_to(outside)
    assert watcher.videos(root) == {}
