# Code audit — issue list

Audited 2026-08-20. Scope: full backend (`backend/app`, routers/services/seed/migrations), full frontend (`frontend/src`), Android/Capacitor shell, systemd deploy units, dependencies, and the shipped APK. This supersedes the 2026-08-14 UI/UX audit (still in git history); its open items are not repeated here.

**This is an audit only — no product code was changed.** Every issue below was verified against the code (and, where noted, against the live DB, running services, or the shipped APK). Items marked *needs verification* could not be fully confirmed from the workspace.

## High

### H1. Production API signs JWTs with the committed dev secret
- `backend/app/config.py:14` (`jwt_secret = "dev-only-secret-change-me-before-sharing"`), used by `backend/app/services/security.py:37,51`.
- Verified: no `.env` exists in the project root; `systemctl --user show vamos-api.service` shows no `EnvironmentFile`, no drop-ins, and no `VAMOS_*` variables. The live API signs tokens with a string published in the git repo. `vamos.db` holds real user accounts.
- Anyone with repo access can forge a valid token for any `user_id` and fully impersonate them (`create_token` only embeds `sub`). Blast radius depends on whether the GitHub repo is public — *needs verification*.
- Fix: generate a real secret into `.env` (or an `EnvironmentFile=` in the unit), restart `vamos-api`, and make startup fail or warn loudly when the default secret is in use.

### H2. Every exercise attempt advances the core loop — progress desyncs from what the user did
- `backend/app/routers/exercises.py:48-54` calls `advance_state` unconditionally on **every** attempt (correct or not, any lesson, no idempotency). Frontend: `Assessment.tsx:94` fires one `submitAttempt` per question; `Practica.tsx` does the same.
- One assessment (~20 questions) ticks the Mi Ruta stepper through multiple clips and into `adapta`/`conversa` without the user visiting `/ruta`; lessons get silently skipped. `path/advance`'s step guard (`routers/path.py:121-142`) only protects that one endpoint.
- Fix: advance the loop only from `/api/path/advance` (step-guarded, idempotent), or gate attempt-driven advancement on the exercise belonging to the current lesson/step.

### H3. Unlimited skill-score grinding via revealed answers
- `backend/app/routers/exercises.py:31-45` + `backend/app/services/scoring.py:69-72`: a failed attempt returns the correct answer (`"Casi. La respuesta correcta es: …"`), and nothing prevents resubmitting it — or repeating any known answer — for full success deltas. `apply_skill_deltas` (`services/progress.py:33-59`) applies each one.
- Skill scores, the adaptive lesson picker, and weekly recaps become meaningless.
- Fix: record one scored attempt per user/exercise, or award deltas only on the first (correct) attempt.

### H4. Shipped APK is a debuggable debug build signed with the public Android Debug key
- `content/downloads/vamos-espanol.apk` — verified via aapt/apksigner: `android:debuggable=true`, cert `CN=Android Debug` (versionCode 37 / 1.0.36, matches `frontend/android/app/build.gradle:10-11`). Built via `assembleDebug`; the `release` block has `minifyEnabled false` and no `signingConfig`.
- `debuggable=true` lets anyone with the device attach a debugger and inspect/inject into the WebView; Play-Store-rejected and scanner-flagged. The debug key lives only in `~/.android/debug.keystore` on this machine — losing it means no update can ever install over the old app (signature mismatch → reinstall, losing the stored token).
- Fix: add a release `signingConfig` (keystore outside the repo, credentials via env), ship `assembleRelease`, and back up the release keystore.

### H5. No backup of the production DB; full reseed orphans completions and wipes progress
- `vamos.db` (repo root, git-ignored, and it *is* the production DB) has no backup script, cron, or timer anywhere in the repo.
- `backend/app/seed/load.py:91-103` `wipe()` deletes `Attempt`, `Exercise`, `Phrase`, `Segment`, `Lesson` — but **not** `LessonCompletion`. Without `AUTOINCREMENT`, SQLite reissues rowids from 1, so after a reseed a user's old completion of lesson id 5 silently marks the *new* lesson id 5 as completed (`routers/progress.py:29-38` and `routers/lessons.py:188-201` trust these ids). Permanently wrong completion state.
- Fix: delete `LessonCompletion` in `wipe()`; add a scheduled `sqlite3 vamos.db ".backup …"` job; take a timestamped backup before any wipe/seed/migration.

## Medium

### M1. Production web traffic served by Vite dev servers
- `deploy/systemd/vamos-web.service:12-13` and `vamos-web-https.service:12-15` run `NODE_ENV=development npm run dev -- --host 0.0.0.0` for the public site: unminified on-the-fly transforms, filesystem watching, HMR websocket, no static caching.
- Fix: serve `frontend/dist` with a static server/reverse proxy; keep dev servers for development.

### M2. Public API origin hardcoded into the shipped native app
- `frontend/src/api/client.ts:29` bakes `https://espanol.justinrecipes.duckdns.org` into every native API/media call (also `vite.config.ts:19`, `capacitor.config.ts:4`). If the hostname lapses or hosting moves, every installed APK is broken until users manually sideload a new build — there is no update channel.
- Fix: build-time `VITE_API_ORIGIN` env var, plus a graceful "please update the app" failure path.

### M3. `wipe()` deletes media on disk before the DB transaction is safe
- `backend/app/seed/load.py:100-103`: `shutil.rmtree(content/seed)` is immediate and irreversible, while the DB deletes are only flushed. If `generate_media` fails mid-seed (gTTS/ffmpeg/network, missing `content/sources/`), the rollback restores old lessons whose media files are already gone → every lesson video 404s.
- Fix: generate into a temp dir and swap only after success.

### M4. Enrichment-added audio exercises reach production with no audio file
- `backend/app/seed/load.py:174-183`: newly authored exercises added to an existing lesson are inserted with `audio_path=None`; media generation only runs for new lessons. Also, the reconcile branch (`load.py:165-173`) only syncs `options`/`passage` — fixes to `expected_answer`, `instructions`, or `skill_weights` never propagate to existing rows.
- Fix: generate mp3s for new enrichment exercises; extend reconciliation to the remaining fields.

### M5. video_fetch can transcribe a new video with the previous video's cached transcript
- `backend/app/seed/video_fetch.py:259-261,476-488`: transcript cache is keyed only by slug; after a "no clean window" failure the video is deleted but the transcript kept, so the next candidate video is cut at timestamps from the wrong audio — a silently wrong generated lesson.
- Fix: include the source filename/hash in the cache key, or delete the transcript when the video is replaced.

### M6. Registration accepts empty passwords and non-emails — **fixed 2026-08-20**
- `backend/app/schemas/auth.py:8-12`: `RegisterRequest` has no `Field` constraints, no `EmailStr` — 0-length passwords, arbitrary strings as email, unbounded names/interests. (Contrast: `ProfileUpdate` does validate, so a garbage-at-registration name can never be re-set via PATCH.)
- Fix: `EmailStr`, `password: Field(min_length=8, …)`, bounds on the rest.
- Fixed: `RegisterRequest` now enforces an email regex pattern, `password` 8–128 chars, `display_name` 1–60 (trimmed), `interests` ≤10 entries of ≤40 chars; covered by new tests in `backend/tests/test_auth.py`.

### M7. No rate limiting anywhere, including auth and CPU/disk-expensive endpoints — **fixed 2026-08-20**
- No limiter middleware in `main.py`. Login is online-brute-forceable; `/api/pronunciation/evaluate` and `/api/conversation/respond` run faster-whisper inference per call; each unique `/api/speech/example` phrase triggers an outbound gTTS request and writes a permanent cache file — unbounded disk growth.
- Fix: `slowapi` or equivalent on `/api/auth/*` and the speech endpoints; cap the TTS cache.
- Fixed: new in-memory sliding-window limiter (`backend/app/services/ratelimit.py`, no new deps) applied as a FastAPI dependency — 10/min on register+login, 30/min on pronunciation/conversation/speech-example; tests in `backend/tests/test_ratelimit.py`. (The TTS cache cap remains open.)

### M8. Draft/unpublished lessons readable and completable by ID — **fixed 2026-08-20**
- `routers/lessons.py:112-121` (`lesson_detail`), `178-186` (`complete_lesson`), `207-211` (assessment) don't check `lesson.status`, while list/select do filter `status == "published"`. Unfinished content is reachable by guessing IDs and inflates completion counts.
- Fix: 404 on non-published lessons in detail/complete/assessment.
- Fixed: all three endpoints now 404 unless `lesson.status == "published"`; test in `backend/tests/test_lessons.py::test_draft_lesson_not_reachable_by_id`.

### M9. Review answers farmable; queue leaks answers to the client — **fixed 2026-08-20**
- `routers/review.py:53-75`: `answer_review` never checks `item.due_date <= today` — the same item can be answered in a loop, applying skill deltas each time. `GET /api/review` (`review.py:23-34`) also ships the expected `answer` for every item up front.
- Fix: reject answers for not-yet-due items; omit `answer` from the queue payload.
- Fixed: `answer_review` returns 409 while `due_date` is in the future; the queue payload no longer includes `answer` (backend `review.py` + frontend `ReviewItem` type); tests in `backend/tests/test_review.py`.

### M10. `comprueba` quiz is unenforced — **fixed 2026-08-20**
- `routers/path.py:121-160`: `/api/path/quiz` records nothing, and `path/advance` with `step="comprueba"` never requires a passed quiz. The quiz is client-side decoration.
- Fix: persist quiz pass per clip and require it to advance (or accept the step is advisory).
- Fixed: new `user_state.quiz_passed` column (migration `b4e8c2a71d05`), set on a correct quiz answer while on `comprueba`; `path/advance` returns 409 without it; `advance_state` resets it on every transition; frontend allows quiz retries and shows the 409 message; tests in `backend/tests/test_journey.py`.

### M11. "Práctica rápida" strips passages and audio from reading/listening exercises — **fixed 2026-08-20**
- `frontend/src/pages/Practica.tsx:25,77-84`: exercises are flattened from all assessment groups but the page renders only `prompt` + options/textarea — reading exercises without their `passage`, listening without the audio player.
- Fix: render passage/audio like `Assessment.tsx:212-218`, or filter to self-contained types.
- Fixed: `Practica.tsx` now renders `exercise.passage` in the same styled block and `exercise.audio_url` via `AudioPlayer`, matching `Assessment.tsx`.

### M12. MiRuta clip player ignores `clip_end` — **fixed 2026-08-20**
- `frontend/src/pages/MiRuta.tsx:93` passes `startTime={today.clip_start}` but never `endTime={today.clip_end}` (though `VideoPlayer` supports it and the API supplies it). "Mira el clip" plays the rest of the video; the scrubber spans the full file.
- Fix: pass `endTime` (or change the copy).
- Fixed: `MiRuta.tsx` now passes `endTime={today.clip_end}` to `VideoPlayer`.

### M13. Misleading error after a successful route advance — **fixed 2026-08-20**
- `frontend/src/pages/MiRuta.tsx:46-57`: `advancePath` + `getProgress` share one `try`; if the refresh fails after a successful advance, the UI shows "No se pudo guardar este paso" even though it saved — and a retry advances the *new* step, skipping one.
- Fix: handle the two calls separately; treat the progress refresh as best-effort.
- Fixed: `advance()` uses the `TodayPath` returned by `advancePath` and runs the `getProgress` refresh afterwards as fire-and-forget with its own `.catch()` — no error banner on refresh failure.

### M14. Opening any lesson silently re-points the user's route — **fixed 2026-08-20**
- `frontend/src/pages/Leccion.tsx:18` calls `api.selectLesson` on every page view; the backend (`lessons.py:93-109`) makes it the current unit and resets loop state to `mira`/clip 0. Catalog cards say "Abrir unidad" — nothing says viewing resets the route. *Needs product verification* whether this is intended.
- Fix: explicit selection action or a confirmation notice.
- Fixed: the page no longer auto-selects on view; it fetches `/api/path/today` to compare against the viewed lesson and only shows an explicit "Empezar esta unidad (sustituye tu unidad actual)" button when the lesson is not the current unit.

### M15. Mock fallback turns auth failures into successful logins (dormant hazard) — **fixed 2026-08-20**
- `frontend/src/api/client.ts:99-106,131-140`: `withMock` catches *any* error. With `VITE_ENABLE_MOCKS=true`, a 401 wrong-password login or 409 duplicate register falls through to `mockLogin()`/`mockRegister()` "success". Verified the current `dist` bundle compiled the fallback out, so production is safe today — but nothing in code prevents a bad build. Mock code ships in the production bundle regardless.
- Fix: fall back only on network errors, never on `ApiError` from `/api/auth/*`.
- Fixed: `withMock` now falls back only when the error is a `TypeError` (fetch network failure) and not an `ApiError`; HTTP errors always propagate.

### M16. Double-tap on record leaks a mic stream and an interval — **fixed 2026-08-20**
- `frontend/src/hooks/useRecorder.ts:38-75`: `start()` is async; mic buttons (`Conversacion.tsx:68`, `RepeatPhraseCard.tsx:50-58`, `VideoShadowing.tsx:111`) aren't disabled while `getUserMedia` is in flight. Two fast taps overwrite the refs — the first stream tracks and interval are never cleaned up.
- Fix: guard `start()` with an in-flight flag; disable buttons until state settles.
- Fixed: `start()` no-ops while a start is in flight (`startingRef`) or already recording; the hook exposes a new `starting` state and all three mic buttons are disabled while it is true.

### M17. HTTPS service depends on another project's cert directory and a hardcoded LAN IP
- `deploy/systemd/vamos-web-https.service:14` reads certs from `/home/justin/Projects/nextERP/certs` (default also in `vite.config.ts:7`); certs are issued for IP `192.168.0.9`. Removing nextERP or a DHCP change silently breaks the service.
- Fix: project-local cert dir, parameterized IP.

## Low

Backend:
- L1. `datetime.utcnow()` throughout models/services (deprecated since 3.12, naive datetimes; project runs Python 3.14). `security.py:31` already uses `datetime.now(UTC)` — inconsistent.
- L2. Group invite codes uppercased (`routers/social.py:41,48`) — entropy loss; unique-collision has no retry/rollback → 500.
- L3. Registration race: check-then-insert on email isn't atomic → unhandled `IntegrityError` 500 instead of 409; no rollback in `get_db` (`db.py:19-24`).
- L4. `GET /api/lessons` and `GET /api/lessons/{id}/assessment` are unauthenticated while sibling endpoints require auth — looks accidental; decide intentionally.
- L5. Dead code: `routers/exercises.py:49-53` computes `next_lesson` for a transition `advance_state` ignores. `AttemptRequest.answer` has no length bound. `services/recap.py:75` instantiates throwaway ORM objects per attempt.
- L6. Full reseed permanently loses the 9 RTVE news lessons (they come from `random.sample`, not the import-time catalog) — a routine reseed silently shrinks the catalog from 95 to 86. Persist fetched news dicts for replay.
- L7. `load.py:282` mutates the module-global `LESSONS` with news lessons (double `load()` in-process accumulates duplicates).
- L8. Committed `video_lessons_c.py` embeds absolute machine-specific `/home/justin/...` source paths; seeds on another machine fail hard mid-seed (see M3).
- L9. `reconcile_media_timings` results silently dropped (`load.py:134-135`) — missing media is invisible operationally.
- L10. news_content: `_grammar_tip` substring matching ("pero" matches "perro"); empty titles → `"Noticias: "`; 60-char truncated title collisions silently drop articles.

Frontend:
- L11. API failure rendered inside the success-styled "¡Repaso al día!" card (`Repaso.tsx:36`).
- L12. Weekly-recap failure leaves a permanent "Cargando…" (`Progreso.tsx:41,103-109` — error swallowed).
- L13. Scrubbers are `<button>`s with pointer-only seeking (`VideoPlayer.tsx:151-168`, `AudioPlayer.tsx:83-97`) — keyboard activation seeks to ~0; no `role="slider"`/arrow keys.
- L14. Conversación mic button has no accessible name (`Conversacion.tsx:68`).
- L15. Conversación setup fetch has no cancellation (`Conversacion.tsx:39-44`) — stale setup can win a route-change race.
- L16. FeedbackPanel: React keys from words (collide on repeats) and a hardcoded "de" highlight regardless of the actual tip (`FeedbackPanel.tsx:67-75`).
- L17. `getSpeechExample` bypasses the shared 401 handling (`client.ts:210-221`).
- L18. VideoPlayer keeps stale time/duration when `src` changes (`VideoPlayer.tsx:37-39,101-104`).
- L19. Placement keeps a stale error after the level changes (`Placement.tsx:30-35`).
- L20. Dead placeholder state in Assessment (`Assessment.tsx:52-53`).
- L21. Groups lets you "Animar" yourself (`Grupos.tsx:56`; no server-side check in `social.py:54-59`).
- L22. VideoShadowing hangs forever on a segment-less lesson (latent — all 95 current lessons have segments).
- L23. Mock API uses string IDs vs the real API's ints; TS types declare `string`, masking the mismatch (no live bug — everything stringifies).

Infra:
- L24. `httpx` is the only unpinned dependency (`requirements.txt:14`).
- L25. Unrelated project's unit (`deploy/systemd/nexterp.service`) committed in this repo.
- L26. `.env.example` doesn't document all `VAMOS_*` vars (`VAMOS_JWT_ALGORITHM`, `VAMOS_CONTENT_DIR`, whisper settings, …) and uses a CWD-relative DB path that only works because the unit sets `WorkingDirectory`.
- L27. `frontend/.gitignore:1-7` contains a false comment about the root `.gitignore` plus a broad `!*` un-ignore.
- L28. `android:allowBackup="true"` in the shipped APK — WebView localStorage (auth token) extractable via `adb backup`.
- L29. `passlib==1.7.4` pinned — unmaintained since 2020; works today only because the code deliberately uses `pbkdf2_sha256`. Plan migration (e.g. `pwdlib`).

## Checked and found sound

- **No IDOR / cross-user access**: every per-user path is keyed off the authenticated `user.id`; review/group endpoints verify ownership/membership; no user-id path parameters exist.
- **No SQL injection**: all queries use SQLAlchemy bound parameters; no raw SQL.
- **JWT verification** pins the algorithm, rejects unknown users; no alg-confusion surface. CORS is an explicit origin list, not wildcard.
- **Upload handling**: 10 MB caps, random temp paths, `finally` cleanup, only the file suffix taken from user filenames; `/media` static mount guards traversal.
- **Schemas**: responses omit `expected_answer`/`password_hash`; profile update whitelists fields (no mass-assignment). Placement grading is recomputed server-side.
- **Exercise data quality** (verified programmatically over all 86 catalog lessons): no duplicate titles/slugs; every MC answer ∈ options; no empty/duplicate options; every reading exercise has a passage; all vocabulary/conversation/listening/reading bank keys match lesson titles exactly.
- **Migration chain**: linear, single head, working downgrades, `alembic check` reports no schema drift; live DB at head.
- **Frontend/backend shape parity**: `TodayPath`, `ConversationSetup/Result`, `PlacementQuestion/Result`, `Progress`, `WeeklyRecap`, `ReviewItem/Result`, `LessonDetail`, `Assessment`, `PronunciationResult` all match; media URL rewriting covers every emitted key.
- **Loop stepper & conversa return flow**: `advancePath` is idempotent per expected step; the swallow-errors continue flow is safe because of it.
- **Android manifest**: no cleartext traffic (denied by default at targetSdk 36, app speaks HTTPS only), no exported components beyond the required launcher activity, permissions match features.
- **Toolchain pinning** matches `AGENTS.md` (Gradle 9.1.0, AGP 8.13.0, SDK 36); no keystores or secrets committed (verified git history + tracked-file grep); `.gitignore` covers `vamos.db`, `content/sources/`, `.android-sdk/`, logs.
- **systemd**: `NoNewPrivileges`, sane restart policies, lingering enabled, web units correctly ordered after the API.
- **Test suite**: 59/59 backend tests pass.

## Suggested priority order

1. **H1** (rotate JWT secret — invalidates existing tokens) and **H4** (release signing) — live security exposure.
2. **H5** (backup + `wipe()` fix) — one routine command away from data loss.
3. **H2/H3** (loop advancement + skill grinding) — progress integrity.
4. **M1/M2** (static hosting, configurable API origin) — deployment fragility.
5. Validation/rate-limit batch: **M6, M7, M8, M9**.
6. UX correctness batch: **M11–M16**, then Low items as time allows.

## Audit limitation

No browser automation or device-matrix testing was performed; phone findings are code-based. Whether the GitHub repo is public (H1 blast radius) and host firewall rules for port 8011 could not be verified from the workspace.
