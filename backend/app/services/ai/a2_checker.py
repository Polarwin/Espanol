"""Conservative A2 Unit 1 rules plus the existing correction provider.

Rules cover familiar, unambiguous constructions, not arbitrary Spanish syntax.
Offsets always address the original submission. Book evidence is retrieved,
never generated; model suggestions cannot change the targeted verb families.
"""
import re

from . import providers
from .. import textbook

NOUNS = {
    'idiomas': 'p', 'libros': 'p', 'deportes': 'p', 'conversaciones': 'p',
    'actividades': 'p', 'películas': 'p', 'noticias': 'p', 'clases': 'p',
    'palabras': 'p', 'ejercicios': 'p', 'viajes': 'p', 'lenguas': 'p',
    'idioma': 's', 'libro': 's', 'deporte': 's', 'conversación': 's',
    'actividad': 's', 'película': 's', 'clase': 's', 'vocabulario': 's',
    'gramática': 's', 'música': 's', 'fútbol': 's', 'español': 's',
    'pronunciación': 's', 'lectura': 's', 'cocina': 's',
}
INFINITIVES = 'aprender hablar entender practicar escuchar leer escribir cocinar correr estudiar bailar viajar conocer hacer tener ir salir repetir mejorar'.split()
FINITE = dict(zip(
    'aprendes hablas entiendes practicas escuchas lees escribes cocinas corres estudias bailas viajas conoces haces tienes vas sales repites mejoras'.split(), INFINITIVES))
SUBJUNCTIVE = dict(zip(FINITE, 'aprendas hables entiendas practiques escuches leas escribas cocines corras estudies bailes viajes conozcas hagas tengas vayas salgas repitas mejores'.split()))
AGREEMENT = re.compile(r'\b(?:me|te|le|nos|os|les)\s+(?:no\s+)?(?P<verb>gustan?|cuestan?)\s+(?P<body>[^.!?;:\n]+)', re.I)
ADVICE = re.compile(r'\b(?P<head>(?:te|le|os|les)\s+recomiendo(?:\s+que)?|puedes|hay\s+que)\s+(?P<verb>' + '|'.join(FINITE) + r')\b', re.I)
PROTECTED = re.compile(r'\b(?:gust\w*|cuest\w*|recomiend\w*|puedes|hay)\b', re.I)


def detect(text: str) -> list[dict]:
    issues = []

    def add(match, replacement, rule, explanation, query):
        old = match.group('verb')
        if old[0].isupper():
            replacement = replacement.capitalize()
        issues.append({'start': match.start('verb'), 'end': match.end('verb'),
                       'original': old, 'replacement': replacement, 'rule': rule,
                       'explanation': explanation, 'query': query})

    for match in AGREEMENT.finditer(text):
        body = match.group('body').lower().strip()
        # Coordinated/relative subjects require interpretation: abstain.
        if re.search(r'\b(y|e|o|u|ni|que|quien|quienes)\b|[,«»"“”]', body):
            continue
        words = body.split()
        if not words:
            continue
        number = None
        if words[0] in INFINITIVES:
            number = 's'
        elif len(words) >= 2 and words[0] in {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'}:
            number = NOUNS.get(words[1])
            article_number = 'p' if words[0] in {'los', 'las', 'unos', 'unas'} else 's'
            if number != article_number:
                continue
            # Only simple noun phrases and familiar modifiers are supported.
            if any(w not in {'rápidas', 'rápidos', 'difíciles', 'fáciles', 'nuevas', 'nuevos', 'español', 'españoles', 'españolas', 'de', 'en', 'muy'} for w in words[2:]):
                continue
        verb = match.group('verb').lower()
        wanted = ('gusta' if verb.startswith('gust') else 'cuesta') + ('n' if number == 'p' else '')
        if number and verb != wanted:
            subject = 'un infinitivo' if words[0] in INFINITIVES else ('un grupo en plural' if number == 'p' else 'un grupo en singular')
            add(match, wanted, 'agreement', f'La cosa o actividad es {subject}; aquí corresponde «{wanted}». El verbo concuerda con lo que gusta o cuesta, no con «me» o «te».', 'gustar' if verb.startswith('gust') else 'cuesta cuestan')

    for match in ADVICE.finditer(text):
        head = match.group('head').lower()
        verb = match.group('verb').lower()
        # Avoid ambiguous readings (e.g. "sales" can be a noun).
        if verb in {'viajas', 'tienes', 'vas', 'sales'} and 'recomiendo' in head:
            continue
        subj = head.endswith('que') and 'recomiendo' in head
        replacement = SUBJUNCTIVE[verb] if subj else FINITE[verb]
        explanation = ('Después de «te recomiendo que» usamos el subjuntivo: «que ' + replacement + '».') if subj else ('En esta estructura usamos el infinitivo: «' + head + ' ' + replacement + '».')
        add(match, replacement, 'advice', explanation, 'recomiendo' if 'recomiendo' in head else 'hay que infinitivo')
    return sorted(issues, key=lambda item: item['start'])


def references(query: str) -> list[dict]:
    """Return a short literal example only when relevant words occur together."""
    patterns = {
        'gustar': r'(?i)\b(?:me|te|le|nos|os|les)\s+gustan?\s+[^.;\n]{3,100}',
        'cuesta cuestan': r'(?i)\b(?:me|te|le|nos|os|les)\s+cuestan?\s+[^.;\n]{3,100}',
        'recomiendo': r'(?i)\brecomiendo\s+(?:que\s+)?[^.;\n]{3,100}',
        'hay que infinitivo': r'(?i)\bhay\s*\+?\s*que\s*\+?\s*infinitivo[^.;\n]{0,100}',
    }
    for passage in textbook.search(query, limit=4):
        match = re.search(patterns[query], str(passage['text']))
        if match:
            return [{'source': passage['source'], 'page': passage['page'], 'excerpt': match.group().strip()}]
    return []


def check(text: str) -> dict:
    issues = detect(text)
    repaired = text
    for issue in reversed(issues):
        repaired = repaired[:issue['start']] + issue['replacement'] + repaired[issue['end']:]
    model = providers.correct(repaired)
    suggestion = model.suggested
    rejected = bool(suggestion and (detect(suggestion) or
        PROTECTED.findall(suggestion.lower()) != PROTECTED.findall(repaired.lower())))
    if rejected:
        suggestion = None
    result = model.model_dump()
    result['original'] = text
    result['suggested'] = suggestion if suggestion is not None else (repaired if issues else None)
    if issues:
        result['status'] = 'partial' if model.status in {'partial', 'unavailable'} or rejected else 'suggestions'
    elif rejected:
        result.update(status='unavailable', suggested=None)
    elif result['suggested'] == text and model.status != 'partial':
        result['status'] = 'no_suggestion'
    for issue in issues:
        issue['references'] = references(issue.pop('query'))
    result['grammar_check'] = {'issues': issues, 'coverage': 'a2-unit-1',
        'model_status': 'rejected' if rejected else model.status}
    return result
