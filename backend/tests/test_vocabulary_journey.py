from uuid import uuid4

import pytest

from backend.app.seed.a2_sample import WORDS
from backend.app.seed.a2_vocabulary_clues import BY_ID, CHAPTERS
from backend.app.services import vocabulary_journey as journey

ROOT = '/api/sample/a2-unit-1/journey'


def answer(state, correct=True):
    target = journey.current(state)
    choice = target if correct else next(item['id'] for item in journey.options(state) if item['id'] != target)
    return journey.transition(state, 'answer', choice)


def finish_chapter(state, miss_first=False):
    while state['phase'] == 'learn':
        state = journey.transition(state, 'next')
    while state['phase'] == 'quiz':
        state = answer(state, not (miss_first and state['index'] == 0))
        state = journey.transition(state, 'continue')
    return state


def test_glossary_coverage_and_small_chapters():
    ids = [word for chapter in CHAPTERS for word in chapter['words']]
    assert set(ids) == {word['id'] for word in WORDS}
    assert len(ids) == len(set(ids)) == 135
    assert all(1 <= len(chapter['words']) <= 5 for chapter in CHAPTERS)
    assert len(CHAPTERS) == 30
    assert all(BY_ID[word]['clue'] for word in ids)


def test_learning_before_quiz_and_no_answer_leak():
    state = journey.initial()
    with pytest.raises(ValueError):
        answer(state)
    with pytest.raises(ValueError):
        journey.transition(state, 'final')
    for _ in range(5):
        state = journey.transition(state, 'next')
    result = journey.view(state, 5)
    assert result['phase'] == 'quiz' and 'word' not in result
    assert 'answer' not in result['question'] and 'correct' not in result['question']
    assert len(result['question']['options']) == 4
    with pytest.raises(ValueError):
        journey.transition(state, 'next')
    with pytest.raises(ValueError):
        journey.transition(state, 'answer', 'not-an-option')
    state = answer(state)
    assert state['feedback']['correct'] and state['correct'] == 1
    with pytest.raises(ValueError):
        answer(state)


def test_review_requires_two_recalls_and_resumes_exact_chapter():
    state = finish_chapter(journey.initial(), miss_first=True)
    word_id = next(iter(state['mistakes']))
    assert state['correct'] == 4
    state = journey.transition(state, 'next')
    state = journey.transition(state, 'review')
    assert state['active']['words'] == [word_id, word_id]
    state = answer(state)
    assert word_id in state['mistakes'] and state['mistakes'][word_id]['streak'] == 1
    state = journey.transition(state, 'continue')
    state = answer(state, False)
    assert state['mistakes'][word_id]['streak'] == 0
    state = journey.transition(state, 'continue')
    state = journey.transition(state, 'resume')
    assert state['chapter'] == 1 and state['phase'] == 'learn' and state['index'] == 0
    state = journey.transition(state, 'review')
    for _ in range(2):
        state = journey.transition(answer(state), 'continue')
    assert not state['mistakes']
    assert state['active']['done']


def test_all_words_then_final_and_final_mistakes():
    state = journey.initial()
    for _ in CHAPTERS:
        state = journey.transition(finish_chapter(state), 'next')
    assert len(state['seen']) == 135
    assert journey.view(state, 0)['final_unlocked']
    state = journey.transition(state, 'final')
    assert len(set(state['active']['words'])) == 135
    first = journey.current(state)
    state = journey.transition(answer(state, False), 'continue')
    assert not journey.view(state, 0)['final_unlocked']
    while not state['active']['done']:
        state = journey.transition(answer(state), 'continue')
    assert state['last_final'] == {'correct': 134, 'total': 135}
    assert first in state['mistakes']
    state = journey.transition(state, 'resume')
    with pytest.raises(ValueError):
        journey.transition(state, 'final')


def test_all_quiz_options_unambiguous_and_bilingual():
    state = journey.initial()
    for _ in CHAPTERS:
        while state['phase'] == 'learn':
            state = journey.transition(state, 'next')
        while state['phase'] == 'quiz':
            for language in ['en', 'es']:
                state = journey.transition(state, 'language', language)
                question = journey.view(state, 0)['question']
                assert len({option['label'] for option in question['options']}) == 4
                assert journey.current(state) in {option['id'] for option in question['options']}
            state = journey.transition(answer(state), 'continue')
        state = journey.transition(state, 'next')


def test_api_persistence_idempotency_stale_actions_and_old_client(client, auth_headers):
    assert client.get(ROOT).status_code == 401
    start = client.get(ROOT, headers=auth_headers).json()
    command = {'action': 'next', 'revision': 0, 'request_id': str(uuid4())}
    result = client.post(ROOT, headers=auth_headers, json=command)
    assert result.status_code == 200, result.text
    assert result.json()['index'] == 1 and result.json()['revision'] == 1
    assert client.post(ROOT, headers=auth_headers, json=command).json() == result.json()
    assert client.post(ROOT, headers=auth_headers, json={**command, 'request_id': str(uuid4())}).status_code == 409
    assert client.get(ROOT, headers=auth_headers).json() == result.json()
    assert client.put('/api/sample/a2-unit-1/state', headers=auth_headers, json={
        'language': 'en', 'reviewed': ['0-0'], 'draft': 'Hola.', 'original': ''}).status_code == 200
    assert client.get(ROOT, headers=auth_headers).json() == result.json()
    token = client.post('/api/auth/register', json={
        'email': 'journey-other@example.com', 'password': 'secret123', 'display_name': 'Other', 'interests': []
    }).json()['token']
    other = {'Authorization': f'Bearer {token}'}
    assert client.get(ROOT, headers=other).json() == start
    assert client.post(ROOT, headers=auth_headers, json={
        'action': 'final', 'revision': 1, 'request_id': str(uuid4())}).status_code == 422
