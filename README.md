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

Exercises now open in **Escuchar primero** mode: load the Spanish narration,
listen/replay at 0.75×, 1× or 1.25×, and answer with the transcript, vocabulary,
translation and suggested answers hidden. **Mostrar transcripción y ayudas**
reveals them without clearing answers. **Leer** retains the original reading
mode. Save answers explicitly; this is ungraded comprehension practice.

Audio is fetched through an authenticated endpoint (including in the Android
app). Watched-video packs reuse their static `lectura.mp3`; deleted watched audio
is reported unavailable, never regenerated. Other saved readings can request
CPU-only narration on demand, cached under `static/SpanishReading/app-audio-*`.
Those caches contain generated reading text/audio only, never learner responses.
The static exports also include an offline **escuchar.html** page with an audio
player, writable questions, and a collapsed transcript/help section. Offline
typed answers are not persisted; use the app to save them to your account.

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

### Automatic reading from new news videos

The **daily 06:00 cron is retired**. The user service
`vamos-news-reading-watcher.service` scans `/srv/files/ytwatcher/NoticiasEspanol/`
every 60 seconds. New finalized videos need a matching Spanish VTT/SRT file and
two minutes without file changes; partial downloads and missing subtitles wait.
It adapts the first five minutes (or the whole video if shorter) into four separate
packs: **A1, A2, B1 and B2**, using the local model and context-aware chunking.
A1 uses shorter, simple text and literal questions; B1/B2 add richer language,
causes, contrasts and supported inferences. Each has its own narration, questions,
vocabulary and English translation. Levels remain AI estimates, not certified
CEFR assessments. Four packs take longer than a single pack and run sequentially.

All generated files live in
`/srv/files/static/SpanishReading/news-<video-id>-<a1|a2|b1|b2>/`: `ejercicio.html`,
`traduccion.html`, `respuestas.html`, `imprimir.html`, `ejercicio.pdf`,
`ejercicio.json`, `subtitulos.txt`, and `resumenes.json`. A hidden `.pending` folder
in the same static directory stages the pack until the PDF is ready. Vocabulary
includes Spanish and English explanations. Generated packs remain unreviewed AI
drafts; questions are open-ended and ungraded.

Each existing account also receives a private copy under Práctica → Lectura;
answers are never included in the static export. Removing static reading files
does not erase app history or regenerate old packs. The metadata-only ledger
`backups/news-reading-watcher.sqlite3` stores identities/statuses, not generated
text. Keep this ledger when cleaning static files. Video IDs prevent duplicates
after renames, restarts, redownloads, or output cleanup. Existing videos are
baselined on installation, not backfilled; new arrivals during downtime are found
when the service resumes. Completed packs are never recreated automatically.

The shared generation lock prevents concurrent reading model jobs. Busy work is
retried on the next scan; failures retry after 10 and 20 minutes, then remain
failed after three attempts. Changed input subtitles can requeue a failed video.
Successful staged generation is reused if PDF creation or delivery needs retrying.
Per-level completion records preserve successful packs even if another level
fails; cleaning a completed level's files does not cause regeneration on retry.
Previously completed/baselined videos are not automatically backfilled.

Install with one command: `./bin/python tools/install_news_reading_watcher.py`.
It backs up the crontab, removes only the old reading entry, preserves unrelated
jobs, and enables the user service. Logs:
`journalctl --user -u vamos-news-reading-watcher.service`.
The machine, local LLM service, and source/output storage must be available.

### Listening packs from news videos

New news-watcher packs use a different audio policy by level:

- **A1:** adapted, frequent vocabulary and short sentences, with present-indicative
  requested in the writing prompt. Occasional harder forms do not block narration.
  Source facts are preserved through attribution, not by changing past events
  into current events.
- **A2, B1, B2:** select a contiguous, self-contained excerpt from the original
  subtitles. Assess vocabulary, grammar, complete meaning and pace for that
  level, then check the isolated excerpt for complete meaning. ffmpeg extracts original audio;
  its unrewritten subtitle text supplies the transcript, translation and questions.

Clips contain 50–300 words and last 15–180 seconds, with preferred paces
of 170/195/230 words per minute for A2/B1/B2. Pace is guidance, not a rejection
threshold. A2/B1 selection allows unfamiliar words and occasional harder grammar
when the main idea is accessible with context and vocabulary help. Word timestamps are preserved for rolling VTT captions;
coarse SRT captions are cut only at cue boundaries. Unterminated final sentences
are excluded. Audio duration is checked before publication.

A level with no accepted complete excerpt is skipped, with its reason recorded
in the watcher's private `skipped_levels` ledger table. It does not silently
receive simplified audio or retry indefinitely. Existing published packs and
learner answers remain intact. This policy applies to new news-watcher packs;
interactive surprise readings and daily reading texts still use adapted prose.
Levels and completeness are assessed by the local model, so packs remain drafts
for review; automatic subtitles can contain errors. The app and exported listening
page identify original versus synthetic audio.

### Local Spanish narration (CPU only)

New watcher packs also include `lectura.mp3`, `audio.json`, and
`audio-credits.txt` in the same static folder. Piper 1.8.0 uses the
`es_ES-sharvard-medium` Spanish (Spain) voice, speaker 0, at a slightly slower
learning pace. It narrates the adapted Spanish reading, not the questions/answers.

Install with `./bin/python tools/install_piper.py`. Python 3.12, Piper and the
voice are isolated in the git-ignored `.local-tts/` directory. Runtime uses only
ONNX's CPU provider (no CUDA/Torch/GPU package), two inference threads, and a
low-priority short-lived process. There is no always-running speech model and
no internet request during synthesis. Successful narration is cached by text
and voice settings; export retries don't synthesize it again.

To narrate an existing pack, run
`.local-tts/venv/bin/python tools/piper_narrate.py /path/to/ejercicio.json`.
Audio stays beside the JSON. The voice's SHARVARD dataset is CC BY 3.0; attribution
and source links accompany each MP3. CPU-only applies to narration, not to the
separate local LLM generating the reading text. Audio failure leaves a new pack
staged for retry rather than marking an incomplete pack delivered.

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
