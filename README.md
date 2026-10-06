# ¡Vamos!

Adaptive Spanish learning application with a FastAPI backend and React frontend.

AI setup and provider switching: [operations guide](design/ai-operations.md).

AI integration instructions: [conversation and writing providers](design/ai-conversation-writing-guide.md).

## Lectura sorpresa

Open **Práctica → Lectura** (`/practica/lectura`) and choose **Crear una lectura sorpresa**.
The default mixes the library (published level-matched reading passages, indexed
textbook pages, and Spanish subtitle files in `VAMOS_WATCH_DIR`) with Spanish
VTT/SRT files in `/srv/files/ytwatcher/NoticiasEspanol/`. Filters let learners
choose a source and A1–C2 adaptation level. Videos without subtitles are skipped;
this feature does not transcribe video or download outside sources.

Each private, saved exercise has five open questions, eight vocabulary entries
with Spanish/English explanations, and separate translation and suggested-answer
views. Save written responses before leaving. This is ungraded practice: the
local model's draft may contain errors and is not a fact-check of the news.

Generation uses the shared `tools/subtitle_reading.py` pipeline with UTF-8-aware
context budgeting and hierarchical summaries, never silent source truncation.
It always calls the loopback gateway `http://127.0.0.1:8349/v1`; no cloud fallback.
`VAMOS_READING_MODEL` defaults to `Qwen3.5-2B-Q4_K_M.gguf` and
`VAMOS_READING_CONTEXT_SIZE` to 8192 (must match llama-server `-c`).
`VAMOS_READING_NEWS_DIR` changes the news root. This dedicated local reading
pipeline is independent of the conversation provider and its enable flag.

The current single-process API runs at most one reading job at a time; duplicate
requests resume that user's existing job, while other users receive a busy
message. Leaving the page does not stop generation. A server restart marks
interrupted jobs failed on the next read; learners can retry. Keep one API worker
until the in-process executor is replaced with a shared job queue. Texts and
learner answers stay in the authenticated database, not the public media folder.

Tests: `./bin/python -m pytest backend/tests/test_reading.py -q`,
`python3 -m unittest discover -s tools -p test_subtitle_reading.py`, and
`node tools/test_reading_ui.cjs` (Playwright; optional `PLAYWRIGHT_MODULE` and
`CHROMIUM_PATH`). The opt-in `tools/smoke_reading.py` calls the real local model
through the running API using a temporary account, with the API JWT configuration
provided in its environment. It cleans up only its own test data on completion.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
cd frontend && npm install && cd ..
```

Replace `VAMOS_JWT_SECRET` in `.env` with a random secret of at least 32 characters.

Create or update the database, then load the demonstration lessons:

```bash
./bin/alembic -c backend/alembic.ini upgrade head
./bin/python -m backend.app.seed.load
```

## Development

Start the backend from the project root on port `8011`:

```bash
./bin/uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8011
```

## Android app

The Capacitor Android wrapper lives in `frontend/android`. Its interface is
bundled into the APK while lessons and media come from the public HTTPS API, so
content updates are available without publishing a new APK. Build it with an
Android SDK and Java 21:

```bash
cd frontend
npm run android:apk
```

The current debug-signed installer is published at
`https://espanol.justinrecipes.duckdns.org/media/downloads/vamos-espanol.apk`.

Start the frontend in another terminal:

```bash
cd frontend
npm run dev
```

For microphone access on the intranet, start the additional mkcert-backed
HTTPS server (reusing nextERP's LAN certificate):

```bash
cd frontend
npm run dev:https
```

Open `https://192.168.0.9:5174`. Phones must trust the existing nextERP mkcert
CA first; it is available from the home server at `/lucia/mkcert-ca.pem`.

Vite listens on all network interfaces and proxies `/api` and `/media` to the
backend at `http://localhost:8011`. From another device on the same network,
open `http://<this-computer-ip>:5173`.

Backend requests and exception traces are written to a rotating log (5 MB per
file, three backups):

```bash
tail -f logs/vamos.log
```

Set `VAMOS_LOG_FILE` to use a different location. Request bodies and
authorization headers are never written to this log.

Only expose these development servers on a trusted private network. A firewall
may need to allow inbound TCP connections to port `5173`; clients do not need
direct access to backend port `8011` because Vite proxies the requests.

## Content sources

The backend discovers content in both configured directories:

- `/srv/files/ytwatcher/Espanol`
- `/home/justin/Projects/Espanol/Vitamina`

`GET /api/content/sources` reports the configured source paths without walking
potentially slow network mounts during a web request. Automated transcription, OCR,
segmentation, copyright review, and lesson publication belong in a separate
background ingestion worker; this scaffold deliberately does not publish new
files without review.

Pronunciation recording has a stable API route, but returns `501` until a speech
analysis worker using transcription and forced alignment is configured.

## Checks

```bash
./bin/pytest -q backend/tests
cd frontend && npm run lint && npm run build
```
