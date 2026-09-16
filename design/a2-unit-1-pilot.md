# A2 Unit 1 LAN pilot

Implemented sample: `/muestra/a2/1`, also linked from the lesson catalogue and
the existing Vitamina A2 Unit 1 lesson. Sign in with an existing Español account.

- HTTP LAN: `http://192.168.0.9:5173/muestra/a2/1`.
- HTTPS LAN: `https://192.168.0.9:5174/muestra/a2/1` (device must trust the local
  certificate authority, as with the existing voice-practice pages).
- Android release: 1.0.45 / versionCode 46.

The sample contains the p.148 glossary (135 category entries, including phrases
repeated in separate source categories), eight authored grammar checks, both
original Unit 1 student-book audio tracks, links into the existing dialogue and
voice practice, and open writing/grammar practice using the existing BARTO
correction adapter. The complete lesson design remains in `a2-unit-1-sample.md`.
This pilot does not claim all parts of that design have been implemented.

Vocabulary has Spanish and English modes. Spanish definitions and examples are
generated on request by `SmolLM3-Q4_K_M.gguf`, the same model used by Claro. The
service uses the configured local conversation gateway URL, pins that model ID,
requires AI enabled and a loopback/local endpoint, and never falls back to cloud.
It uses structured JSON generation, a 45-second HTTP timeout, one active glossary
generation and a bounded 256-entry process cache. Cached definitions are lost on
API restart. Inference is shared with other local applications; unavailable/busy
responses let the learner retry or switch to English.

Writing uses the existing local `barto` correction provider and its 12-second
timeout. Original and suggested text remain separate. Partial/unavailable results
are labelled; unchanged text is not presented as proof of correctness. Grammar
gap questions use authored answers and explanations; open grammar sentences use
BARTO. Neither model grades proficiency or the writing task's completeness.

The explicit Save button stores language preference, marked vocabulary, the
writing draft and its first reviewed version in `a2_sample_progress`, keyed by
the authenticated user. Save before navigating to dialogue or leaving the page.
Grammar exercise answers and the separate short grammar textbox are session-only.
Marked vocabulary means practised, not mastered. Existing lesson IDs, accounts,
history and content files are preserved; no reseed is needed.

Validation: backend suite (117 passed, 1 opt-in test skipped), frontend build and
lint, real SmolLM3 definitions and BARTO correction, browser checks with an isolated
in-memory database (mobile width, desktop, saved draft/language, real audio,
definition generation and writing correction), LAN HTTP/HTTPS and auth checks.
