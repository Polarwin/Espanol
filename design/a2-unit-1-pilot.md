# A2 Unit 1 LAN pilot

Implemented sample: `/muestra/a2/1`, also linked from the lesson catalogue and
the existing Vitamina A2 Unit 1 lesson. Sign in with an existing Español account.

- HTTP LAN: `http://192.168.0.9:5173/muestra/a2/1`.
- HTTPS LAN: `https://192.168.0.9:5174/muestra/a2/1` (device must trust the local
  certificate authority, as with the existing voice-practice pages).
- Android release: 1.0.50 / versionCode 51.

The sample contains the p.148 glossary (135 category entries, including phrases
repeated in separate source categories), eight authored grammar checks, both
original Unit 1 student-book audio tracks, links into the existing dialogue and
voice practice, and open writing/grammar practice using the existing BARTO
correction adapter. The complete lesson design remains in `a2-unit-1-sample.md`.
This pilot does not claim all parts of that design have been implemented.

Vocabulary now follows 27 guided chapters, each with three to seven entries.
One- or two-entry category tails are merged into the preceding chapter on the
same topic. All 135 entries remain covered. The data migration remaps existing
positions and preserves current quizzes, scores, feedback and review queues.
A pre-merge quiz can finish its original question set before teaching the added
words; someone already in a tail finishes just that remaining portion once.
No completed vocabulary is reset. This is a backend content change; APK 1.0.48
receives the new chapter layout through the existing API without rebuilding.
Validation for the merge: 214 backend tests passed, one opt-in test skipped,
including remapping every old chapter in teaching, quiz and summary phases.
Existing production journeys were backed up and checked against the migration
result before restarting the service.
The learner sees one teaching card at a time, can hear the word with browser
Spanish TTS, hide the meaning for recall, and then takes a short quiz. There is
no category picker. Chapter order moves from personality/interests through daily
life and social encounters into learning and city activities. All 135 original
category entries remain covered.

Quizzes alternate between finding a word from its meaning and finding a meaning
from its word. Authored Spanish cues and the existing English meanings provide
stable questions. Correct answers and grading stay on the server; generated
model output never determines a quiz grade. Distractors exclude the same category
to avoid close synonyms, and exclude repeated words/translations. This first
version tests recognition rather than free recall or certified mastery.

Correct quiz answers show varied encouragement and advance automatically after
1.1 seconds, including in review and final tests. Incorrect answers retain the
Continue button so the learner can read the explanation. Pending save failures
pause automatic advancement until the learner retries; unmounting cancels the
timer. Reloading a saved correct answer resumes the automatic transition.
Round summaries vary by result (all correct, some correct, or no correct answers)
and round position. Mistake feedback and teaching-card memory prompts also vary;
scores, instructions and navigation labels remain explicit and consistent.

Errors enter a personal review queue. A round covers up to five error items,
each appearing twice in different question directions. An item leaves the queue
after two correct review answers; another mistake resets that item's streak.
Completed chapters plus an empty mistake queue unlock a final test with all 135
entries in shuffled order. Final-test errors go into the same review queue.
Review returns the learner to the exact chapter/card they left. Final tests are
resumable and can be retaken after reviewing errors.

The new `a2_vocabulary_journey` table stores each user's position, scores, errors,
language preference and current feedback. Every action is saved automatically,
with optimistic revisions and request IDs protecting against stale tabs and a
retried lost response. Old practice checkmarks are preserved separately but do
not count as quiz passes. Existing writing drafts are untouched.

Vocabulary has Spanish and English modes. Teaching cards show an authored simple
meaning immediately. Additional Spanish explanations and examples are generated
on request by `SmolLM3-Q4_K_M.gguf`, the same model used by Claro. The
service uses the configured local conversation gateway URL, pins that model ID,
requires AI enabled and a loopback/local endpoint, and never falls back to cloud.
It uses structured JSON generation, a 45-second HTTP timeout, one active glossary
generation and a bounded 256-entry process cache. Cached definitions are lost on
API restart. Inference is shared with other local applications; unavailable/busy
responses let the learner retry or switch to English.

Writing uses the existing local `barto` correction provider and its 12-second
timeout. The shared writing-feedback component shows removed text struck through
and additions highlighted, with a clean suggested version available on expansion.
Spacing-only changes have their own label; removed spaces are visible as ␠.
Identical text does not appear as a correction or as duplicate paragraphs.
Classification preserves accents, punctuation and word boundaries (for example,
«a ver» versus «aver» is not treated as a cosmetic spacing change).
Partial/unavailable results
are labelled; unchanged text is not presented as proof of correctness. Grammar
gap questions use authored answers and explanations; open grammar sentences use
BARTO. Neither model grades proficiency or the writing task's completeness.
Gap prompts explicitly name the target verb or communicative purpose and provide
the relevant choices as answer buttons, with immediate feedback on selection.
Open grammar/writing practice remains a textbox reviewed by BARTO. Older APKs
still receive choices within the prompt text. Feedback distinguishes a different valid meaning (for
example, «me cuestan los idiomas») from the target form requested by the exercise.

The explicit Save draft button retains the writing draft and its first reviewed
version in `a2_sample_progress`, keyed by the authenticated user. Older vocabulary
checkmarks and preference are retained there for compatibility. Its updates cannot
overwrite the separate vocabulary journey. Save writing before leaving the page;
vocabulary needs no manual save. Grammar exercise answers and the separate short
grammar textbox remain session-only. Existing lesson IDs, accounts, history and
content files are preserved; no reseed is needed.

Validation for 1.0.46: backend suite (123 passed, 1 opt-in test skipped), frontend
build and lint; complete all-chapter/final-test simulation, mistake review and
account isolation; mobile/desktop browser checks with an isolated database,
including teach/quiz/review/resume, language persistence, and a response dropped
after the server committed followed by an idempotent retry. Existing real model,
writing and audio integrations were verified in 1.0.45 and retained.

Writing-feedback validation in 1.0.50: four text-comparison tests, frontend build
and lint, and browser checks with controlled model responses for spacing-only,
spelling/accent edits, identical text, partial coverage and unavailability on
mobile/desktop. BARTO itself is unchanged; clearer feedback does not imply that
it detects every grammar or meaning problem.
