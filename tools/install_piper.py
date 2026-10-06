#!/usr/bin/env python3
"""One-command local CPU-only TTS setup: ./bin/python tools/install_piper.py."""
from pathlib import Path
import shutil
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
VOICE = 'es_ES-sharvard-medium'
BASE = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/'


def main():
    uv = shutil.which('uv')
    if not uv or not shutil.which('ffmpeg'):
        raise SystemExit('Install uv and ffmpeg first.')
    directory = ROOT / '.local-tts'
    python = directory / 'venv/bin/python'
    directory.mkdir(exist_ok=True)
    if not python.exists():
        subprocess.run([uv, 'venv', '--python', '3.12', str(directory / 'venv')], check=True)
    subprocess.run([uv, 'pip', 'install', '--python', str(python), 'piper-tts==1.8.0'], check=True)
    voices = directory / 'voices'
    voices.mkdir(exist_ok=True)
    for name in (VOICE + '.onnx', VOICE + '.onnx.json', 'MODEL_CARD'):
        destination = voices / name
        if destination.exists():
            continue
        temporary = destination.with_suffix(destination.suffix + '.download')
        with urlopen(BASE + name, timeout=120) as response, temporary.open('wb') as output:
            shutil.copyfileobj(response, output)
        temporary.replace(destination)
    print('Piper installed in .local-tts/ with Spanish (Spain) voice. Runtime is CPU-only; no CUDA package installed.')


if __name__ == '__main__':
    main()
