"""Download safetensors/tokenizer files, preserving the revision on reinstall."""
import json
import sys
from pathlib import Path
from huggingface_hub import snapshot_download

root = Path(sys.argv[1]).resolve()
manifest = root / 'manifest.json'
model_id = 'flax-community/spanish-t5-small'
revision = json.loads(manifest.read_text())['revision'] if manifest.exists() else '37a7d1ce23d20605a705b098e9ef705d8a3e9b2a'
snapshot_download(repo_id=model_id, revision=revision, local_dir=root / 'model',
                  allow_patterns=['*.json', '*.model', '*.txt', '*.safetensors', 'README.md', 'LICENSE*'])
manifest.write_text(json.dumps({'model': model_id, 'revision': revision}, indent=2) + '\n')
print(f'Downloaded {model_id} at {revision}')
