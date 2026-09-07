"""Download safetensors/tokenizer files, preserving the revision on reinstall."""
import json
import sys
from pathlib import Path
from huggingface_hub import snapshot_download

root = Path(sys.argv[1]).resolve()
manifest = root / 'manifest.json'
model_id = 'SkitCon/gec-spanish-BARTO-SYNTHETIC'
revision = json.loads(manifest.read_text())['revision'] if manifest.exists() else '686fdc629800270c0ff3d342e98536efb9b3aaa2'
snapshot_download(repo_id=model_id, revision=revision, local_dir=root / 'model',
                  allow_patterns=['*.json', '*.model', '*.txt', '*.safetensors', 'README.md', 'LICENSE*'])
manifest.write_text(json.dumps({'model': model_id, 'revision': revision}, indent=2) + '\n')
print(f'Downloaded {model_id} at {revision}')
