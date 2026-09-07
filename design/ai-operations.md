# Running conversation and writing AI

Implemented in September 2026. SmolLM3 generates conversation replies through the existing llama gateway; a persistent BARTO CPU worker suggests writing corrections. Routes, backend contracts and UI do not depend on a specific model vendor.

## Local services

```bash
./tools/spanish-barto/install.sh
cp deploy/systemd/vamos-barto.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now vamos-barto.service
curl http://127.0.0.1:8351/health
```

The worker listens only on loopback, loads the pinned model once, and has one active inference slot (busy calls return 429). It processes up to 12 Spanish sentence spans and skips sentences over 128 tokens, preserving whitespace and reporting partial coverage. It filters broad rewrites, number changes and noninitial capitalized-word changes conservatively. These checks do not prove preservation of meaning. In particular, errors can still be missed. Worker dependencies remain separate from the API's Python environment.

The existing gateway at `http://127.0.0.1:8349/v1` serves chat models and unloads them after inactivity. The API calls BARTO directly at `http://127.0.0.1:8351`; the shared llama gateway was not modified. Worker endpoints are internal and are not publicly proxied.

## Enable and switch providers

Settings live in `backend/app/config.py` and follow the existing `VAMOS_` environment convention. Production's API unit enables `VAMOS_AI_ENABLED=true`; development defaults to false. A service environment value overrides `.env`.

Defaults:

```dotenv
VAMOS_AI_ENABLED=true
VAMOS_AI_CLOUD_ENABLED=false
VAMOS_AI_CONVERSATION_ADAPTER=openai_compatible
VAMOS_AI_CONVERSATION_URL=http://127.0.0.1:8349/v1
VAMOS_AI_CONVERSATION_MODEL=SmolLM3-Q4_K_M.gguf
VAMOS_AI_CONVERSATION_LOCAL=true
VAMOS_AI_CORRECTION_ADAPTER=barto
VAMOS_AI_CORRECTION_URL=http://127.0.0.1:8351
VAMOS_AI_CORRECTION_MODEL=SkitCon/gec-spanish-BARTO-SYNTHETIC
VAMOS_AI_CORRECTION_LOCAL=true
```

Another local model: change `VAMOS_AI_CONVERSATION_MODEL` to its installed gateway model ID. Another local server: change the URL to its loopback endpoint (use a local tunnel for a LAN server). Keep conversation and correction settings independent. BARTO's checkpoint is pinned by its installer, not switched by changing the API model label.

For OpenAI conversation, configure the following with an evaluated API model ID and a server-side `OPENAI_API_KEY`:

```dotenv
VAMOS_AI_CLOUD_ENABLED=true
VAMOS_AI_CONVERSATION_ADAPTER=openai_responses
VAMOS_AI_CONVERSATION_URL=https://api.openai.com/v1
VAMOS_AI_CONVERSATION_MODEL=<evaluated-api-model-id>
VAMOS_AI_CONVERSATION_LOCAL=false
VAMOS_AI_CONVERSATION_KEY_ENV=OPENAI_API_KEY
```

For Claude, use adapter `anthropic`, URL `https://api.anthropic.com/v1`, the chosen Claude API model ID, and `VAMOS_AI_CONVERSATION_KEY_ENV=ANTHROPIC_API_KEY`. Set local=false and cloud_enabled=true, and supply that key to the service. Model IDs and endpoint feature support must be checked before switching. Consumer ChatGPT/Claude web subscriptions are not used by these adapters.

To use a chat model for correction, apply the corresponding settings with `CORRECTION` instead of `CONVERSATION`. Chat correction requests return only revised text; they do not assess task relevance or provide grammar explanations. These adapters have mocked protocol tests, but no paid cloud calls were made during implementation. Cloud use requires explicit configuration and never happens as an automatic local fallback. Local providers must use loopback URLs; cloud providers require HTTPS and a configured key. Secrets belong in protected service/environment files, not Git or frontend variables.

After changing service drop-ins, run daemon-reload; restart the API to apply settings. No frontend/APK change is needed for a provider switch with the same API contract. Set `VAMOS_AI_ENABLED=false` in the service environment to disable inference and retain scripted practice. The larger proposed JSON registry in [the design guide](ai-conversation-writing-guide.md) is not implemented; the environment settings above are authoritative for this release.

## Learner behavior

- Conversation supports typed responses or recorded audio, submitted with an explicit Send button. Four-turn sessions store history on the server and are scoped to the authenticated user and lesson. Request IDs prevent duplicate turn credit; stale turns return 409. Legacy clients without session IDs still work but lack history/retry protection.
- SmolLM3 handles the first three replies; the authored lesson closes the fourth. Busy, failed, malformed, oversized or truncated responses fall back to the authored prompt. The UI indicates this fallback.
- BARTO reviews submitted writing in assessments, writing reviews and typed conversation. Original and suggested text are shown separately, without auto-applying changes. Speech transcripts are not automatically marked as grammar errors.
- An unchanged result says no changes were suggested, not that the writing is perfect. Unavailable and partially reviewed responses are identified explicitly.
- Existing writing practice credit remains unchanged and is labeled as practice credit, not a grammar/content grade. Neither model decides assessment scores. Typed conversation credits writing practice rather than sentences spoken.

The current worker may take longer on several sentences; call timeouts are 12 seconds for correction and 20 seconds for conversation HTTP operations. Busy workers fall back immediately rather than building an unbounded queue. SDK/network timeouts are not an absolute end-to-end streaming deadline. Conversation providers return non-streaming text to the app.

## Verification and release

```bash
./bin/pytest backend/tests -q
# Explicit local inference, isolated test database; no real learner records:
VAMOS_TEST_LIVE_AI=1 ./bin/pytest backend/tests/test_ai.py -q
npm --prefix frontend run build
npm --prefix frontend run lint
```

Contract tests cover provider formats, cloud configuration, malformed/truncated responses, fallback, correction filtering, session ownership/history/retry, and separation of correction from credit. The opt-in smoke test calls the installed models through real application endpoints with a temporary database.

Apply Alembic migrations before restarting the API. The new `conversation_sessions` table persists history and the latest idempotent result. Frontend changes require the complete APK and GitHub release procedure in [AGENTS.md](../AGENTS.md). Provider configuration changes alone do not.
