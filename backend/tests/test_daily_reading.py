from sqlalchemy import select

from backend.app.models import ReadingPractice
from backend.app.services import reading
from tools import daily_reading


def test_daily_generation_cached_delivery_and_private_answers(db_session, client, auth_headers, monkeypatch, tmp_path):
    monkeypatch.setattr(reading.settings, 'backup_dir', tmp_path)
    class BorrowSession:
        def __enter__(self): return db_session
        def __exit__(self, *args): pass
    monkeypatch.setattr(daily_reading, 'SessionLocal', BorrowSession)
    calls = []
    monkeypatch.setattr(reading, 'select_source', lambda *args: (
        {'source': 'news', 'source_key': 'news-key', 'source_title': 'Noticia'},
        'Un texto', {'start': 0, 'duration': 180}))
    def generate(*args):
        calls.append(True)
        return {'questions': [{'question': '¿Qué?', 'suggested_answer': 'Una noticia'}],
                'review_status': 'draft', 'level': 'A2'}, []
    monkeypatch.setattr(reading, 'generate_pack', generate)
    assert daily_reading.run('2026-10-07') == 1
    job = db_session.scalar(select(ReadingPractice))
    job.answers = {'0': 'Mi respuesta privada'}
    db_session.commit()
    assert daily_reading.run('2026-10-07') == 0
    assert job.answers == {'0': 'Mi respuesta privada'}
    other = client.post('/api/auth/register', json={
        'email': 'daily-reader@example.com', 'password': 'secret123', 'display_name': 'Reader'}).json()
    assert daily_reading.run('2026-10-07') == 1
    assert len(calls) == 1
    headers = {'Authorization': 'Bearer ' + other['token']}
    jobs = client.get('/api/reading', headers=headers).json()
    assert len(jobs) == 1 and jobs[0]['status'] == 'ready'
    assert client.get('/api/reading/' + jobs[0]['id'], headers=headers).json()['answers'] == {}
    assert client.get('/api/reading/' + job.id, headers=headers).status_code == 404


def test_shared_generation_lock(tmp_path, monkeypatch):
    import pytest
    monkeypatch.setattr(reading.settings, 'backup_dir', tmp_path)
    with reading.generation_slot():
        with pytest.raises(BlockingIOError):
            with reading.generation_slot():
                raise AssertionError('Must not allow simultaneous generators')
    with reading.generation_slot():
        pass


def test_no_users_skips_model(db_session, monkeypatch, tmp_path):
    monkeypatch.setattr(reading.settings, 'backup_dir', tmp_path)
    class BorrowSession:
        def __enter__(self): return db_session
        def __exit__(self, *args): pass
    monkeypatch.setattr(daily_reading, 'SessionLocal', BorrowSession)
    assert daily_reading.run('2026-10-07') == 0
