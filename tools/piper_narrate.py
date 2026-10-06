#!/usr/bin/env python3
"""CPU-only Spanish narration. Run using .local-tts/venv/bin/python.

Input: path to ejercicio.json. Output: lectura.mp3 and audio metadata/credits
beside that JSON. No model downloads or remote speech services at runtime.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import wave

ROOT = Path(__file__).resolve().parents[1]
VOICE = 'es_ES-sharvard-medium'
CREDITS = '''Synthetic Spanish narration: Piper, es_ES-sharvard-medium, speaker 0.
Piper software: https://github.com/OHF-Voice/piper1-gpl (GPL-3.0)
Voice model: https://huggingface.co/rhasspy/piper-voices/tree/main/es/es_ES/sharvard/medium
SHARVARD dataset: https://datashare.ed.ac.uk/handle/10283/574
Voice dataset license: Creative Commons Attribution 3.0
https://creativecommons.org/licenses/by/3.0/
Audio is synthesized from the adapted reading, not the original newsreader.
'''


def narrate(pack_path, force=False):
    pack_path = pack_path.resolve()
    directory = pack_path.parent
    pack = json.loads(pack_path.read_text(encoding='utf-8'))
    text = pack['reading'].strip()
    if not text or len(text) > 20000:
        raise ValueError('Expected a reading of 1–20000 characters')
    fingerprint = sha256((VOICE + ':speaker0:speed1.12:' + text).encode()).hexdigest()
    audio = directory / 'lectura.mp3'
    metadata = directory / 'audio.json'
    if not force and metadata.exists() and audio.exists() and audio.stat().st_size > 0:
        if json.loads(metadata.read_text())['text_hash'] == fingerprint:
            return

    # Restrict this short-lived process before importing ONNX Runtime. No
    # onnxruntime-gpu, CUDA, Torch, or background TTS server is required.
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['OMP_NUM_THREADS'] = '2'
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, set(sorted(os.sched_getaffinity(0))[:2]))
    os.nice(10)
    from piper import PiperVoice, SynthesisConfig
    from piper.config import PiperConfig
    import onnxruntime as ort
    started = time.monotonic()
    model = ROOT / '.local-tts/voices' / (VOICE + '.onnx')
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.add_session_config_entry('session.intra_op.allow_spinning', '0')
    voice = PiperVoice(
        config=PiperConfig.from_dict(json.loads(Path(str(model) + '.json').read_text())),
        session=ort.InferenceSession(str(model), sess_options=options, providers=['CPUExecutionProvider']))
    providers = voice.session.get_providers()
    if providers != ['CPUExecutionProvider']:
        raise RuntimeError(f'CPU-only provider required, got {providers}')
    config = SynthesisConfig(speaker_id=0, length_scale=1.12)
    with tempfile.TemporaryDirectory(prefix='.tts-', dir=directory) as temporary:
        temporary = Path(temporary)
        wav_path = temporary / 'lectura.wav'
        with wave.open(str(wav_path), 'wb') as wav:
            voice.synthesize_wav(text, wav, syn_config=config)
        with wave.open(str(wav_path)) as wav:
            duration = wav.getnframes() / wav.getframerate()
        mp3 = temporary / 'lectura.mp3'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(wav_path),
                        '-codec:a', 'libmp3lame', '-b:a', '96k', '-threads', '1', str(mp3)],
                       check=True, timeout=120, capture_output=True)
        if not mp3.stat().st_size:
            raise ValueError('Empty audio file')
        result = dict(text_hash=fingerprint, voice=VOICE, speaker=0, engine='Piper 1.8.0',
                      providers=providers, cpu_threads=2, duration_seconds=round(duration, 2),
                      generation_seconds=round(time.monotonic() - started, 2))
        (temporary / 'audio.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        (temporary / 'audio-credits.txt').write_text(CREDITS, encoding='utf-8')
        mp3.replace(audio)
        (temporary / 'audio.json').replace(metadata)
        (temporary / 'audio-credits.txt').replace(directory / 'audio-credits.txt')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack', type=Path)
    parser.add_argument('--force', action='store_true', help='Regenerate existing narration')
    args = parser.parse_args()
    narrate(args.pack, force=args.force)
