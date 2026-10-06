import json
from types import SimpleNamespace
from unittest.mock import Mock
import wave

import pytest

from tools import subtitle_listening as listening
from tools import subtitle_reading as reading


def test_word_timestamps_survive_blank_lines_and_rolling_captions():
    raw = '''WEBVTT

00:00:01.000 --> 00:00:03.000
\x20
María<00:00:02.000><c> compra</c>

00:00:03.000 --> 00:00:03.010
María compra

00:00:03.010 --> 00:00:06.000
María compra
pan.<00:00:04.500><c> Juan</c><00:00:05.000><c> trabaja.</c>

00:00:06.000 --> 00:00:08.000
Y después
'''
    sentences = listening.subtitle_sentences(raw)
    assert [s['text'] for s in sentences] == ['María compra pan.', 'Juan trabaja.']
    assert sentences[0]['start'] == 1
    assert sentences[0]['end'] == sentences[1]['start'] == 4.5
    assert sentences[1]['end'] == 6


def test_srt_keeps_whole_cues_and_repeated_speech():
    raw = '''1
00:00:00,000 --> 00:00:04,000
Hola. Hola.

2
00:00:05,000 --> 00:00:09,000
Hola. Hola.

3
00:00:10,000 --> 00:00:12,000
Una frase sin terminar
'''
    sentences = listening.subtitle_sentences(raw)
    assert [s['text'] for s in sentences] == ['Hola. Hola.', 'Hola. Hola.']
    assert sentences[0]['start'] == 0
    assert sentences[1]['start'] == 5


def window():
    return [{'id': i, 'start': i * 15, 'end': (i + 1) * 15,
             'text': 'María compra pan en la tienda del barrio y habla con todos sus vecinos cada mañana.'}
            for i in range(4)]


def decision(accepted=True):
    return dict(accepted=accepted, first=0, last=3, reason='Adecuado.',
                vocabulary='Vocabulario cotidiano.', grammar='Presente.', completeness='Idea completa.')


def test_selection_preserves_exact_contiguous_words():
    result = listening.clip_from_selection(decision(), window(), 'A2')
    assert result['reading'] == ' '.join(s['text'] for s in window())
    assert (result['start'], result['duration']) == (0, 60)
    assert result['audio_kind'] == 'original'
    with pytest.raises(ValueError, match='existing'):
        listening.clip_from_selection(dict(decision(), last=20), window(), 'A2')
    rapid = [dict(s, start=s['start'] / 3, end=s['end'] / 3) for s in window()]
    with pytest.raises(ValueError, match='Too fast'):
        listening.clip_from_selection(decision(), rapid, 'A2')
    assert listening.clip_from_selection(decision(False), window(), 'A2') is None


def test_isolated_review_can_reject_candidate(monkeypatch):
    monkeypatch.setattr(listening, 'subtitle_sentences', lambda raw: window())
    monkeypatch.setattr(listening, 'candidate_windows', lambda sentences, **kwargs: [sentences])
    model = Mock(side_effect=[dict(decision(), range='0:3'), {'suitable': False, 'reason': 'Falta el antecedente.'}])
    monkeypatch.setattr(listening, 'chat', model)
    with pytest.raises(listening.NoSuitableClip):
        listening.select_clip('ignored', SimpleNamespace(level='A2'))
    assert model.call_count == 2


def test_original_pack_never_rewrites_or_summarizes_transcript(monkeypatch):
    original = listening.clip_from_selection(decision(), window(), 'A2')
    source = original['reading']
    calls = []
    def chat(args, instruction, data, validate, schema, **kwargs):
        calls.append(instruction)
        assert data == source
        if instruction.startswith('Traduce'):
            value = {'translation': 'A translation with all the original content. ' * 10}
        else:
            value = {'questions': [{'question': '¿Qué compra María?', 'suggested_answer': 'Pan.'}],
                     'vocabulary': [{'term': 'pan', 'spanish': 'Alimento que se prepara con harina.',
                                     'english': 'Food made from flour and water.'}]}
        validate(value)
        return value
    monkeypatch.setattr(reading, 'chat', chat)
    args = SimpleNamespace(level='A2', questions=1, vocabulary=1, model='test', context_size=8192)
    pack, audit = reading.generate_pack(source, args, original=original)
    assert pack['reading'] == source and pack['audio_kind'] == 'original'
    assert len(calls) == 2 and audit == []
    pack.update(source='Source video', audio_file='lectura.mp3')
    page = reading.render(pack)['escuchar.html']
    assert 'Audio original del vídeo.' in page
    assert 'Voz sintética' not in page


def test_ffmpeg_extracts_expected_duration_and_rejects_truncated_audio(tmp_path):
    import shutil
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        pytest.skip('ffmpeg required')
    source = tmp_path / 'source.wav'
    with wave.open(str(source), 'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(8000)
        wav.writeframes(b'\0\0' * 8000 * 25)
    pack = {'start': 2, 'duration': 15, 'reading': 'Una frase.', 'source': 'Test source'}
    listening.extract_audio(source, tmp_path, pack)
    metadata = json.loads((tmp_path / 'audio.json').read_text())
    assert abs(metadata['duration_seconds'] - 15) < .3
    assert metadata['audio_kind'] == 'original'
    digest = metadata['source_hash']
    with pytest.raises(ValueError, match='complete selected'):
        listening.extract_audio(source, tmp_path, dict(pack, start=20))
    assert json.loads((tmp_path / 'audio.json').read_text())['source_hash'] == digest


def test_a1_non_present_verbs_reject_the_generated_reading(monkeypatch):
    model = Mock(return_value={'present_only': False, 'reason': 'Compró is past tense.'})
    monkeypatch.setattr(reading, 'chat', model)
    with pytest.raises(ValueError, match='present indicative'):
        reading.validate_generated_reading({'title': 'Test', 'reading': 'María compró pan. ' * 40},
                                           None, SimpleNamespace(level='A1'))
    model.return_value = {'present_only': True, 'reason': 'Compra is present indicative.'}
    reading.validate_generated_reading({'title': 'Test', 'reading': 'María compra pan. ' * 40},
                                       None, SimpleNamespace(level='A1'))
