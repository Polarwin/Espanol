"""Server-owned vocabulary progression and grading; no LLM grades."""
import random
from copy import deepcopy

from ..seed.a2_vocabulary_clues import BY_ID, CHAPTERS


def initial(language='es'):
    return {'chapter': 0, 'phase': 'learn', 'index': 0, 'correct': 0,
            'feedback': None, 'mistakes': {}, 'active': None, 'last_final': None,
            'language': language, 'seen': [], 'quiz_round': 0}


def current(state):
    active = state['active']
    if active:
        return None if active['done'] else active['words'][active['index']]
    if state['chapter'] >= len(CHAPTERS) or state['phase'] == 'summary':
        return None
    return CHAPTERS[state['chapter']]['words'][state['index']]


def options(state):
    word = BY_ID[current(state)]
    rng = random.Random(f"{word['id']}:{state['quiz_round']}:{state['active']['kind'] if state['active'] else 'chapter'}")
    # Other categories avoid ambiguous synonyms (e.g. vago/perezoso) and shared forms.
    pool = [item for item in BY_ID.values() if item['category'] != word['category']
            and item['text'] != word['text'] and item['translation'] != word['translation']]
    rng.shuffle(pool)
    choices = [word]
    for item in pool:
        if all(item['text'] != other['text'] and item['translation'] != other['translation'] for other in choices):
            choices.append(item)
        if len(choices) == 4:
            break
    rng.shuffle(choices)
    return choices


def view(state, revision):
    active = state['active']
    word_id = current(state)
    feedback = active['feedback'] if active else state['feedback']
    learning = not active and state['phase'] == 'learn'
    result = {
        'revision': revision, 'language': state['language'],
        'chapter': state['chapter'], 'chapters': len(CHAPTERS),
        'completed': min(len(CHAPTERS), state['chapter'] + (state['phase'] == 'summary')),
        'title': CHAPTERS[state['chapter']]['title'] if state['chapter'] < len(CHAPTERS) else 'Todo el vocabulario',
        'mode': active['kind'] if active else 'chapter',
        'phase': ('summary' if active['done'] else 'quiz') if active else state['phase'],
        'index': active['index'] if active else state['index'],
        'total': len(active['words']) if active else (len(CHAPTERS[state['chapter']]['words']) if state['chapter'] < len(CHAPTERS) else 0),
        'correct': active['correct'] if active else state['correct'],
        'seen': len(state['seen']), 'word_count': len(BY_ID),
        'mistakes': len(state['mistakes']), 'feedback': feedback,
        'final_unlocked': state['chapter'] >= len(CHAPTERS) and not state['mistakes'],
        'last_final': state['last_final'],
    }
    if word_id:
        word = BY_ID[word_id]
        if learning:
            result['word'] = word
        else:
            # Both question directions use stable authored clues, never generated definitions.
            reverse = (active['index'] if active else state['index']) % 2 == 1
            result['question'] = {
                'prompt': word['text'] if reverse else (word['clue'] if state['language'] == 'es' else word['translation']),
                'instruction': '¿Qué significa?' if reverse else '¿Qué palabra encaja?',
                'options': [{'id': item['id'], 'label': (item['clue'] if state['language'] == 'es' else item['translation']) if reverse else item['text']} for item in options(state)],
            }
    return result


def transition(original, action, choice=None):
    state = deepcopy(original)
    active = state['active']
    if action == 'language':
        if choice not in {'en', 'es'}:
            raise ValueError('Idioma desconocido.')
        state['language'] = choice
        return state
    if action == 'resume':
        if not active or not active['done']:
            raise ValueError('Termina esta ronda antes de continuar.')
        state['active'] = None
        return state
    if action in {'review', 'final'}:
        if active or state['feedback']:
            raise ValueError('Continúa con la actividad actual primero.')
        if action == 'review':
            if not state['mistakes']:
                raise ValueError('No tienes errores pendientes.')
            words = list(state['mistakes'])[:5]
            # Two separated recalls per item; missed items remain for another short round.
            words = words + words[1:] + words[:1]
        else:
            if state['chapter'] < len(CHAPTERS) or state['mistakes']:
                raise ValueError('Completa los capítulos y repasa los errores primero.')
            words = list(BY_ID)
        state['quiz_round'] += 1
        if action == 'final':
            random.Random(state['quiz_round']).shuffle(words)
        state['active'] = {'kind': action, 'words': words, 'index': 0, 'correct': 0, 'feedback': None, 'done': False}
        return state
    if action == 'next':
        if active or state['chapter'] >= len(CHAPTERS):
            raise ValueError('No hay una tarjeta para avanzar.')
        if state['phase'] == 'learn':
            word_id = current(state)
            if word_id not in state['seen']:
                state['seen'].append(word_id)
            state['index'] += 1
            if state['index'] == len(CHAPTERS[state['chapter']]['words']):
                state.update(phase='quiz', index=0, correct=0)
                state['quiz_round'] += 1
        elif state['phase'] == 'summary':
            state.update(chapter=state['chapter'] + 1, phase='learn', index=0, correct=0, feedback=None)
            if state['chapter'] == len(CHAPTERS):
                state['phase'] = 'complete'
        else:
            raise ValueError('Responde a la pregunta primero.')
        return state
    holder = active if active else state
    if action == 'answer':
        if not current(state) or holder['feedback'] or (not active and state['phase'] != 'quiz'):
            raise ValueError('Esta pregunta ya no está disponible.')
        if choice not in {item['id'] for item in options(state)}:
            raise ValueError('Elige una de las respuestas.')
        word_id = current(state)
        word = BY_ID[word_id]
        correct = choice == word_id
        holder['correct'] += int(correct)
        mistake = state['mistakes'].get(word_id)
        if not correct:
            state['mistakes'][word_id] = {'wrong': (mistake['wrong'] if mistake else 0) + 1, 'streak': 0}
        elif active and active['kind'] == 'review' and mistake:
            mistake['streak'] += 1
            if mistake['streak'] >= 2:
                del state['mistakes'][word_id]
        holder['feedback'] = {'correct': correct, 'word': word['text'], 'answer_id': word_id, 'chosen_id': choice,
                              'meaning': word['clue'] if state['language'] == 'es' else word['translation']}
        return state
    if action == 'continue':
        if not holder['feedback']:
            raise ValueError('Responde antes de continuar.')
        holder['feedback'] = None
        holder['index'] += 1
        total = len(active['words']) if active else len(CHAPTERS[state['chapter']]['words'])
        if holder['index'] == total:
            if active:
                active['done'] = True
                if active['kind'] == 'final':
                    state['last_final'] = {'correct': active['correct'], 'total': total}
            else:
                state['phase'] = 'summary'
        return state
    raise ValueError('Acción desconocida.')
