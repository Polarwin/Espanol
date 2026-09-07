# Spanish-T5-small local experiment

Downloads `flax-community/spanish-t5-small` and installs an isolated CPU inference environment. Requires `uv`; the installer uses Python 3.12 (uv can download it when missing). No sudo is needed. It does not modify the app's Python environment or the existing LLM gateway.

From the project root:

```bash
./tools/spanish-t5/install.sh
./tools/spanish-t5/test.sh
./tools/spanish-t5/test.sh --text 'Corrige la gramática: Soy veinte años.'
./tools/spanish-t5/test.sh --text 'Tengo <extra_id_0> años.'
./tools/spanish-t5/test.sh --output /tmp/spanish-t5-results.json
```

Default storage is `.local-models/spanish-t5/`, ignored by Git. Set `VAMOS_T5_HOME` to an absolute alternative directory for both scripts if needed. Dependencies and model files require network access during installation; testing runs offline. The installer pins the model revision to `37a7d1ce23d20605a705b098e9ef705d8a3e9b2a`, reuses it on reinstall, and downloads safetensors rather than pickle weights. Runtime package versions are recorded in `installed-requirements.txt`; top-level packages are pinned in the installer, while transitive dependencies are resolved at install time.

The model is pretrained Spanish T5, not a grammar-correction fine-tune. The `Corrige la gramática:` text is an experimental prompt, not a documented task prefix. Masked-span prompts are included for comparison. The test reports raw output too, so T5 sentinel tokens are visible. Greedy decoding, four CPU threads and a 64-token generation limit are defaults. Use `--threads` and `--max-new-tokens` to change those settings.

## Initial local result, 2026-09-07

Six prompts tested on the i5-10210U. Model/tokenizer loading took 0.38 seconds after Python imports; generation took 0.07–0.90 seconds per example. Process startup/import time is additional. Correction prompts produced fragmented text and sentinel tokens, not useful corrected sentences. The dialogue prompt repeated text and reached the output limit. These results do not support using the pretrained checkpoint directly in the app. A Spanish grammatical-correction fine-tune is needed before further product evaluation.

Verbatim results: [results.json](../../design/evaluations/spanish-t5-2026-09-07/results.json).

Model source and license: https://huggingface.co/flax-community/spanish-t5-small (MIT).
