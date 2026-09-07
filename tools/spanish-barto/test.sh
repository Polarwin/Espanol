#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd -- "$script_dir/../.." && pwd)"
model_home="${VAMOS_BARTO_HOME:-$project_dir/.local-models/spanish-barto}"
[[ -x "$model_home/venv/bin/python" ]] || { echo "Run $script_dir/install.sh first." >&2; exit 1; }
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
exec "$model_home/venv/bin/python" "$script_dir/try_model.py" --model-home "$model_home" "$@"
