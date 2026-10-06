"""Bridge the app's Python environment to the isolated CPU-only Piper runtime."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def ensure_audio(directory):
    python = ROOT / '.local-tts/venv/bin/python'
    if not python.is_file():
        raise RuntimeError('Run ./bin/python tools/install_piper.py first')
    subprocess.run([str(python), str(ROOT / 'tools/piper_narrate.py'),
                    str(Path(directory).resolve() / 'ejercicio.json')],
                   check=True, timeout=600)
