"""Fetch real YouTube clips for the C1/C2 companion units and emit video lessons.

For each unit, resolves candidate queries with yt-dlp's ``ytsearch``, downloads
the best match (max 720p, preferably under ~15 min) into ``content/sources/``,
transcribes it with faster-whisper, picks a clean contiguous 40-60s window and
emits ``video_lessons_c.py`` with lesson dicts in exactly the shape
``video_content.py`` produces (``generate_media`` re-cuts the clip from the
stored ``source_video`` window at seed time; this script also writes a preview
cut to ``content/seed/<slug>/video.mp4`` so the clip can be reviewed directly).

Run from the project root:

    ./bin/python -m backend.app.seed.video_fetch [--only SLUG ...] [--limit N]
"""

import argparse
import hashlib
import json
import pprint
import random
import re
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

from ..config import settings
from .curriculum_content import SPECS

PROJECT_ROOT = Path(__file__).resolve().parents[3]
YTDLP = PROJECT_ROOT / "bin" / "yt-dlp"
SOURCES_DIR = Path(settings.content_dir) / "sources"
SEED_DIR = Path(settings.content_dir) / "seed"
OUT_MODULE = Path(__file__).with_name("video_lessons_c.py")
REPORT = SOURCES_DIR / "fetch_report.json"

WINDOW_MIN, WINDOW_MAX = 40.0, 60.0
MIN_WORDS = 70  # a 40-60s window of natural speech should carry ~90+ words

WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")
STOPWORDS = {
    "porque", "cuando", "entonces", "también", "siempre", "ahora", "después",
    "mientras", "aunque", "contra", "entre", "hasta", "desde", "donde",
    "nuestro", "nuestra", "nosotros", "ustedes", "ellos", "ellas", "estaba",
    "estamos", "tenemos", "tener", "hacer", "puede", "pueden", "todavía",
    "mismo", "misma", "mucho", "mucha", "todos", "todas", "sobre", "quiero",
}

# Per unit slug: 2-4 ytsearch queries (or direct URLs) for advanced, natural
# Spain-Spanish content matching the unit theme.
CANDIDATES: dict[str, list[str]] = {
    "companion-c1-individuo": [
        "entrevista psicólogo personalidad identidad España",
        "documental la personalidad se hereda o se construye",
        "charla identidad personal psicología español",
    ],
    "companion-c1-tiempo-libre": [
        "documental ocio y tiempo libre en España rtve",
        "reportaje aficiones de los españoles",
        "debate conciliación trabajo tiempo libre España",
    ],
    "companion-c1-mundo-laboral": [
        "reportaje mercado laboral España rtve",
        "documental futuro del trabajo en España",
        "entrevista experto empleo reestructuración empresas españolas",
    ],
    "companion-c1-experiencia-gastronomica": [
        "documental gastronomía española rtve",
        "reportaje bares de barrio cocina tradicional española",
        "entrevista chef español cocina de autor",
    ],
    "companion-c1-alternativas-ambientales": [
        "documental transición energética España rtve",
        "reportaje huertos urbanos España",
        "reportaje reciclaje vertederos medio ambiente España",
    ],
    "companion-c1-educacion": [
        "debate sistema educativo español",
        "documental educación en España rtve",
        "entrevista profesor innovación educativa España",
    ],
    "companion-c1-paisajes-urbanos": [
        "documental urbanismo ciudades españolas rtve",
        "reportaje transformación de barrios Madrid",
        "documental arquitectura y vida urbana España",
    ],
    "companion-c1-geografias-y-viajes": [
        "documental viajar por España rtve",
        "reportaje turismo rural España",
        "documental paisajes y geografías de España",
    ],
    "companion-c1-deporte-y-bienestar": [
        "documental deporte y salud rtve España",
        "reportaje entrenamiento bienestar vida saludable España",
        "entrevista atleta español maratón lesión",
    ],
    "companion-c1-economia-y-negocios": [
        "reportaje economía española pequeños comercios rtve",
        "entrevista economista español inflación",
        "documental emprendedores negocios España",
    ],
    "companion-c1-palabras": [
        "RAE nuevas palabras español entrevista",
        "documental historia del idioma español rtve",
        "reportaje préstamos del inglés en el español",
    ],
    "companion-c1-siglo-xxi": [
        "documental tecnología y sociedad rtve España",
        "debate impacto de las redes sociales España",
        "reportaje desconexión digital españoles",
    ],
    "companion-c2-retorica-y-debate": [
        "torneo de debate universitario España final",
        "debate político rtve cara a cara",
        "charla arte de la retórica argumentación español",
    ],
    "companion-c2-lengua-y-sociedad": [
        "documental lenguas de España diversidad lingüística",
        "reportaje lenguas minoritarias España transmisión",
        "entrevista sociolingüista español norma y variedades",
    ],
    "companion-c2-ciencia-y-divulgacion": [
        "entrevista divulgador científico español",
        "documental investigación científica España rtve",
        "charla divulgación científica rigor España",
    ],
    "companion-c2-literatura": [
        "Página Dos TVE entrevista escritor español",
        "Entrevista a Luis Landero en Página Dos de TVE",
        "entrevista escritor español novela literatura",
    ],
    "companion-c2-medios-y-opinion": [
        "debate medios de comunicación y opinión pública España",
        "documental periodismo en España rtve",
        "reportaje desinformación medios españoles",
    ],
    "companion-c2-memoria-historica": [
        "documental memoria histórica España rtve",
        "reportaje recuperación de la memoria histórica",
        "entrevista historiador memoria histórica España",
    ],
    "companion-c2-humor-e-ironia": [
        "entrevista humorista español ironía",
        "documental historia del humor en España",
        "monólogo humor español con público",
    ],
    "companion-c2-lenguaje-administrativo": [
        "lenguaje claro administración pública España",
        "reportaje trámites burocracia administración española rtve",
        "plazos días hábiles recurso administrativo abogado explica",
    ],
    "companion-c2-identidades": [
        "documental identidad cultural España rtve",
        "entrevista entre dos culturas identidad español",
        "reportaje identidades culturales raíces España",
    ],
    "companion-c2-el-siglo-digital": [
        "documental inteligencia artificial sociedad rtve España",
        "debate algoritmos y sociedad español",
        "reportaje sociedad digital atención España",
    ],
}

# Fallback listening distractors used when fewer than two other units have a
# transcript to borrow lines from. They are deliberately generic.
FALLBACK_DISTRACTORS = [
    "Mañana lloverá con fuerza en toda la península.",
    "El partido terminó con un empate a dos goles.",
    "La receta lleva harina, huevos y un poco de azúcar.",
    "El tren de las ocho llega con veinte minutos de retraso.",
]


def log(msg: str) -> None:
    print(f"[video_fetch {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def ytsearch(query: str, limit: int = 8) -> list[tuple[str, float, str]]:
    """Resolve a query (or return a direct URL) to (url, duration, title)."""
    if query.startswith("http"):
        return [(query, 0.0, "")]
    proc = _run(
        [str(YTDLP), f"ytsearch{limit}:{query}", "--flat-playlist", "--no-warnings",
         "--print", "%(id)s\t%(duration)s\t%(title)s"],
        timeout=180,
    )
    if proc.returncode != 0:
        log(f"  search failed for {query!r}: {proc.stderr.strip()[:200]}")
        return []
    results = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            duration = float(parts[1])
        except ValueError:
            continue  # duration "NA"
        results.append((f"https://www.youtube.com/watch?v={parts[0]}", duration, parts[2]))
    return results


def _media_files(dest_base: Path) -> list[Path]:
    """Downloaded files for a unit, including yt-dlp partial/merge artefacts."""
    return [
        p for p in sorted(dest_base.parent.glob(dest_base.name + ".*"))
        if p.suffix in {".mp4", ".webm", ".mkv", ".m4a", ".part", ".ytdl"}
    ]


def _has_av_streams(path: Path) -> bool:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    kinds = set(proc.stdout.split())
    return {"video", "audio"} <= kinds


def download(url: str, dest_base: Path) -> Path | None:
    """Download max-720p video; returns the downloaded file path or None."""
    template = f"{dest_base}.%(ext)s"
    attempts = [
        [],
        ["--extractor-args", "youtube:player_client=android,web"],
    ]
    for extra in attempts:
        # Drop partials left by the previous attempt (failed merges leave
        # audio-only *.f251.webm style files that must not be picked up).
        for stale in _media_files(dest_base):
            stale.unlink()
        proc = _run(
            [str(YTDLP), url, "-f", "bv*[height<=720]+ba/b[height<=720]/b",
             "--merge-output-format", "mp4", "--no-playlist", "--no-warnings",
             "--retries", "2", "-o", template, *extra],
            timeout=900,
        )
        if proc.returncode == 0:
            for candidate in _media_files(dest_base):
                if candidate.suffix in {".mp4", ".webm", ".mkv"} and _has_av_streams(candidate):
                    return candidate
        log(f"  download attempt failed ({url}): {proc.stderr.strip()[-200:]}")
        time.sleep(3)
    return None


def load_model(name: str):
    from faster_whisper import WhisperModel

    log(f"loading whisper model {name!r} (downloads to ~/.cache on first use)")
    return WhisperModel(name, device="cpu", compute_type="int8", cpu_threads=4)


def _source_sha256(video: Path) -> str:
    digest = hashlib.sha256()
    with video.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cached_transcript(cache: Path, source_hash: str) -> list[dict[str, Any]] | None:
    if cache.exists():
        cached = json.loads(cache.read_text())
        if isinstance(cached, dict) and cached.get("source_sha256") == source_hash:
            return cached.get("segments", [])
    return None


def transcribe(video: Path, cache: Path, model) -> list[dict[str, Any]]:
    source_hash = _source_sha256(video)
    cached = _cached_transcript(cache, source_hash)
    if cached is not None:
        return cached
    wav = video.with_suffix(".audio.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
         "-vn", "-ac", "1", "-ar", "16000", str(wav)],
        check=True,
    )
    segments, _info = model.transcribe(str(wav), language="es", beam_size=5, vad_filter=True)
    data = [
        {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
         "avg_logprob": s.avg_logprob, "no_speech_prob": s.no_speech_prob}
        for s in segments
    ]
    wav.unlink(missing_ok=True)
    cache.write_text(json.dumps(
        {"source_sha256": source_hash, "segments": data}, ensure_ascii=False, indent=1
    ))
    return data


def pick_window(segments: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Pick the cleanest contiguous 40-60s window of whisper segments."""
    best: tuple[float, int, int] | None = None
    for i in range(len(segments)):
        for j in range(i + 2, len(segments) + 1):
            duration = segments[j - 1]["end"] - segments[i]["start"]
            if duration > WINDOW_MAX:
                break
            if duration < WINDOW_MIN:
                continue
            window = segments[i:j]
            text = " ".join(s["text"] for s in window)
            if "♪" in text:
                continue
            words = len(text.split())
            if words < MIN_WORDS:
                continue
            score = (
                statistics.mean(s["avg_logprob"] for s in window)
                - 0.5 * statistics.mean(s["no_speech_prob"] for s in window)
                + 0.002 * words
            )
            if best is None or score > best[0]:
                best = (score, i, j)
    if best is None:
        return None
    _, i, j = best
    window = segments[i:j]
    return {
        "start": round(window[0]["start"], 2),
        "end": round(window[-1]["end"], 2),
        "segments": window,
    }


def cut_preview(source: Path, start: float, end: float, out: Path) -> None:
    """Cut the chosen window with exactly the ffmpeg flags generate_media uses."""
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-ss", str(start), "-t", str(end - start), "-i", str(source),
         "-map", "0:v:0", "-map", "0:a:0",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         str(out)],
        check=True,
    )


def _chunks(items: list, n: int) -> list[list]:
    base, extra = divmod(len(items), n)
    out, idx = [], 0
    for k in range(n):
        size = base + (1 if k < extra else 0)
        out.append(items[idx:idx + size])
        idx += size
    return [chunk for chunk in out if chunk]


def _words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def _pick_vocab(segments: list[dict[str, Any]]) -> tuple[str, str, list[str]]:
    """Pick a content word; returns (prompt_with_blank, answer, options)."""
    candidates: list[tuple[str, str]] = []  # (line, word)
    for seg in segments:
        for word in _words(seg["text"]):
            if len(word) >= 7 and word.lower() not in STOPWORDS:
                candidates.append((seg["text"], word))
    if not candidates:
        raise ValueError("no vocabulary word found")
    # Longest word first; prefer one from a mid-window line.
    candidates.sort(key=lambda pair: len(pair[1]), reverse=True)
    line, word = candidates[0]
    prompt = line.replace(word, "_____", 1)
    pool = [
        w for seg in segments for w in _words(seg["text"])
        if len(w) >= 6 and w.lower() != word.lower()
    ]
    seen: set[str] = set()
    distractors: list[str] = []
    for w in pool:
        if w.lower() not in seen:
            seen.add(w.lower())
            distractors.append(w)
        if len(distractors) == 2:
            break
    options = [word, *distractors]
    random.Random(f"vocab-{line}").shuffle(options)
    return prompt, word, options


def _pick_line(segments: list[dict[str, Any]], min_w: int, max_w: int, avoid: set[str]) -> str:
    """Pick a verbatim line; long whisper segments are split into chunks."""
    lines: list[str] = []
    for seg in segments:
        words = seg["text"].split()
        if min_w <= len(words) <= max_w:
            lines.append(seg["text"])
        elif len(words) > max_w:
            for i in range(0, len(words), max_w - 1):
                chunk = " ".join(words[i:i + max_w])
                if min_w <= len(chunk.split()) <= max_w:
                    lines.append(chunk)
    lines = [l for l in lines if l not in avoid]
    if not lines:
        raise ValueError("no usable line found")
    lines.sort(key=len)
    return lines[len(lines) // 2]


def build_lesson(spec: dict[str, Any], window: dict[str, Any], source: Path,
                 other_lines: list[str]) -> dict[str, Any]:
    slug = spec["slug"].replace("companion-", "video-", 1)
    start, end = window["start"], window["end"]
    whisper_segs = window["segments"]
    group_count = max(3, min(5, round(len(whisper_segs) / 2)))
    segments = [
        {
            "start": round(group[0]["start"] - start, 2),
            "end": round(group[-1]["end"] - start, 2),
            "transcript": [{"es": s["text"], "en": ""} for s in group],
            "phrases": [],
        }
        for group in _chunks(whisper_segs, group_count)
    ]

    exercises: list[dict[str, Any]] = []
    try:
        prompt, word, options = _pick_vocab(whisper_segs)
        exercises.append({
            "type": "vocabulary", "instructions": "Completa la frase del vídeo.",
            "prompt": prompt, "options": options, "expected_answer": word,
            "skill_weights": {"vocabulary": 1.0},
        })
    except ValueError:
        log(f"  {slug}: no vocabulary exercise could be built")

    used: set[str] = set()
    try:
        listen_line = _pick_line(whisper_segs, 5, 14, used)
        used.add(listen_line)
        distractors = [l for l in other_lines if l != listen_line][:2]
        distractors += [d for d in FALLBACK_DISTRACTORS if len(distractors) < 2]
        options = [listen_line, *distractors[:2]]
        random.Random(f"listen-{slug}").shuffle(options)
        exercises.append({
            "type": "listening", "instructions": "Escucha y elige.",
            "prompt": "¿Cuál de estas frases se escucha en el vídeo?",
            "options": options, "expected_answer": listen_line, "audio": True,
            "skill_weights": {"listening": 1.0},
        })
    except ValueError:
        log(f"  {slug}: no listening exercise could be built")

    try:
        repeat = _pick_line(whisper_segs, 3, 9, used)
        exercises.append({
            "type": "pronunciation", "instructions": "Escucha y repite.",
            "prompt": f"Repite: {repeat}", "options": None, "expected_answer": repeat,
            "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5},
        })
    except ValueError:
        log(f"  {slug}: no pronunciation exercise could be built")

    return {
        "slug": slug, "title": f"{spec['title']} · Vídeo",
        "cefr_level": spec["level"], "topics": list(spec["topics"]),
        "source": "video-library", "status": "published",
        # Relative to the content dir (portable); load.py resolves it at seed time.
        "source_video": {"path": f"sources/{source.name}", "start": start, "end": end},
        "grammar_tip": {
            "wrong": spec["wrong"], "right": spec["right"],
            "explanation": spec["explanation"],
        },
        "segments": segments,
        "exercises": exercises,
    }


def process_unit(spec: dict[str, Any], model, deadline: float) -> tuple[dict[str, Any] | None, str | None]:
    """Search, download, transcribe and pick a window for one unit."""
    slug = spec["slug"]
    last_error = "no candidates"
    for query in CANDIDATES.get(slug, []):
        if time.time() > deadline:
            return None, "global deadline reached"
        results = ytsearch(query)
        usable = [(u, d, t) for u, d, t in results if 150 <= d <= 900]
        if not usable:
            last_error = f"no usable results for {query!r}"
            continue
        # Prefer videos of ~4-13 minutes.
        usable.sort(key=lambda item: abs(item[1] - 480))
        for url, duration, title in usable[:4]:
            log(f"  trying {title!r} ({duration:.0f}s) {url}")
            dest_base = SOURCES_DIR / slug
            for stale in SOURCES_DIR.glob(slug + ".*"):
                if stale.suffix != ".json":
                    stale.unlink()
            video = download(url, dest_base)
            if video is None:
                last_error = f"download failed for {url}"
                continue
            segments = transcribe(video, SOURCES_DIR / f"{slug}.transcript.json", model)
            window = pick_window(segments)
            if window is None:
                last_error = f"no clean 40-60s window in {title!r}"
                video.unlink(missing_ok=True)
                (SOURCES_DIR / f"{slug}.transcript.json").unlink(missing_ok=True)
                continue
            window.update({"url": url, "title": title, "file": video.name})
            return window, None
    return None, last_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", default=None, help="process only these unit slugs")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", default="base")
    parser.add_argument("--max-minutes", type=float, default=75.0)
    args = parser.parse_args()

    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    specs = [s for s in SPECS if s["slug"].startswith(("companion-c1-", "companion-c2-"))]
    if args.only:
        specs = [s for s in specs if s["slug"] in args.only]
    if args.limit:
        specs = specs[: args.limit]

    deadline = time.time() + args.max_minutes * 60
    windows: dict[str, dict[str, Any]] = {}
    failures: dict[str, str] = {}
    model = None
    for spec in specs:
        slug = spec["slug"]
        cache = SOURCES_DIR / f"{slug}.window.json"
        if cache.exists():
            log(f"{slug}: cached window found, skipping fetch")
            windows[slug] = json.loads(cache.read_text())
            continue
        if time.time() > deadline:
            failures[slug] = "global deadline reached"
            log(f"{slug}: skipped, global deadline reached")
            continue
        log(f"{slug}: searching ({spec['title']})")
        if model is None:
            model = load_model(args.model)
        try:
            window, error = process_unit(spec, model, deadline)
        except Exception as exc:  # keep going with the remaining units
            window, error = None, f"unexpected error: {exc}"
        if window is None:
            failures[slug] = error or "unknown failure"
            log(f"{slug}: FAILED - {failures[slug]}")
        else:
            try:
                cut_preview(
                    SOURCES_DIR / window["file"], window["start"], window["end"],
                    SEED_DIR / slug.replace("companion-", "video-", 1) / "video.mp4",
                )
            except Exception as exc:  # keep going with the remaining units
                failures[slug] = f"preview cut failed: {exc}"
                log(f"{slug}: FAILED - {failures[slug]}")
                continue
            cache.write_text(json.dumps(window, ensure_ascii=False, indent=1))
            windows[slug] = window
            log(f"{slug}: window {window['start']}-{window['end']}s from {window['title']!r}")

    # Distractors for the listening MC come from the other units' transcripts,
    # so they are natural Spanish lines guaranteed absent from this transcript.
    # Emit lessons for every unit with a cached window, not only the ones this
    # run processed, so --only runs never shrink the output module.
    lessons: list[dict[str, Any]] = []
    all_specs = [s for s in SPECS if s["slug"].startswith(("companion-c1-", "companion-c2-"))]
    for spec in all_specs:
        slug = spec["slug"]
        if slug not in windows:
            cache = SOURCES_DIR / f"{slug}.window.json"
            if cache.exists():
                windows[slug] = json.loads(cache.read_text())
        if slug not in windows:
            continue
        window = windows[slug]
        own = {s["text"] for s in window["segments"]}
        other_lines = [
            s["text"] for other, w in windows.items() if other != slug
            for s in w["segments"] if 5 <= len(s["text"].split()) <= 14 and s["text"] not in own
        ]
        lessons.append(build_lesson(spec, window, SOURCES_DIR / window["file"], other_lines))

    OUT_MODULE.write_text(
        '"""Real YouTube clips for the C1/C2 companion units.\n\n'
        "Generated by backend/app/seed/video_fetch.py; regenerate with:\n"
        "    ./bin/python -m backend.app.seed.video_fetch\n"
        '"""\n\nC_VIDEO_LESSONS = '
        + pprint.pformat(lessons, width=140, sort_dicts=False)
        + "\n"
    )
    REPORT.write_text(json.dumps(
        {"ok": sorted(windows), "failed": failures}, ensure_ascii=False, indent=1))
    log(f"done: {len(lessons)} lessons -> {OUT_MODULE}; failures: {json.dumps(failures, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
