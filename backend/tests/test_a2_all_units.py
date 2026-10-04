import pytest
from sqlalchemy import select

from backend.app.models import Exercise, Lesson
from backend.app.services.ai import a2_checker, providers
from backend.app.services.ai.contracts import Correction

CASES = [
    (1, 'Me gusta los idiomas.', 'Me gustan los idiomas.'),
    (2, 'He escribido una carta.', 'He escrito una carta.'),
    (2, 'Hemos hacido los deberes.', 'Hemos hecho los deberes.'),
    (3, 'Aquí se puede hablas español.', 'Aquí se puede hablar español.'),
    (4, 'Estoy leiendo un libro.', 'Estoy leyendo un libro.'),
    (4, 'Está dormiendo.', 'Está durmiendo.'),
    (5, '¿Dónde fuistes ayer?', '¿Dónde fuiste ayer?'),
    (5, 'Ayer dijistes la verdad.', 'Ayer dijiste la verdad.'),
    (6, 'Suelo comes arroz.', 'Suelo comer arroz.'),
    (6, 'Bebo mucho agua.', 'Bebo mucha agua.'),
    (6, 'Compré demasiada libros.', 'Compré demasiados libros.'),
    (7, 'Tengo tan libros como tú.', 'Tengo tantos libros como tú.'),
    (7, 'Es tanto caro como ese.', 'Es tan caro como ese.'),
    (8, 'De niño eraba tímido.', 'De niño era tímido.'),
    (8, 'Le lo di ayer.', 'Se lo di ayer.'),
    (9, 'Me duele los pies.', 'Me duelen los pies.'),
    (9, 'Me duelen la cabeza.', 'Me duele la cabeza.'),
    (9, 'Vuelvo a estudias español.', 'Vuelvo a estudiar español.'),
    (10, 'Estas llaves son las míos.', 'Estas llaves son las mías.'),
    (10, 'Este libro es el tuya.', 'Este libro es el tuyo.'),
]


@pytest.mark.parametrize('unit,original,expected', CASES)
def test_units(unit, original, expected, monkeypatch):
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='no_suggestion', original=text, suggested=text))
    result = a2_checker.check(original)
    assert result['suggested'] == expected
    assert {issue['unit'] for issue in result['grammar_check']['issues']} == {unit}
    assert result['grammar_check']['coverage'] == 'a2'
    for issue in result['grammar_check']['issues']:
        assert original[issue['start']:issue['end']] == issue['original']


@pytest.mark.parametrize('text', [
    'He freído pescado. He frito pescado. He impreso las cartas. He imprimido las cartas.',
    'Ayer fui al cine. Hoy fui al cine. Hoy he ido al cine.',
    'Aquí se puede hablar. Se venden libros.',
    'Estoy leyendo. Está durmiendo. Estamos construyendo una casa.',
    'Fuiste a casa. Vos hablaste conmigo.',
    'Suelo comer arroz. Hay mucha agua. Tengo muy poco tiempo.',
    'Tengo tantos libros como tú. Es tan caro como ese.',
    'Antes era tímido. Veíamos la tele. Iba al colegio.',
    'Se lo di. Le dije que lo hiciera. Les di los libros.',
    'Me duelen los pies. Me duele la cabeza. Me duele la cabeza y el cuello.',
    'Estas llaves son las mías. Este libro es el tuyo. Lo bonito es compartir.',
    'Llegué en autobús. Llegué a Madrid. Llevo viviendo aquí dos años.',
    'Me gusta leer y escribir. Te recomiendo que practiques.',
    '¿Por qué estudias? Porque me gusta. Quiero saber por qué.',
])
def test_valid_variants(text):
    assert a2_checker.detect(text) == []


def test_every_unit_and_paragraph_fallback(monkeypatch):
    assert {case[0] for case in CASES} == set(range(1, 11))
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='unavailable', original=text))
    original = 'He escribido una carta. Estoy leiendo. Bebo mucho agua. Las llaves son las míos.'
    result = a2_checker.correction(original)
    assert result.suggested == 'He escrito una carta. Estoy leyendo. Bebo mucha agua. Las llaves son las mías.'
    assert result.status == 'partial'
    assert len(result.grammar_check['issues']) == 4


def test_model_cannot_undo_extended_rule(monkeypatch):
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='suggestions', original=text, suggested='He escrito una postal.'))
    # Unrelated edit may be retained.
    assert a2_checker.check('He escribido una carta.')['suggested'] == 'He escrito una postal.'
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='suggestions', original=text, suggested='He leído una carta.'))
    result = a2_checker.check('He escribido una carta.')
    assert result['suggested'] == 'He escrito una carta.'
    assert result['grammar_check']['model_status'] == 'rejected'
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='suggestions', original=text, suggested='He escritos una carta.'))
    assert a2_checker.check('He escribido una carta.')['suggested'] == 'He escrito una carta.'


def test_a2_exercise_response_preserves_checker_and_credit(client, auth_headers, db_session, monkeypatch):
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='no_suggestion', original=text, suggested=text))
    exercise = db_session.scalar(select(Exercise).join(Lesson).where(Lesson.cefr_level == 'A2', Exercise.type == 'writing'))
    response = client.post(f'/api/exercises/{exercise.id}/attempt', headers=auth_headers, json={'answer': 'He escribido una carta.'})
    assert response.status_code == 200
    result = response.json()
    assert result['score'] == 0.8
    assert result['correction']['suggested'] == 'He escrito una carta.'
    assert result['correction']['grammar_check']['issues'][0]['unit'] == 2


def test_typed_conversation_and_review(client, auth_headers, db_session, monkeypatch):
    from backend.app.models import User
    from backend.app.services.spaced_review import create_review_item
    from backend.app.routers import capabilities
    monkeypatch.setattr(providers, 'correct', lambda text: Correction(status='no_suggestion', original=text, suggested=text))
    monkeypatch.setattr(capabilities, 'ai_respond', lambda profile, history, text, fallback: (fallback, True))
    lesson = db_session.scalar(select(Lesson).where(Lesson.cefr_level == 'A2'))
    setup = client.get('/api/conversation/setup', params={'lesson_id': lesson.id}, headers=auth_headers).json()
    result = client.post('/api/conversation/respond', headers=auth_headers, data={
        'session_id': setup['session_id'], 'turn': 0, 'text': 'Estoy leiendo un libro.', 'request_id': 'all-a2-conversation'})
    assert result.status_code == 200, result.text
    assert result.json()['writing_correction']['grammar_check']['issues'][0]['unit'] == 4
    exercise = db_session.scalar(select(Exercise).where(Exercise.lesson_id == lesson.id, Exercise.type == 'writing'))
    user = db_session.scalar(select(User))
    item = create_review_item(db_session, user, 'writing', {'exercise_id': exercise.id, 'prompt': 'Escribe.'})
    db_session.commit()
    response = client.post(f'/api/review/{item.id}', headers=auth_headers, json={'answer': 'Me duele los pies.'})
    assert response.status_code == 200, response.text
    assert response.json()['correction']['grammar_check']['issues'][0]['unit'] == 9
