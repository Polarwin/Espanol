# ¡Vamos!

Adaptive Spanish learning application with a FastAPI backend and React frontend.

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
