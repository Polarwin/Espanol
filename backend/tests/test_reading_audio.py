from hashlib import sha256
import json
from unittest.mock import Mock

import pytest

from tools import piper_narrate, reading_audio


def test_cached_narration_does_not_load_model(tmp_path, monkeypatch):
    pack = tmp_path / 'ejercicio.json'
    pack.write_text(json.dumps({'reading': 'Hola, vamos a leer.'}))
    digest = sha256((piper_narrate.VOICE + ':speaker0:speed1.12:Hola, vamos a leer.').encode()).hexdigest()
    (tmp_path / 'audio.json').write_text(json.dumps({'text_hash': digest}))
    (tmp_path / 'lectura.mp3').write_bytes(b'cached audio')
    monkeypatch.setattr(piper_narrate.os, 'nice', Mock(side_effect=AssertionError('Must use cache')))
    piper_narrate.narrate(pack)
    assert (tmp_path / 'lectura.mp3').read_bytes() == b'cached audio'


def test_rejects_empty_reading_before_model_load(tmp_path):
    pack = tmp_path / 'ejercicio.json'
    pack.write_text(json.dumps({'reading': '   '}))
    with pytest.raises(ValueError):
        piper_narrate.narrate(pack)


def test_isolated_runtime_and_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr(reading_audio, 'ROOT', tmp_path)
    python = tmp_path / '.local-tts/venv/bin/python'
    python.parent.mkdir(parents=True)
    python.touch()
    run = Mock()
    monkeypatch.setattr(reading_audio.subprocess, 'run', run)
    reading_audio.ensure_audio(tmp_path / 'static/pack')
    arguments = run.call_args.args[0]
    assert arguments[0] == str(python)
    assert arguments[-1] == str(tmp_path / 'static/pack/ejercicio.json')
    assert run.call_args.kwargs == {'check': True, 'timeout': 600}


def test_missing_install_does_not_fall_back_to_cloud(tmp_path, monkeypatch):
    monkeypatch.setattr(reading_audio, 'ROOT', tmp_path)
    with pytest.raises(RuntimeError, match='install_piper'):
        reading_audio.ensure_audio(tmp_path)
