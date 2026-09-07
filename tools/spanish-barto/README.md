# Spanish BARTO sentence correction

Local experiment with `SkitCon/gec-spanish-BARTO-SYNTHETIC`, revision `686fdc629800270c0ff3d342e98536efb9b3aaa2`. This is a correction fine-tune with 139,419,648 parameters. Model source: https://huggingface.co/SkitCon/gec-spanish-BARTO-SYNTHETIC

## Run

From the project root:

```bash
./tools/spanish-barto/install.sh
./tools/spanish-barto/test.sh --text 'Soy veinte años y me gusta las películas españolas.' --runs 1
./tools/spanish-barto/test.sh --output /tmp/barto-results.json
```

Requires uv. The installer creates a Python 3.12 CPU environment and downloads safetensors plus tokenizer files into the git-ignored `.local-models/spanish-barto/`. Reinstallation reuses the pinned revision and cached packages. Set `VAMOS_BARTO_HOME` to an absolute alternative directory for both scripts if needed. It records installed dependency versions; transitive dependencies are resolved at installation time.

Testing runs offline, using four CPU threads by default. Supply one sentence with no instruction prefix. Inputs over 128 tokens are rejected rather than silently truncated. The test uses the checkpoint's generation settings, deterministic decoding, and an explicit 128-new-token limit; the resolved settings are saved with the results. The default suite contains 18 unique sentences, each run twice. This runs independently of the app and LLM gateway.

## Initial evaluation — 2026-09-07

On the i5-10210U, model/tokenizer loading took 0.514 seconds after Python imports. Warm sentence correction median was 0.391 seconds across 35 requests (the first request excluded); the overall range was 0.261–1.124 seconds. Process startup/import time is additional. No GPU was used.

Manual review found 9 of 10 intended corrections successful, with identical output on both runs. This comprises eight of nine clearly erroneous inputs plus the separate past-tense diagnostic. “Ayer voy…” can also occur as narrative present, so its conversion is an intended exercise correction rather than a context-free grammatical requirement. Two inputs came from the model card and therefore are smoke tests, not independent held-out evidence.

Successful examples:

- “Soy veinte años” → “Tengo veinte años”
- “Me gusta las películas españolas” → “Me gustan las películas españolas”
- The combined age/agreement sentence was fully corrected.
- “Ayer voy al mercado y compro dos manzanas” → “Ayer fui al mercado y compré dos manzanas”
- “Si habría sabido…” → “Si hubiera sabido…”
- Gender agreement, subject/verb agreement and “Estoy de acuerdo” were corrected.
- “Yo va al tienda” → “Voy a la tienda”: acceptable despite differing from the exact reference by omission of the optional pronoun.

Missed error: “Espero que tú ganas” was unchanged in both runs. Expected: “Espero que tú ganes.”

All eight correct control sentences were preserved exactly, including “Depende de que tengamos tiempo,” “Ojalá hubiera más trenes los domingos,” and regional “Hoy fui … frutillas.” This is a small sample, not an established false-positive rate or general accuracy claim. Repeated deterministic outputs are not additional independent examples.

The elephant sentence is grammatically correct and was preserved. The model receives no exercise prompt, so it cannot assess whether that sentence answers the lesson task. It also does not provide explanations, CEFR assessment, or dialogue replies. Unchanged output must not be interpreted as a guaranteed correct answer.

Recommendation: best tested candidate so far for sentence-level correction suggestions, subject to broader learner-text evaluation. Keep grading and task relevance separate. SmolLM3 remains the previously tested dialogue candidate. No production integration was performed.

Raw timings, inputs, outputs and model configuration: [results.json](../../design/evaluations/spanish-barto-2026-09-07/results.json). Compared with the earlier Qwen/SmolLM3 trial, this model receives raw sentences rather than instruction-following tasks, so latency comparisons reflect different workloads.
