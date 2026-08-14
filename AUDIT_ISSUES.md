# UI and functionality audit

Audited 2026-08-14. Scope: React routes and controls, their API wiring, and responsive behavior inferred from the implemented breakpoints/layout. I also ran the repository's automated checks. This is an audit only; no product code was changed.

## Summary

- No literal `Link`/`NavLink` target points to a missing React route.
- One implemented page is unreachable through the UI.
- Several media controls look complete but do not behave as their labels imply.
- The general layout should reflow at common phone widths, but the fixed mobile chrome has safe-area, overlap, truncation, and touch-target problems.
- Some copy is clearly placeholder/demo copy. It is listed separately where the UI presents it as live personalized information.

## Functional and navigation issues

### High — Conversation hides microphone failures

`useRecorder` provides actionable errors for denied permission, missing `MediaRecorder`, and unavailable hardware (`frontend/src/hooks/useRecorder.ts:41-73`). `Conversacion` does not read the hook's `error` value (`frontend/src/pages/Conversacion.tsx:16`) and continues to show “Toca y responde en español” (`frontend/src/pages/Conversacion.tsx:53`). On a phone with denied microphone permission or an insecure HTTP origin, tapping the microphone appears to do nothing and gives no recovery instructions.

Recommended: destructure the recorder error and render it next to the microphone; change the prompt/button state when recording is unavailable.

### Medium — Audio timeline and seeking use a fake 18-second duration

`AudioPlayer` fixes `duration` to the `durationSeconds` prop, whose default is 18 seconds (`frontend/src/components/AudioPlayer.tsx:21-26`). It never reads the real audio element's metadata (`frontend/src/components/AudioPlayer.tsx:61-66`). The displayed total, waveform progress, and tap-to-seek calculation are therefore wrong for every real clip that is not exactly 18 seconds.

Recommended: store duration in state and update it from `audio.duration` on `loadedmetadata`/`durationchange`.

### Medium — “CC” is not real captioning

The video player receives one string and displays that same string for the entire video (`frontend/src/components/VideoPlayer.tsx:110-115`). The “CC” control only hides/shows this static overlay (`frontend/src/components/VideoPlayer.tsx:149`). On the lesson page this is always the first transcript line. Users will reasonably expect synchronized captions, particularly in a language-learning app.

Recommended: provide timed cues (for example WebVTT/SRT converted to `<track>`) or rename the control/content as a non-synchronized phrase prompt.

### Medium — Groups exists but has no link anywhere

`/grupos` is registered (`frontend/src/App.tsx:42`) and the page contains working create/join/encourage controls, but it is absent from both desktop and mobile navigation (`frontend/src/components/Sidebar.tsx:6-13`) and no other component links to it. A user cannot discover the feature without manually entering the URL.

Recommended: add an intentional entry point, or remove/mark the page as an internal placeholder until it is ready.

### Medium — Fullscreen can silently do nothing

The fullscreen button calls `requestFullscreen()` on a wrapper without checking support or handling rejection (`frontend/src/components/VideoPlayer.tsx:150`). This is not consistently available for arbitrary elements on mobile browsers, notably iPhone Safari, and a failed promise produces no user feedback.

Recommended: feature-detect fullscreen, prefer video-native fullscreen where required, hide/disable the control when unsupported, and handle rejection.

### Low — Practice submissions can be duplicated

The quick-practice page has no pending/submitting state. “Comprobar” remains enabled while `submitAttempt` is in flight (`frontend/src/pages/Practica.tsx:85`), so repeated taps can record multiple attempts and apply progress more than once.

Recommended: disable the answer controls and submit button while awaiting the API, as the assessment page already does.

### Low — Profile failures are shown as success

Both success and failure strings share the same `message` state, but the status is always green (`text-leaf`) at `frontend/src/pages/Perfil.tsx:61`. “No se pudo guardar” therefore looks like a successful save.

Recommended: keep separate success/error state and use error styling plus `role="alert"` for failures.

## Phone and responsive-layout issues

### Medium — Fixed mobile header does not account for the top safe area

The header is fixed at `top-0` with a hard 56 px height (`frontend/src/components/AppLayout.tsx:11`), with no `env(safe-area-inset-top)`. The viewport declaration also omits `viewport-fit=cover` (`frontend/index.html:6`). In an edge-to-edge webview or notched phone layout, system chrome may overlap the logo and controls.

Recommended: define a safe-area-aware header height/padding and matching main-content top padding; add the appropriate viewport configuration after testing the Android wrapper and iOS browsers.

### Medium — Bottom clearance is not tied to the actual bottom-nav height

The bottom navigation adds `safe-area-inset-bottom` to itself (`frontend/src/components/Sidebar.tsx:69`), but page clearance remains the fixed `pb-20` (`frontend/src/components/AppLayout.tsx:15`). On devices with a large bottom inset, the last page content can sit behind the taller nav. The conversation recorder is similarly fixed at `bottom-16` (`frontend/src/pages/Conversacion.tsx:53`) rather than the nav's real height plus safe area.

Recommended: define shared CSS variables for header/nav heights including safe-area insets and use them for page padding and sticky/fixed controls.

### Medium — Floating lesson button can cover the real lesson actions

On phones, `Leccion` renders both the normal end-of-page “Conversar”/“Empezar la práctica” actions and a fixed “Conversar” pill (`frontend/src/pages/Leccion.tsx:65-66`). The page has no extra local bottom clearance for that pill. Near the bottom, it can obscure one of the real action buttons or challenge content.

Recommended: remove the duplicate floating action at the bottom of the page, hide it when the normal actions are visible, or reserve enough space for it.

### Low — Six bottom-nav items are cramped and below comfortable touch size

At 320 px wide, six equal columns are only about 53 px wide. Each link uses 10 px text, truncates labels, and has only `py-1` around a 20 px icon (`frontend/src/components/Sidebar.tsx:69-74`), yielding a control substantially shorter than the commonly recommended 44 px touch target. “Lecciones” and “Conversar” are likely to truncate on narrow phones or with larger text settings.

Recommended: use fewer primary tabs with a “More” destination, shorten labels, and enforce at least a 44×44 px hit area.

### Low — Mobile video has no mute control

The volume/mute button is explicitly hidden below the `sm` breakpoint (`frontend/src/components/VideoPlayer.tsx:127`). The custom player also suppresses native controls, so phone users have no in-player audio toggle.

Recommended: retain a compact mute button on mobile or expose native controls.

## Placeholder or misleading live copy

These may be intentional placeholders, but they currently look like calculated/personalized facts:

1. The assessment always says the learner needs future-tense and plans practice and always shows the same three concept chips, regardless of lesson or answers (`frontend/src/pages/Assessment.tsx:332-348`).
2. The assessment says “Nuevas lecciones se añaden automáticamente” (`frontend/src/pages/Assessment.tsx:409`), while the README says publication belongs to a separate worker and this scaffold deliberately does not publish files automatically (`README.md:89-93`). This is directly contradictory.
3. The route page always labels a clip as `00:42` (`frontend/src/pages/MiRuta.tsx:93-95`) even though the video player reads the real media duration.
4. The home page always promises an approximately 12-minute session (`frontend/src/pages/Inicio.tsx:27-29`) without calculating it from the current lesson.
5. While progress is loading, the route header displays a fallback “12 días” as if it were the user's real streak (`frontend/src/pages/MiRuta.tsx:73-76`). A loading placeholder such as “–” would avoid presenting false progress.
6. The video and audio components intentionally simulate playback when no media URL exists. That is useful in explicit mock/demo mode, but production data with a missing URL would show a working-looking fake player instead of a missing-media error (`frontend/src/components/VideoPlayer.tsx:36-49`, `frontend/src/components/AudioPlayer.tsx:28-40`).

## What appears sound

- All literal application links map to declared routes; unknown URLs redirect to the authenticated home flow.
- Buttons for authentication, placement, route progression, lesson selection, assessments, profile updates, groups, recording, speech examples, theme, and logout have handlers or form submissions.
- The primary content layouts use single-column phone defaults and introduce multi-column layouts only at `sm`, `lg`, or `xl`; no obvious fixed-width content panel forces general horizontal scrolling.
- Bottom navigation accounts for the bottom safe area within the nav itself, and the lesson floating conversation button does too.

## Verification performed

- `npm run lint` — passed.
- `npm run build` — passed (TypeScript and Vite production build).
- Backend test suite — 43 passed. The suite emitted 1,531 deprecation warnings, mostly from naive `datetime.utcnow()` use; these are maintenance warnings rather than current UI failures.
- Static route/control/API trace across `frontend/src` and relevant backend routers.

## Audit limitation

No browser automation runtime was installed in this workspace, so phone findings are code/layout-based rather than screenshots from a device matrix. Before release, manually test at 320×568, 360×800, 390×844, and 412×915; include Android gesture navigation, large font/display scaling, denied microphone permission, slow/offline media, landscape orientation, and a real iPhone Safari session if the web build supports iOS users.
