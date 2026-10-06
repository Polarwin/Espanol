from unittest.mock import Mock

import pytest
from backend.app.models import ReadingPractice
from backend.app.services import reading

select_source = reading.select_source


@pytest.fixture(autouse=True)
def isolated_worker(monkeypatch):
    reading.active.clear()
    monkeypatch.setattr(reading.executor, 'submit', Mock())
    monkeypatch.setattr(reading, 'select_source', lambda *a: (
        dict(source='library', source_key='test', source_title='Biblioteca'), 'Texto de prueba', {'start': 0, 'duration': 0}))
    yield
    reading.active.clear()


def test_auth_and_validation(client, auth_headers):
    assert client.get('/api/reading').status_code == 401
    assert client.post('/api/reading', headers=auth_headers, json={'source': '/etc/passwd'}).status_code == 422
    assert client.post('/api/reading', headers=auth_headers, json={'level': 'C3'}).status_code == 422


def test_create_deduplicates_and_recovers(client, auth_headers):
    first = client.post('/api/reading', headers=auth_headers, json={}).json()
    assert first['status'] == 'queued'
    second = client.post('/api/reading', headers=auth_headers, json={}).json()
    assert first['id'] == second['id']
    assert reading.executor.submit.call_count == 1
    assert 'source_key' not in first
    assert len(client.get('/api/reading', headers=auth_headers).json()) == 1
    reading.active.clear()
    recovered = client.get('/api/reading/' + first['id'], headers=auth_headers).json()
    assert recovered['status'] == 'failed'
    assert 'reiniciar' in recovered['error']


def test_answers_and_ownership(client, auth_headers, db_session):
    first = client.post('/api/reading', headers=auth_headers, json={}).json()
    path = '/api/reading/' + first['id']
    assert client.put(path + '/answers', headers=auth_headers, json={'answers': {'0': 'Hola'}}).status_code == 409
    job = db_session.get(ReadingPractice, first['id'])
    job.status, job.pack = 'ready', {'questions': [{'question': '¿Qué?', 'suggested_answer': 'Algo'}]}
    db_session.commit()
    assert client.put(path + '/answers', headers=auth_headers, json={'answers': {'0': 'Mi respuesta'}}).status_code == 200
    assert client.get(path, headers=auth_headers).json()['answers'] == {'0': 'Mi respuesta'}
    assert client.put(path + '/answers', headers=auth_headers, json={'answers': {'5': 'No'}}).status_code == 422
    assert client.put(path + '/answers', headers=auth_headers, json={'answers': {'0': 'x' * 4001}}).status_code == 422
    other = client.post('/api/auth/register', json={'email': 'reader@example.com', 'password': 'secret123', 'display_name': 'Reader'}).json()
    headers = {'Authorization': 'Bearer ' + other['token']}
    assert client.get(path, headers=headers).status_code == 404
    assert client.put(path + '/answers', headers=headers, json={'answers': {}}).status_code == 404
    assert client.get('/api/reading', headers=headers).json() == []


def test_busy_and_missing(client, auth_headers, monkeypatch):
    reading.active.add('other-user')
    assert client.post('/api/reading', headers=auth_headers, json={}).status_code == 409
    reading.active.clear()
    def missing(*args):
        raise ValueError('missing')
    monkeypatch.setattr(reading, 'select_source', missing)
    assert client.post('/api/reading', headers=auth_headers, json={}).status_code == 422


def test_subtitle_dedup_and_symlink_escape(tmp_path):
    root = tmp_path / 'news'
    root.mkdir()
    for name in ['clip.es.vtt', 'clip.es-orig.vtt', 'clip.es.srt', 'clip.en.vtt']:
        (root / name).touch()
    outside = tmp_path / 'outside.vtt'
    outside.touch()
    (root / 'escape.vtt').symlink_to(outside)
    assert [p.name for p in reading.subtitle_candidates(root)] == ['clip.es-orig.vtt']


def test_real_source_selection(db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(reading.settings, 'watch_dir', tmp_path)
    monkeypatch.setattr(reading.settings, 'reading_news_dir', tmp_path)
    monkeypatch.setattr(reading.textbook, 'available', lambda: False)
    source, text, excerpt = select_source(db_session, 'library', 'A2', set())
    assert source['source'] == 'library' and len(text.split()) >= 30
    assert excerpt['duration'] == 0
    with pytest.raises(ValueError):
        select_source(db_session, 'news', 'A2', set())
    (tmp_path / 'noticias.es.vtt').write_text('WEBVTT\n\n00:00:00.000 --> 00:01:00.000\n' + 'Una noticia para leer en español. ' * 20)
    source, text, excerpt = select_source(db_session, 'news', 'A2', set())
    assert source['source'] == 'news' and source['source_title'] == 'noticias'
    assert str(tmp_path) not in str(source)
    assert len(text.split()) >= 30


def test_worker_persists_and_releases(client, auth_headers, db_session, monkeypatch):
    first = client.post('/api/reading', headers=auth_headers, json={}).json()
    class BorrowSession:
        def __enter__(self): return db_session
        def __exit__(self, *args): pass
    monkeypatch.setattr(reading, 'SessionLocal', BorrowSession)
    def generate(text, args, progress):
        progress('Preparando preguntas')
        return {'questions': [], 'review_status': 'draft'}, []
    monkeypatch.setattr(reading, 'generate_pack', generate)
    reading.generate(first['id'], 'Text', {'start': 0, 'duration': 0})
    assert not reading.active
    assert client.get('/api/reading/' + first['id'], headers=auth_headers).json()['status'] == 'ready'
    def failure(*args): raise ValueError('private model text')
    monkeypatch.setattr(reading, 'generate_pack', failure)
    reading.active.add(first['id'])
    reading.generate(first['id'], 'Text', {})
    response = client.get('/api/reading/' + first['id'], headers=auth_headers).json()
    assert response['status'] == 'failed'
    assert 'private' not in response['error']
    assert not reading.active
