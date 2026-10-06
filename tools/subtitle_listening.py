"""Select coherent, level-assessed subtitle excerpts and extract their source audio."""
from dataclasses import dataclass
from hashlib import sha256
import html
import json
from pathlib import Path
import re
import subprocess
import tempfile

from tools.subtitle_reading import TIMING, seconds, chat, object_schema

GUIDES = {
    'A2': 'Vocabulario cotidiano y frecuente, temas concretos y familiares, frases sencillas, conectores básicos. Prioriza la idea principal y hechos explícitos. Admite algunas palabras nuevas, nombres propios y términos de noticias si el contexto o el glosario ayudan. No exijas que cada palabra o verbo sea de A2.',
    'B1': 'Vocabulario frecuente sobre actualidad y vida cotidiana, narración clara, causas y opiniones explícitas. Puede incluir pasado y futuro, algunas frases complejas y palabras menos frecuentes explicables con el contexto o glosario. Evalúa la comprensión global, no cada palabra por separado.',
    'B2': 'Actualidad, argumentos, contrastes, matices y subordinación. Admite vocabulario abstracto y algunas expresiones idiomáticas, pero no discurso muy especializado o implícito de C1/C2.',
}
PREFERRED_WPM = {'A2': 170, 'B1': 195, 'B2': 230}
STAMP = re.compile(r'<((?:\d+:)?\d{2}:\d{2}[.,]\d{3})>')
ENDING = re.compile(r'[.!?][»”"\')\]]*$')


class NoSuitableClip(ValueError):
    """The available subtitles contain no accepted standalone clip for this level."""


@dataclass
class Word:
    text: str
    start: float
    end: float


def subtitle_sentences(raw):
    """Preserve words/timing while removing repeated rolling-caption prefixes.

    Inline word timestamps permit sentence cuts inside a cue. For coarse SRT
    cues, only cut at cue boundaries, never estimate timing from character count.
    """
    words = []
    previous_end = None
    rolling = raw.lstrip('\ufeff\r\n ').startswith('WEBVTT')
    # Some downloaded VTTs have blank spacer lines *inside* a cue. Split at
    # timing lines, not blank lines, or the first spoken words lose their times.
    raw = raw.replace('\r', '').lstrip('\ufeff')
    timings = list(TIMING.finditer(raw))
    for index, timing in enumerate(timings):
        start, end = seconds(timing['start']), seconds(timing['end'])
        if end <= start:
            continue
        payload_start = raw.find('\n', timing.end())
        if payload_start < 0:
            continue
        payload_end = timings[index + 1].start() if index + 1 < len(timings) else len(raw)
        payload = raw[payload_start:payload_end].strip()
        # SRT sequence numbers belong to the next timing line.
        payload = re.sub(r'\n\s*\d+\s*$', '', payload)
        chunks = STAMP.split(payload)
        additions = []
        cursor = start
        for i in range(0, len(chunks), 2):
            stop = seconds(chunks[i + 1]) if i + 1 < len(chunks) else end
            text = html.unescape(re.sub(r'<[^>]*>', '', chunks[i]))
            text = re.sub(r'\[(?:música|music|aplausos|applause)\]', '', text, flags=re.I)
            additions.extend(Word(token, cursor, max(cursor, stop)) for token in text.split())
            cursor = stop
        overlap = 0
        if rolling and previous_end is not None and start <= previous_end + .1:
            for size in range(min(len(words), len(additions)), 0, -1):
                if [w.text for w in words[-size:]] == [w.text for w in additions[:size]]:
                    overlap = size
                    break
        words.extend(additions[overlap:])
        previous_end = end
    sentences, current = [], []
    for i, word in enumerate(words):
        current.append(word)
        following = words[i + 1] if i + 1 < len(words) else None
        # Rolling cues often end a word after the next cue begins. Use the
        # next genuine word onset as the boundary, not the repeated caption.
        boundary = following.start if following and following.start > word.start else word.end
        safe_cut = following is None or following.start >= word.end or following.start > word.start
        if ENDING.search(word.text) and safe_cut:
            sentences.append({'id': len(sentences), 'start': current[0].start,
                              'end': boundary, 'text': ' '.join(w.text for w in current)})
            current = []
    # A dangling final sentence is deliberately not eligible.
    return sentences


def candidate_windows(sentences, budget=3000):
    """Overlapping windows retain surrounding context for the selector."""
    index = 0
    while index < len(sentences):
        window = []
        for sentence in sentences[index:]:
            if sentence['end'] - sentences[index]['start'] > 180:
                break
            trial = window + [sentence]
            if len(json.dumps(trial, ensure_ascii=False).encode()) > budget:
                break
            window = trial
        if window:
            yield window
        index += max(1, len(window) // 2)


def clip_from_selection(value, window, level):
    if type(value.get('accepted')) is not bool:
        raise ValueError('accepted must be boolean')
    for key in ('reason', 'vocabulary', 'grammar', 'completeness'):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ValueError('Missing assessment: ' + key)
    if not value['accepted']:
        return None
    start, end = value.get('first'), value.get('last')
    if type(start) is not int or type(end) is not int:
        raise ValueError('Sentence IDs must be integers')
    selected = [s for s in window if start <= s['id'] <= end]
    if not selected or selected[0]['id'] != start or selected[-1]['id'] != end:
        raise ValueError(f'Select existing IDs {window[0]["id"]}–{window[-1]["id"]}, first <= last; use accepted=false if none fit')
    text = ' '.join(s['text'] for s in selected)
    duration = selected[-1]['end'] - selected[0]['start']
    count = len(text.split())
    if not 50 <= count <= 300 or not 15 <= duration <= 180:
        raise ValueError('Select 50–300 words, 15–180 seconds, with complete content')
    pace = count * 60 / duration
    return {'reading': text, 'start': selected[0]['start'], 'duration': duration,
            'audio_kind': 'original', 'level_assessment': {
                **{k: value[k] for k in ('reason', 'vocabulary', 'grammar', 'completeness')},
                'words_per_minute': round(pace, 1), 'method': 'local-model', 'level': level}}


def select_clip(raw, args, progress=lambda stage: None):
    if args.level not in GUIDES:
        raise ValueError('Original clips support A2, B1 and B2')
    for index, window in enumerate(candidate_windows(subtitle_sentences(raw), budget=2200), 1):
        # Do arithmetic and range validation in code. The model chooses only
        # between valid ranges and evaluates language/content, not timestamps.
        choices = {}
        for first in window:
            for last in window:
                trial = dict(accepted=True, first=first['id'], last=last['id'],
                             reason='pending', vocabulary='pending', grammar='pending', completeness='pending')
                try:
                    clip = clip_from_selection(trial, window, args.level)
                except ValueError:
                    continue
                choices[f"{first['id']}:{last['id']}"] = {
                    'words': len(clip['reading'].split()), 'seconds': round(clip['duration'], 2),
                    'wpm': clip['level_assessment']['words_per_minute']}
        if not choices:
            continue
        # Bound prompt overhead; sample ranges throughout this overlapping window.
        keys = list(choices)
        if len(keys) > 20:
            keys = [keys[round(i * (len(keys) - 1) / 19)] for i in range(20)]
            choices = {key: choices[key] for key in keys}
        brief = {'type': 'string', 'minLength': 1, 'maxLength': 160}
        schema = object_schema({'range': {'type': 'string', 'enum': ['none', *choices]},
                                'reason': brief, 'vocabulary': brief, 'grammar': brief, 'completeness': brief})
        def selected(value):
            key = value.get('range')
            if key != 'none' and key not in choices:
                raise ValueError('Choose one of the supplied ranges, or none')
            first, last = map(int, key.split(':')) if key != 'none' else (0, 0)
            return clip_from_selection(dict(value, accepted=key != 'none', first=first, last=last), window, args.level)
        progress(f'Evaluando fragmento {index} para {args.level}')
        result = chat(args,
            f'Selecciona un fragmento CONTIGUO de audio original apto para {args.level}. {GUIDES[args.level]} '
            'Elige range de la lista ranges (IDs de primera:última frase, ambos incluidos); '
            'los rangos ya cumplen límites de longitud. '
            f'Prefiere un ritmo cercano a {PREFERRED_WPM[args.level]} palabras/minuto, sin rechazar solo por velocidad; se puede repetir o escuchar más lento. '
            'Sé flexible con el nivel: basta comprender la idea principal con contexto y un pequeño glosario. '
            'Admite algunas palabras o estructuras más difíciles. Debe ser una unidad completa: '
            'introduce quién o qué se trata, desarrolla una idea y termina esa idea. Rechaza referencias sin antecedente, '
            'introducciones cortadas y frases incompletas. Una noticia sobre una decisión futura puede ser una idea completa. '
            'Escoge el fragmento más accesible que sirva para practicar el nivel. No reescribas ni inventes contenido. '
            'range="none" solo si todos son claramente incomprensibles para este nivel o están incompletos. '
            'Explica reason, vocabulary (palabras para el glosario), grammar y completeness en UNA frase corta por campo, máximo 160 caracteres cada uno.',
            json.dumps({'sentences': window, 'ranges': choices}, ensure_ascii=False),
            selected, schema, max_tokens=700)
        clip = selected(result)
        if clip:
            # Independently assess the exact isolated excerpt, without surrounding
            # text which might hide an unresolved reference or incomplete idea.
            def validate_review(value):
                if type(value.get('suitable')) is not bool:
                    raise ValueError('suitable must be boolean')
                if not isinstance(value.get('reason'), str) or not value['reason'].strip():
                    raise ValueError('Explain review decision')
            review = chat(args,
                'Comprueba solo si este fragmento contiene una idea comprensible y completa. '
                'No vuelvas a evaluar el nivel, los tiempos verbales ni palabras difíciles. '
                'Una decisión futura o una historia en curso no implica que el fragmento esté incompleto. '
                'suitable=false solo si falta contexto esencial o se corta una frase o idea. '
                'Devuelve suitable y reason en una sola frase corta (máximo 160 caracteres); no reescribas el fragmento.', clip['reading'], validate_review,
                object_schema({'suitable': {'type': 'boolean'}, 'reason': brief}), max_tokens=400)
            if review['suitable']:
                clip['level_assessment']['isolated_review'] = review['reason']
                return clip
    raise NoSuitableClip(f'No complete original excerpt suitable for {args.level}')


def extract_audio(video, directory, pack):
    """Accurate decoded audio cut; publish only a verified, complete MP3."""
    video, directory = Path(video).resolve(), Path(directory)
    start, duration = float(pack['start']), float(pack['duration'])
    if start < 0 or not 15 <= duration <= 180:
        raise ValueError('Invalid clip time range')
    signature = {'source': str(video), 'size': video.stat().st_size,
                 'mtime_ns': video.stat().st_mtime_ns, 'start': start, 'duration': duration,
                 'transcript': pack['reading']}
    digest = sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
    target, metadata = directory / 'lectura.mp3', directory / 'audio.json'
    if target.is_file() and target.stat().st_size and metadata.is_file():
        if json.loads(metadata.read_text()).get('source_hash') == digest:
            return
    with tempfile.TemporaryDirectory(prefix='.clip-', dir=directory) as temporary:
        temporary = Path(temporary)
        mp3 = temporary / 'lectura.mp3'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(video),
                        '-ss', str(start), '-t', str(duration), '-map', '0:a:0', '-vn',
                        '-codec:a', 'libmp3lame', '-b:a', '96k', '-threads', '1', str(mp3)],
                       check=True, capture_output=True, timeout=180)
        probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'json', str(mp3)], check=True, capture_output=True, text=True, timeout=15)
        actual = float(json.loads(probe.stdout)['format']['duration'])
        if abs(actual - duration) > .3 or mp3.stat().st_size == 0:
            raise ValueError('Source audio does not cover the complete selected excerpt')
        result = {'source_hash': digest, 'audio_kind': 'original', 'start': start,
                  'duration_seconds': round(actual, 3), 'engine': 'ffmpeg',
                  'source': pack.get('source', video.name)}
        (temporary / 'audio.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        (temporary / 'audio-credits.txt').write_text(
            f"Original source audio: {result['source']}\nExcerpt: {start:.3f}–{start + duration:.3f} seconds.\n"
            'Transcript comes from source subtitles and may contain recognition errors.\n')
        mp3.replace(target)
        (temporary / 'audio.json').replace(metadata)
        (temporary / 'audio-credits.txt').replace(directory / 'audio-credits.txt')
