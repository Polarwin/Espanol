#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd -- "$script_dir/../.." && pwd)"
model_home="${VAMOS_T5_HOME:-$project_dir/.local-models/spanish-t5}"
command -v uv >/dev/null || { echo 'Install uv (https://docs.astral.sh/uv/) before running this installer.' >&2; exit 1; }
mkdir -p "$model_home"
if [[ ! -x "$model_home/venv/bin/python" ]]; then
  uv venv --python 3.12 "$model_home/venv"
fi
uv pip install --python "$model_home/venv/bin/python" --index-url https://download.pytorch.org/whl/cpu 'torch==2.8.0'
uv pip install --python "$model_home/venv/bin/python" 'transformers==4.57.6' 'sentencepiece==0.2.1' 'safetensors>=0.4.3,<1'
"$model_home/venv/bin/python" "$script_dir/download.py" "$model_home"
uv pip freeze --python "$model_home/venv/bin/python" > "$model_home/installed-requirements.txt"
printf '\nInstalled Spanish-T5-small at %s\nRun: %s/test.sh\n' "$model_home" "$script_dir"
