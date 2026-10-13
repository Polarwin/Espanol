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
    monkeypatch.setattr(watcher, 'LEVELS', ('A2',))
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
    calls = Mock(side_effect=lambda *args, **kwargs: output.mkdir(exist_ok=True))
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
    monkeypatch.setattr(watcher, 'select_clip', Mock(return_value={
        'reading': 'Un texto.', 'start': 2, 'duration': 60, 'audio_kind': 'original'}))
    audio = Mock(side_effect=lambda directory: (directory / 'lectura.mp3').write_bytes(b'test MP3'))
    monkeypatch.setattr(watcher, 'ensure_audio', Mock(side_effect=AssertionError('Original clip must not use TTS')))
    monkeypatch.setattr(watcher, 'extract_audio', lambda video, directory, pack: audio(directory))
    pdf = Mock(side_effect=OSError('PDF unavailable'))
    monkeypatch.setattr(watcher, 'make_pdf', pdf)
    watcher.scan(ledger, root, output, now=10)
    watcher.scan(ledger, root, output, now=140)
    assert (output / '.news-abcdefghijk-a2.pending/ejercicio.json').exists()
    assert ledger.execute('SELECT status FROM videos').fetchone()[0] == 'pending'
    pdf.side_effect = lambda directory, browser: (directory / 'ejercicio.pdf').write_bytes(b'test PDF')
    watcher.scan(ledger, root, output, now=800)
    generator.assert_called_once()
    destination = watcher.find_export(output, 'abcdefghijk', 'A2')
    assert all((destination / name).is_file() for name in ['lectura.mp3', 'ejercicio.pdf', 'ejercicio.html', 'traduccion.html', 'respuestas.html', 'ejercicio.json', 'subtitulos.txt'])
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


def test_four_levels_resume_only_unfinished_level(setup, monkeypatch):
    root, output, db = setup
    monkeypatch.setattr(watcher, 'LEVELS', ('A1', 'A2', 'B1', 'B2'))
    add_video(root)
    seen = []
    def export(key, video, subtitle, root, output, level):
        seen.append(level)
        if level == 'A2' and seen.count('A2') == 1:
            raise ValueError('Retry this level')
    monkeypatch.setattr(watcher, 'publish_level', export)
    watcher.scan(db, root, output, now=10)
    watcher.scan(db, root, output, now=140)
    assert seen == ['A1', 'A2', 'B1', 'B2']
    assert {r[0] for r in db.execute('SELECT level FROM completed_levels')} == {'A1', 'B1', 'B2'}
    # No completed output exists on disk: cleanup must still not regenerate it.
    watcher.scan(db, root, output, now=800)
    assert seen == ['A1', 'A2', 'B1', 'B2', 'A2']
    assert db.execute('SELECT status FROM videos').fetchone()[0] == 'done'


def test_level_specific_private_delivery(db_session, client, auth_headers, monkeypatch):
    class BorrowSession:
        def __enter__(self): return db_session
        def __exit__(self, *args): pass
    monkeypatch.setattr(watcher, 'SessionLocal', BorrowSession)
    for level in ('A1', 'A2', 'B1', 'B2'):
        assert watcher.deliver('abcdefghijk', 'News', {'level': level}) == 1
    rows = db_session.scalars(select(ReadingPractice)).all()
    assert {r.level for r in rows} == {'A1', 'A2', 'B1', 'B2'}
    assert len({r.id for r in rows}) == 4
    rows[0].answers = {'0': 'Private answer'}
    db_session.commit()
    for level in ('A1', 'A2', 'B1', 'B2'):
        assert watcher.deliver('abcdefghijk', 'News', {'level': level}) == 0
    assert rows[0].answers == {'0': 'Private answer'}


def test_unsuitable_level_is_recorded_and_not_retried(setup, monkeypatch):
    root, output, db = setup
    add_video(root)
    exporter = Mock(side_effect=watcher.NoSuitableClip('No complete A2 excerpt'))
    monkeypatch.setattr(watcher, 'publish_level', exporter)
    watcher.scan(db, root, output, now=10)
    watcher.scan(db, root, output, now=140)
    assert db.execute('SELECT level FROM skipped_levels').fetchone()[0] == 'A2'
    assert db.execute('SELECT status FROM videos').fetchone()[0] == 'done'
    watcher.scan(db, root, output, now=900)
    exporter.assert_called_once()


def test_daily_limit_survives_cleanup_and_resumes_next_day(setup, monkeypatch):
    root, output, db = setup
    monkeypatch.setattr(watcher, 'LEVELS', ('A1', 'A2'))
    day = ['2026-10-13']
    monkeypatch.setattr(watcher, 'local_day', lambda timestamp=None: day[0])
    seen = []
    def export(key, video, subtitle, root, output, level):
        seen.append((key, level, day[0]))
        target = output / level / day[0] / f'news-{key}-{level.lower()}'
        target.mkdir(parents=True)
        (target / 'ejercicio.json').write_text(json.dumps({
            'level': level, 'video_key': key, 'published_date': day[0]}))
    monkeypatch.setattr(watcher, 'publish_level', export)
    for n in range(5):
        add_video(root, key=f'video{n:06d}')
    watcher.scan(db, root, output, now=10)
    for n in range(7):
        watcher.scan(db, root, output, now=140 + n)
    assert len(seen) == 6
    assert db.execute("SELECT COUNT(*) FROM videos WHERE status='pending'").fetchone()[0] == 2
    assert db.execute('SELECT SUM(attempts) FROM videos').fetchone()[0] == 0
    shutil.rmtree(output)
    with watcher.connect(root.parent / 'private/watcher.sqlite3') as reopened:
        watcher.scan(reopened, root, output, now=300)
        assert len(seen) == 6  # Removing files must not reset quota.
        day[0] = '2026-10-14'
        watcher.scan(reopened, root, output, now=90000)
        watcher.scan(reopened, root, output, now=90100)
        assert len(seen) == 10
        assert reopened.execute("SELECT COUNT(*) FROM videos WHERE status='pending'").fetchone()[0] == 0


def test_reconcile_recovers_publication_before_delivery_crash(setup):
    root, output, db = setup
    target = output / 'A2/2026-10-13/news-abcdefghijk-a2'
    target.mkdir(parents=True)
    (target / 'ejercicio.json').write_text(json.dumps({
        'level': 'A2', 'video_key': 'abcdefghijk', 'published_date': '2026-10-13'}))
    watcher.reconcile_publications(db, output)
    watcher.reconcile_publications(db, output)
    assert db.execute('SELECT COUNT(*) FROM publications').fetchone()[0] == 1
    assert watcher.find_export(output, 'abcdefghijk', 'A2') == target


def test_organize_preserves_audio_and_saves_original_metadata(tmp_path):
    from tools.organize_readings import organize
    root, backup = tmp_path / 'static', tmp_path / 'backup'
    old = root / 'news-abcdefghijk-a1'
    old.mkdir(parents=True)
    original = json.dumps({'level': 'A1', 'video_key': 'abcdefghijk',
                           'published_date': '2026-10-06', 'reading': 'Texto original.'})
    (old / 'ejercicio.json').write_text(original)
    (old / 'lectura.mp3').write_bytes(b'original MP3')
    assert len(organize(root, backup)) == 1
    assert old.exists() and not backup.exists()
    organize(root, backup, apply=True)
    new = root / 'A1/2026-10-06/news-abcdefghijk-a1'
    assert not old.exists()
    assert (new / 'lectura.mp3').read_bytes() == b'original MP3'
    assert (backup / 'news-abcdefghijk-a1.json').read_text() == original
    assert json.loads((new / 'ejercicio.json').read_text())['reading'] == 'Texto original.'
    assert organize(root, tmp_path / 'another-backup') == []
