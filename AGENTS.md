# ¡Vamos! Español — Agent Notes

## Building the Android APK

The app is a Capacitor shell: the web bundle from `frontend/dist` is copied into
`frontend/android/app/src/main/assets/public/`. Data always comes from the API
server, so only **frontend/UI changes** require a new APK.

**Always update the APK with any frontend change**: bump `versionCode` /
`versionName` in `frontend/android/app/build.gradle`, rebuild, publish to
`content/downloads/vamos-espanol.apk`, then commit, push, tag `v<versionName>`
and create a GitHub release with the APK attached (`gh release create`). Do not
leave the site/APK serving a stale bundle.

### Environment gotchas (this machine)

- System Java is a **JRE only** (`/usr/lib/jvm/java-25-openjdk-amd64` has no
  `javac`). A full JDK 21 lives at `.android-sdk/jdk` (git-ignored, survives
  reboots). If it is missing, restore it with:
  ```bash
  mkdir -p .android-sdk/jdk
  curl -sL "https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/hotspot/normal/eclipse" \
    -o /tmp/temurin21.tar.gz
  tar -xzf /tmp/temurin21.tar.gz -C .android-sdk/jdk --strip-components=1
  ```
- The Gradle wrapper is pinned to **9.1.0** — required for Java 21+ toolchains
  (Gradle 8.x fails with `Unsupported class file major version`). Do not
  downgrade it.
- The Android SDK is local at `.android-sdk/` (`sdk.dir` is set in
  `frontend/android/local.properties`). Build-tools 35.0.0 and platform
  android-36 are installed.

### Build and publish

```bash
# 1. Build the web bundle and copy it into the Android project
npm --prefix frontend run build
npm --prefix frontend exec cap sync android

# 2. Build the APK with the project-local JDK
JAVA_HOME=/home/justin/Projects/Espanol/.android-sdk/jdk \
  frontend/android/gradlew -p frontend/android assembleDebug

# 3. Publish to the site's download link and verify
cp frontend/android/app/build/outputs/apk/debug/app-debug.apk content/downloads/vamos-espanol.apk
.android-sdk/build-tools/35.0.0/apksigner verify content/downloads/vamos-espanol.apk
sha256sum content/downloads/vamos-espanol.apk
```

### Backend/DB changes → restart services

When backend code or the seed content changes, migrate and restart:

```bash
./bin/alembic -c backend/alembic.ini upgrade head
systemctl --user restart vamos-api.service vamos-web.service vamos-web-https.service
```

- `vamos-api`: uvicorn on port 8011 (`backend.app.main:app`)
- `vamos-web` / `vamos-web-https`: Vite dev servers on 5173 / 5174

Smoke test after restart:

```bash
curl -s http://127.0.0.1:8011/api/lessons | python -c "import json,sys; print(len(json.load(sys.stdin())))"
```

## Content seeding

- Lessons are authored Python dicts in `backend/app/seed/` (`content.py`,
  `curriculum_content.py`, `vocabulary_content.py`, `conversation_content.py`,
  `reading_content.py`, `listening_content.py`). Titles must match exactly
  across vocabulary banks, conversation scenarios, reading passages and
  listening scripts. C1 units mirror `Vitamina/Vitamina C1` guía titles;
  C2 units are authored (no Vitamina C2 book exists).
- C1/C2 video lessons come from YouTube: `./bin/python -m backend.app.seed.video_fetch`
  (yt-dlp download → `content/sources/`, faster-whisper transcription, ffmpeg
  cut) generates `backend/app/seed/video_lessons_c.py`. `content/sources/` is
  git-ignored — a fresh clone must re-run `video_fetch` before seeding those
  lessons. Preview clips land in `content/seed/video-c*/video.mp4`.
- Non-destructive load: `sync_missing_lessons(db, media=True)` in
  `backend/app/seed/load.py`. Full wipe/reseed: `./bin/python -m backend.app.seed.load`
  (needs network for gTTS and ffmpeg for video rendering). Add `--news N` to
  also fetch N random RTVE news lessons (C1/C2, built by
  `backend/app/seed/news_content.py`); default 0 never touches the network.
  Dedup keys on lesson **title**, so news titles are deterministic per article.
- `SessionLocal` runs with `autoflush=False` — flush explicitly before any
  dedup-by-query logic.
