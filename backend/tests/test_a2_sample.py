import httpx
import pytest

from backend.app.config import settings
from backend.app.seed.a2_sample import WORDS
from backend.app.services.ai import vocabulary, providers
from backend.app.services.ai import a2_grading
from backend.app.services.ai.contracts import Correction

ROOT = '/api/sample/a2-unit-1'


def test_grammar_marks_separate_from_corrections(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, 'ai_correction_local', True)
    monkeypatch.setattr(settings, 'ai_correction_adapter', 'barto')
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='unavailable', original=text))
    monkeypatch.setattr(a2_grading, 'grade', lambda text: {'status': 'graded', 'score': 1, 'total': 3, 'criteria': {}})
    body = {'text': 'Me gusta cocinar.', 'task': 'grammar'}
    result = client.post(ROOT + '/writing', headers=auth_headers, json=body).json()
    assert result['assessment']['score'] == 1
    assert result['status'] == 'unavailable'
    def fail(text):
        raise ValueError('busy')
    monkeypatch.setattr(a2_grading, 'grade', fail)
    result = client.post(ROOT + '/writing', headers=auth_headers, json=body).json()
    assert result['assessment'] == {'status': 'unavailable'}
    assert 'assessment' not in client.post(ROOT + '/writing', headers=auth_headers, json={'text': body['text']}).json()


def test_grader_requires_local_model_and_literal_evidence(monkeypatch):
    import json
    monkeypatch.setattr(settings, 'ai_enabled', True)
    monkeypatch.setattr(settings, 'ai_conversation_local', True)
    monkeypatch.setattr(settings, 'ai_conversation_url', 'http://localhost:8349/v1')
    evidence = 'Me gusta cocinar.'
    def post(self, url, **kwargs):
        assert kwargs['json']['model'] == vocabulary.MODEL
        return httpx.Response(200, request=httpx.Request('POST', url), json={'choices': [
            {'finish_reason': 'stop', 'message': {'content': json.dumps({
                name: {'met': name == 'preference', 'evidence': evidence if name == 'preference' else '', 'feedback': 'Una idea.'}
                for name in ['preference', 'difficulty', 'advice']})}}]})
    monkeypatch.setattr(httpx.Client, 'post', post)
    assert a2_grading.grade(evidence)['score'] == 1
    spaced = a2_grading.grade('Me gusta cocinar .')
    assert spaced['score'] == 1
    assert spaced['criteria']['preference']['evidence'] == 'Me gusta cocinar .'
    with pytest.raises(ValueError):
        a2_grading.grade('Hola.')
    monkeypatch.setattr(settings, 'ai_conversation_local', False)
    with pytest.raises(ValueError):
        a2_grading.grade(evidence)


def test_auth_glossary_and_account_isolation(client, auth_headers):
    assert client.get(ROOT).status_code == 401
    sample = client.get(ROOT, headers=auth_headers).json()
    assert len({word['category'] for word in sample['words']}) == 10
    assert len({word['id'] for word in WORDS}) == len(WORDS)
    assert sample['lesson_id'] is not None
    state = {'language': 'en', 'reviewed': ['0-0'], 'draft': 'Me gustan los idiomas.', 'original': 'Me gusta los idiomas.'}
    assert client.put(ROOT + '/state', headers=auth_headers, json=state).status_code == 200
    assert client.get(ROOT, headers=auth_headers).json()['state'] == state
    token = client.post('/api/auth/register', json={
        'email': 'other-sample@example.com', 'password': 'secret123', 'display_name': 'Other', 'interests': []
    }).json()['token']
    assert client.get(ROOT, headers={'Authorization': f'Bearer {token}'}).json()['state']['draft'] == ''
    assert client.put(ROOT + '/state', headers=auth_headers, json={**state, 'reviewed': ['unknown']}).status_code == 422


def test_definition_unknown_and_failure(client, auth_headers, monkeypatch):
    assert client.post(ROOT + '/words/not-a-word', headers=auth_headers).status_code == 404
    def fail(*args):
        raise ValueError('busy')
    monkeypatch.setattr(vocabulary, 'explain', fail)
    assert client.post(ROOT + '/words/0-0', headers=auth_headers).status_code == 503


def test_definition_forces_claro_model_caches_and_blocks_cloud(monkeypatch):
    vocabulary._generate.cache_clear()
    monkeypatch.setattr(settings, 'ai_enabled', True)
    monkeypatch.setattr(settings, 'ai_conversation_local', True)
    monkeypatch.setattr(settings, 'ai_conversation_url', 'http://127.0.0.1:8349/v1')
    calls = []
    def post(self, url, **kwargs):
        calls.append(kwargs['json'])
        return httpx.Response(200, request=httpx.Request('POST', url), json={
            'choices': [{'finish_reason': 'stop', 'message': {'content': '{"definition":"Persona que disfruta con otras personas.","example":"Ana es sociable y tiene muchos amigos."}'}}]})
    monkeypatch.setattr(httpx.Client, 'post', post)
    assert vocabulary.explain('sociable', 'sociable').example.startswith('Ana')
    vocabulary.explain('sociable', 'sociable')
    assert len(calls) == 1 and calls[0]['model'] == 'SmolLM3-Q4_K_M.gguf'
    monkeypatch.setattr(settings, 'ai_conversation_local', False)
    with pytest.raises(ValueError):
        vocabulary.explain('sociable', 'sociable')
    vocabulary._generate.cache_clear()


def test_truncated_definition_not_cached(monkeypatch):
    vocabulary._generate.cache_clear()
    def post(self, url, **kwargs):
        return httpx.Response(200, request=httpx.Request('POST', url), json={'choices': [{'finish_reason': 'length'}]})
    monkeypatch.setattr(httpx.Client, 'post', post)
    with pytest.raises(ValueError):
        vocabulary._generate('http://localhost/v1', 'correr', 'to run')
    assert vocabulary._generate.cache_info().currsize == 0


def test_writing_uses_correction_service_and_audio_boundaries(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, 'ai_correction_local', True)
    monkeypatch.setattr(settings, 'ai_correction_adapter', 'barto')
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(
        status='suggestions', original=text, suggested='Me gustan los libros.', processed=1))
    result = client.post(ROOT + '/writing', headers=auth_headers, json={'text': 'Me gusta los libros.'})
    assert result.json()['suggested'] == 'Me gustan los libros.'
    assert client.post(ROOT + '/writing', headers=auth_headers, json={'text': ' '}).status_code == 422
    assert client.post(ROOT + '/writing', headers=auth_headers, json={'text': 'a' * 2001}).status_code == 422
    assert client.get(ROOT + '/audio/1').status_code == 401
    assert client.get(ROOT + '/audio/3', headers=auth_headers).status_code == 404
    monkeypatch.setattr(settings, 'ai_correction_local', False)
    assert client.post(ROOT + '/writing', headers=auth_headers, json={'text': 'Hola.'}).status_code == 503
