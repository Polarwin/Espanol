import httpx
import pytest
from sqlalchemy import select

from backend.app.config import Settings, settings
from backend.app.models import ConversationSession, Exercise, SkillProgress
from backend.app.services.ai import providers
from backend.app.services.ai.contracts import Correction


def mock_http(monkeypatch, handler):
    real = httpx.Client
    monkeypatch.setattr(providers.httpx, 'Client', lambda **kwargs: real(transport=httpx.MockTransport(handler), **kwargs))


def test_barto_validation_and_timeout(monkeypatch):
    monkeypatch.setattr(settings, 'ai_enabled', True)
    mock_http(monkeypatch, lambda req: httpx.Response(200, json={'status':'suggestions', 'original':'Soy veinte años.', 'suggested':'Tengo veinte años.', 'processed':1, 'skipped':0}))
    assert providers.correct('Soy veinte años.').suggested == 'Tengo veinte años.'
    assert providers.correct('Me llamo Ana.').status == 'unavailable'  # mismatched original


def test_barto_failure_is_not_no_error(monkeypatch):
    monkeypatch.setattr(settings, 'ai_enabled', True)
    mock_http(monkeypatch, lambda req: httpx.Response(429))
    assert providers.correct('Soy veinte años.').status == 'unavailable'


def test_partial_and_numbers(monkeypatch):
    monkeypatch.setattr(settings, 'ai_enabled', True)
    mock_http(monkeypatch, lambda req: httpx.Response(200, json={'status':'partial', 'original':'Tengo 20 años.', 'suggested':'Tengo 30 años.', 'processed':1, 'skipped':1}))
    assert providers.correct('Tengo 20 años.').status == 'unavailable'


def test_cloud_disabled_and_loopback_only():
    with pytest.raises(ValueError):
        Settings(_env_file=None, ai_enabled=True, ai_conversation_local=False)
    with pytest.raises(ValueError):
        Settings(_env_file=None, ai_enabled=True, ai_conversation_url='http://example.com/v1')


@pytest.mark.parametrize('adapter,response', [
    ('openai_compatible', {'choices':[{'finish_reason':'stop','message':{'content':'Hola.'}}]}),
    ('openai_responses', {'status':'completed','output':[{'content':[{'type':'output_text','text':'Hola.'}]}]}),
    ('anthropic', {'stop_reason':'end_turn','content':[{'type':'text','text':'Hola.'}]}),
])
def test_adapter_contracts(monkeypatch, adapter, response):
    monkeypatch.setattr(settings, 'ai_conversation_adapter', adapter)
    mock_http(monkeypatch, lambda req: httpx.Response(200, json=response))
    assert providers.chat([{'role':'system','content':'Habla español.'},{'role':'user','content':'Hola'}]) == 'Hola.'


def test_truncation_falls_back(monkeypatch):
    monkeypatch.setattr(settings, 'ai_enabled', True)
    mock_http(monkeypatch, lambda req: httpx.Response(200, json={'choices':[{'finish_reason':'length','message':{'content':'partial'}}]}))
    profile = dict(scene='Un café', cefr_level='A1', goal='Pedir', vocabulary=[])
    assert providers.respond(profile, [], 'Hola', '¿Qué quieres?') == ('¿Qué quieres?', True)


def test_conversation_history_and_retry(client, auth_headers, db_session, monkeypatch):
    from backend.app.routers import capabilities
    histories = []
    def respond(profile, history, text, fallback):
        histories.append(history)
        return '¿A qué hora?', False
    monkeypatch.setattr(capabilities, 'ai_respond', respond)
    setup = client.get('/api/conversation/setup', headers=auth_headers).json()
    data = {'session_id':setup['session_id'], 'turn':0, 'text':'Quiero ir a Valencia.', 'request_id':'one'}
    first = client.post('/api/conversation/respond', data=data, headers=auth_headers)
    assert first.status_code == 200, first.text
    progress = [(p.skill, p.score) for p in db_session.scalars(select(SkillProgress)).all()]
    repeated = client.post('/api/conversation/respond', data=data, headers=auth_headers)
    assert repeated.json() == first.json()
    assert len(histories) == 1
    assert progress == [(p.skill, p.score) for p in db_session.scalars(select(SkillProgress)).all()]
    data.update(turn=1, text='Mañana a las nueve.', request_id='two')
    assert client.post('/api/conversation/respond', data=data, headers=auth_headers).status_code == 200
    assert histories[1][-2:] == [{'role':'user','content':'Quiero ir a Valencia.'},{'role':'assistant','content':'¿A qué hora?'}]
    data.update(request_id='three')
    assert client.post('/api/conversation/respond', data=data, headers=auth_headers).status_code == 409
    session = db_session.get(ConversationSession, setup['session_id'])
    session.user_id = 999
    db_session.commit()
    assert client.post('/api/conversation/respond', data=data, headers=auth_headers).status_code == 404


def test_writing_suggestion_does_not_change_credit(client, auth_headers, db_session, monkeypatch):
    from backend.app.services import scoring
    monkeypatch.setattr(scoring, 'suggest_correction', lambda text: Correction(status='suggestions', original=text, suggested='Tengo veinte años.', processed=1))
    exercise = db_session.scalar(select(Exercise).where(Exercise.type == 'writing'))
    result = client.post(f'/api/exercises/{exercise.id}/attempt', json={'answer':'Soy veinte años.'}, headers=auth_headers)
    assert result.status_code == 200, result.text
    assert result.json()['score'] == 0.8
    assert result.json()['correction']['suggested'] == 'Tengo veinte años.'
    assert 'crédito' in result.json()['feedback']


def test_edit_filter_preserves_names_and_numbers():
    from backend.app.services.ai.text_safety import acceptable_edit
    assert acceptable_edit('Soy veinte años.', 'Tengo veinte años.')
    assert not acceptable_edit('Hola, Sr. García.', 'Hola, Sr. García Hidalgo.')
    assert not acceptable_edit('Tengo 20 años.', 'Tengo 30 años.')


def test_correction_partial_response(monkeypatch):
    monkeypatch.setattr(settings, 'ai_enabled', True)
    mock_http(monkeypatch, lambda req: httpx.Response(200, json={'status':'partial','original':'Hola.','suggested':'Hola.','processed':0,'skipped':1}))
    result = providers.correct('Hola.')
    assert result.status == 'partial' and result.skipped == 1


@pytest.mark.skipif(__import__('os').environ.get('VAMOS_TEST_LIVE_AI') != '1', reason='Explicit local model smoke test')
def test_live_models_through_app(client, auth_headers, db_session, monkeypatch):
    monkeypatch.setattr(settings, 'ai_enabled', True)
    setup = client.get('/api/conversation/setup', headers=auth_headers).json()
    data = {'session_id': setup['session_id'], 'turn':0, 'request_id':'live-one', 'text':'Me gusta cocinar y quiero aprender español.'}
    response = client.post('/api/conversation/respond', data=data, headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json()['fallback'] is False, response.text
    assert response.json()['reply'] and response.json()['writing_correction']['status'] != 'unavailable'
    repeated = client.post('/api/conversation/respond', data=data, headers=auth_headers)
    assert repeated.json() == response.json()
    data.update(turn=1, request_id='live-two', text='Prefiero cocinar paella. ¿Qué te gusta cocinar?')
    response = client.post('/api/conversation/respond', data=data, headers=auth_headers)
    assert response.status_code == 200 and response.json()['fallback'] is False, response.text
    exercise = db_session.scalar(select(Exercise).where(Exercise.type == 'writing'))
    response = client.post(f'/api/exercises/{exercise.id}/attempt', headers=auth_headers, json={'answer':'Soy veinte años y me gusta las películas españolas.'})
    assert response.status_code == 200, response.text
    assert response.json()['correction']['suggested'] == 'Tengo veinte años y me gustan las películas españolas.'
