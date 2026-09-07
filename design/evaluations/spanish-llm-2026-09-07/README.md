# Local Spanish tutor model comparison — 2026-09-07

Recommendation: SmolLM3 is the better candidate of these two for a constrained practice pilot, with advisory feedback only. Neither is reliable enough for automatic writing grades. No serving configuration or app code was changed.

## Method

Live requests through the existing http://127.0.0.1:8349/v1 gateway, on the i5-10210U / MX350 host. Eight synthetic Spanish tasks, two runs per model, 32 requests total. Both installed Q4_K_M models used temperature 0.7, top_p 0.8, seeds 42/43, max_tokens 200, streaming, enable_thinking=false and /no_think. No reasoning text was returned; all responses stopped normally. Requests were sequential because the gateway serves one generation at a time.

Tasks: cafe role-play, train-booking memory, explicit past-tense writing, valid subjunctive, age/gustar errors, valid regional Spanish, off-topic answer, past counterfactual. Prompts and verbatim outputs are in cases.json and results.json. run.py reproduces the requests and writes to /tmp/vamos-llm-comparison (create that directory first).

## Measured latency

| Metric | Qwen3.5-2B | SmolLM3 |
|---|---:|---:|
| Warm complete-response median, 15 requests | 1.91 s | 2.33 s |
| Warm range | 0.94–5.15 s | 1.06–4.70 s |
| Warm first-content median | 0.44 s | 0.66 s |
| First response after model switch, one observation | 10.31 s | 12.67 s |
| Warm dialogue median, 3 requests | 1.30 s | 2.33 s |
| Writing median, 12 requests | 2.15 s | 2.38 s |

SmolLM3's overall warm median was 0.42 seconds higher. These are task response times, not equal-token throughput comparisons: output lengths vary. Prompts benefited from the engine's prefix cache. First-response measurements include model loading/switching and generation, not isolated model-load time. No concurrent workload, speech recognition, TTS, network-to-phone latency, or long essay benchmark is included.

## Qualitative findings

- Past tense: SmolLM3 produced “Ayer fui al mercado y compré dos manzanas” in both runs. Qwen accepted the present-tense answer in run 1 with a false explanation of regional tense use; in run 2 it proposed “Ayer vi al mercado,” an incorrect correction.
- Age and agreement: both models accepted “Soy veinte años y me gusta las películas españolas” in both runs. The expected correction is “Tengo veinte años y me gustan las películas españolas.” This basic repeated error rules out autonomous grading.
- Past counterfactual: Qwen accepted “Si habría sabido…” in both runs. SmolLM3 accepted it once and correctly changed it to “Si hubiera sabido…” once.
- Valid subjunctive: both accepted “Depende de que tengamos tiempo. Ojalá hubiera más trenes los domingos” in both runs.
- Regional Spanish: neither marked “Hoy fui … frutillas” as erroneous. SmolLM3 sometimes repeated or paraphrased text despite being told not to rewrite correct answers.
- Task relevance: SmolLM3 correctly explained the off-topic response in both runs. Qwen correctly rejected it once; its second rejection confused the task and the answer in its explanation.
- Cafe role-play: SmolLM3 offered an appropriate milk alternative in both runs. Qwen did so once; its first response drifted into unrelated beverage questions.
- Train memory: neither consistently restated the destination, day, time and one-way preference. SmolLM3 mentioned Valencia in one run; the other asked whether the user needed help buying a ticket. Qwen gave generic confirmations and once asked about leaving immediately despite the specified trip being tomorrow.

These are manual observations on a small synthetic set, not teacher-certified scores or general model rankings. Results apply to the installed quantizations and these non-thinking prompts/settings. Prompt tuning and larger evaluation could change the outcome.

## App fit

SmolLM3 warrants the next constrained dialogue pilot: better observed content quality with a modest warm latency increase. Preserve authored scenarios and validate task-specific behavior. Its writing feedback remains experimental; do not use it to assign progress or correctness scores. Qwen3.5-2B's speed advantage does not compensate for its observed correction errors. If a single model is chosen for the pilot, SmolLM3 also avoids switching between dialogue and writing models. The wrapper unloads idle models after 300 seconds, so first-turn delay must be accounted for separately. This experiment does not establish that SmolLM3 beats Qwen3-1.7B under an identical benchmark; that model was only spot-checked earlier.
