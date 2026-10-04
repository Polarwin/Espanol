# Palabra a palabra — standalone offline flashcards

Deployed independently of ¡Vamos! at `/srv/files/static/EspanolFlashcards/`.
The existing nginx static location serves it at:

`https://192.168.0.9/ytwatcher/static/EspanolFlashcards/`

Open `EspanolFlashcards-offline.html` directly in a browser for fully offline use.
The HTML contains the complete deck, conjugations, CSS and JavaScript. No server,
API, model, CDN, account, fonts, or remote speech service is required. The served
version can also cache itself with a service worker on trusted HTTPS/localhost.
The self-contained download works independently of service-worker support.

## Content and study

- 1,097 cards and 319 verb paradigms at the initial build; counts are checked by
  the builder. Cards cover all ten Vitamina A2 glossary units plus selected words
  and verbs occurring in the local Ke books. This does **not** claim complete
  coverage of every book or all Vitamina levels.
- The Spanish–English glossary is extracted by column and line coordinates,
  restoring indented verb phrases. Reviewed Unit 1 translations override the
  original glossary where available. Some translation wording is edited for clarity.
- Ke additions use curated bilingual terms or Jehle infinitives matched against
  the local OCR index. Each card carries book and PDF-page references. References
  indicate the vocabulary's occurrence, not the source of every conjugation table.
- Jehle conjugations include indicative present, preterite, imperfect, perfect,
  future, conditional, present subjunctive, and affirmative/negative imperative
  when available. Pronouns use tú/vosotros. Explicit supplementary regular
  paradigms and selected pronominal adaptations are labelled; the latter show
  seven tenses and omit imperatives. Missing forms are never guessed silently.
- Ten-card sessions prioritize due reviews and then new cards. Ratings schedule
  another attempt in ten minutes, one day, or increasing intervals. Mistakes can
  be retried immediately. This is self-assessed recall, not an automatic exam.
- Progress is stored locally per browser/origin. Export/import transfers it to
  other devices or between the hosted and downloaded versions. Downloading a new
  HTML file does not synchronize progress. Voice playback uses only a locally
  installed Spanish speech voice and explains when no offline voice is available.

## Rebuild on this machine

The build reads the local Ke OCR index, Vitamina A2 Spanish–English glossary PDF,
existing reviewed vocabulary, and an attributed verb database. It does not copy
PDFs into the static folder. It does not modify the ¡Vamos! frontend or APK.

```bash
./bin/pip install --target /tmp/espanol-flashcard-pdf -r standalone/flashcards/requirements-build.txt
curl -fsSL https://raw.githubusercontent.com/ghidinelli/fred-jehle-spanish-verbs/master/jehle_verb_database.csv -o /tmp/espanol-jehle-verbs.csv
curl -fsSL https://raw.githubusercontent.com/ghidinelli/fred-jehle-spanish-verbs/master/license.txt -o /tmp/espanol-jehle-license.txt
PYTHONPATH=/tmp/espanol-flashcard-pdf ./bin/python standalone/flashcards/build.py
```

The build generates both HTML versions, manifest, service worker, icons, licence
and `data-audit.json`. A content hash versions the offline cache. The source books
and generated deck are local deployment data and are not committed to this repo.

## Verification

```bash
node standalone/flashcards/verify.cjs
node standalone/flashcards/verify-web.cjs
```

These machine-specific Playwright checks test direct-file use with networking
disabled, sessions, retries, conjugations, keyboard actions, persistence,
export/import, mobile layout, and the real LAN HTTPS site's offline reload.
The HTTPS check ignores the local test browser's certificate errors; ordinary
users need to trust the existing LAN certificate to install the web app.

## Attribution

Vocabulary references: the user's local SGEL Vitamina A2 glossary and Ke books.
Translations are compiled from those references and the existing curated banks.
Conjugation tables derive from [Fred Jehle's database, compiled by Brian
Ghidinelli](https://github.com/ghidinelli/fred-jehle-spanish-verbs), licensed
CC BY-NC-SA 3.0. Adaptations and attribution are included in the app and the verb
data remains subject to that licence. Supplementary paradigms are explicitly
labelled in the UI. The build dependency PyMuPDF is only used to extract PDF
text and render the app's own icon; it is not shipped or used by the offline app.
