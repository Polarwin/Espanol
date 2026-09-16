from uuid import uuid4

import pytest

from backend.app.seed.a2_sample import WORDS
from backend.app.seed.a2_vocabulary_clues import BY_ID, CHAPTERS
from backend.app.services import vocabulary_journey as journey
from backend.alembic.versions.j6b1c9e5f7a3_merge_short_vocabulary_chapters import OLD, remap

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
    assert all(3 <= len(chapter['words']) <= 7 for chapter in CHAPTERS)
    assert len(CHAPTERS) == 27
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


@pytest.mark.parametrize('old_index', range(30))
@pytest.mark.parametrize('phase', ['learn', 'quiz', 'summary'])
def test_merge_migration_preserves_progress_and_teaches_remaining_words(old_index, phase):
    original = journey.initial('en')
    original.update(chapter=old_index, phase=phase,
                    index=len(OLD[old_index]) if phase == 'summary' else len(OLD[old_index]) - 1,
                    correct=2 if phase != 'learn' else 0,
                    seen=[word for words in OLD[:old_index] for word in words],
                    mistakes={'5-0': {'wrong': 2, 'streak': 1}},
                    last_final={'correct': 120, 'total': 135})
    if phase != 'learn':
        original['seen'] += OLD[old_index]
    else:
        original['seen'] += OLD[old_index][:-1]
    state = remap(original)
    assert state['mistakes'] == original['mistakes']
    assert state['last_final'] == original['last_final']
    assert state['correct'] == original['correct']
    assert state['seen'] == original['seen']
    if phase != 'summary':
        assert journey.current(state) == OLD[old_index][original['index']]
    while state['phase'] != 'complete':
        state = journey.transition(finish_chapter(state), 'next')
    assert set(state['seen']) == set(BY_ID)


def test_merge_migration_keeps_active_review_final_and_pending_feedback():
    original = journey.initial()
    original.update(chapter=10, phase='quiz', index=1,
                    feedback={'correct': True, 'word': 'ver series'},
                    active={'kind': 'review', 'words': ['5-0', '5-0'], 'index': 1,
                            'correct': 1, 'feedback': None, 'done': False})
    state = remap(original)
    assert state['active'] == original['active']
    assert state['feedback'] == original['feedback']
    assert journey.current(state) == '5-0'
    state['active'] = None
    assert journey.current(state) == '2-21'
    assert journey.view(state, 5)['total'] == 2
    original.update(chapter=30, phase='complete')
    state = remap(original)
    assert state['chapter'] == 27 and state['active'] == original['active']


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
