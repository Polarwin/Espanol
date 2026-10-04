"""Build a self-contained offline deck. No book text or network is needed at runtime.

PYTHONPATH=/tmp/espanol-flashcard-pdf ./bin/python standalone/flashcards/build.py
Requires PyMuPDF and the locally downloaded, attributed Jehle CSV in /tmp.
"""
import csv
import hashlib
import json
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend.app.seed.a2_sample import WORDS
from backend.app.seed.vocabulary_content import RAW_BANKS

DEST = Path('/srv/files/static/EspanolFlashcards')
SOURCE = Path(__file__).parent


def norm(text):
    return ' '.join(re.sub(r'[^\w\s]', ' ', ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if not unicodedata.combining(c))).split())


def glossary():
    path = next((ROOT / 'Vitamina/Vitamina A2/Vitamina A2. Extras').glob('*Inglés*'))
    doc = pymupdf.open(path)
    rows = []
    unit, category, previous = 1, '', None
    for page_number, page in enumerate(doc, 1):
        columns = [defaultdict(list), defaultdict(list)]
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    x, y, _, _ = span['bbox']
                    if not span['text'].strip() or y < 70 or y > 775:
                        continue
                    columns[int(x >= 300)][round(y)].append(span)
        for col, lines in enumerate(columns):
            boundary = 439 if col else 184
            grouped = []
            for y, spans in sorted(lines.items()):
                if grouped and y - grouped[-1][0] <= 2:
                    grouped[-1][1].extend(spans)
                else:
                    grouped.append((y, list(spans)))
            for y, spans in grouped:
                spanish = sorted([s for s in spans if s['bbox'][0] < boundary - 1], key=lambda s: s['bbox'][0])
                english = sorted([s for s in spans if s['bbox'][0] >= boundary - 1], key=lambda s: s['bbox'][0])
                es = ' '.join(''.join(s['text'] for s in spanish).split())
                en = ' '.join(''.join(s['text'] for s in english).split())
                if es.startswith('UNIDAD'):
                    unit = int(re.search(r'\d+', es).group()); previous = None; continue
                if spanish and 'Heavy' in spanish[0]['font'] and spanish[0]['bbox'][0] - (255 if col else 0) < 60:
                    category = es; previous = None; continue
                if not es:
                    if rows and en and previous is not None: rows[-1]['en'] += ' ' + en
                    continue
                if not en:
                    if rows and es and previous is not None: rows[-1]['es'] += ' ' + es
                    continue
                left = spanish[0]['bbox'][0] - (255 if col else 0)
                # Indented continuations inherit the printed verb or noun stem.
                if previous and left > previous['left'] + 10:
                    candidates = ['las relaciones ', 'el desarrollo ', 'el aceite de ', 'el centro ', 'hablar de ', 'darse ', 'poner ', 'cruzarse ', 'subir ', 'guardar ', 'hacer ', 'ir ', 'jugar ', 'tomar ', 'ver ', 'ser ', 'estar ', 'tener ', 'quedar ', 'compartir ', 'es ']
                    prefix = next((p for p in candidates if previous['es'].startswith(p)), '')
                    if prefix and not es.startswith(prefix): es = prefix + es
                else:
                    previous = {'es': es, 'left': left}
                if category == 'Perder':
                    es = 'perder ' + es
                    if not en.startswith('to '): en = 'to miss ' + en
                rows.append({'es': es, 'en': en, 'unit': unit, 'category': category,
                             'source': 'Vitamina A2 · Glosario español–inglés', 'page': page_number})
    return rows


def main():
    records = list(csv.DictReader(Path('/tmp/espanol-jehle-verbs.csv').open(encoding='utf-8-sig')))
    conjugations = defaultdict(dict)
    translations = {}
    tenses = {('Indicativo', 'Presente'): 'Presente', ('Indicativo', 'Pretérito'): 'Indefinido',
              ('Indicativo', 'Imperfecto'): 'Imperfecto', ('Indicativo', 'Pretérito perfecto'): 'Perfecto',
              ('Indicativo', 'Futuro'): 'Futuro', ('Indicativo', 'Condicional'): 'Condicional',
              ('Subjuntivo', 'Presente'): 'Subjuntivo', ('Imperativo Afirmativo', 'Presente'): 'Imperativo +',
              ('Imperativo Negativo', 'Presente'): 'Imperativo −'}
    for row in records:
        verb = row['infinitive']
        translations[verb] = row['infinitive_english']
        if (row['mood'], row['tense']) in tenses:
            conjugations[verb][tenses[row['mood'], row['tense']]] = [row[f'form_{p}'] or '—' for p in ['1s', '2s', '3s', '1p', '2p', '3p']]
        conjugations[verb]['Participio'] = row['pastparticiple']
        conjugations[verb]['Gerundio'] = row['gerund']
    # Explicit regular-verb supplement, not a blanket regularity assumption.
    regular = 'adaptar apuntar aprovechar bajar cambiar contratar cruzar desconectar discutir escalar estornudar ligar llevar mejorar opinar pasear pelar planificar prestar recorrer recuperar relajar rellenar sobrevalorar solucionar tapar tatuar'.split()
    for verb in regular:
        if verb in conjugations: continue
        stem, ending = verb[:-2], verb[-2:]
        subjstem = stem[:-1] + {'c': 'qu', 'g': 'gu', 'z': 'c'}[stem[-1]] if ending == 'ar' and stem[-1] in 'cgz' else stem
        present = ['o','as','a','amos','áis','an'] if ending=='ar' else (['o','es','e','emos','éis','en'] if ending=='er' else ['o','es','e','imos','ís','en'])
        preterite = ['é','aste','ó','amos','asteis','aron'] if ending=='ar' else ['í','iste','ió','imos','isteis','ieron']
        imperfect = ['aba','abas','aba','ábamos','abais','aban'] if ending=='ar' else ['ía','ías','ía','íamos','íais','ían']
        subj = ['e','es','e','emos','éis','en'] if ending=='ar' else ['a','as','a','amos','áis','an']
        participle=stem+('ado' if ending=='ar' else 'ido')
        conjugations[verb]={'Presente':[stem+x for x in present], 'Indefinido':[stem+x for x in preterite],
            'Imperfecto':[stem+x for x in imperfect], 'Perfecto':[h+' '+participle for h in ['he','has','ha','hemos','habéis','han']],
            'Futuro':[verb+x for x in ['é','ás','á','emos','éis','án']], 'Condicional':[verb+x for x in ['ía','ías','ía','íamos','íais','ían']],
            'Subjuntivo':[subjstem+x for x in subj], 'Gerundio':stem+('ando' if ending=='ar' else 'iendo'), 'Participio':participle,
            'note':'Conjugación regular preparada para esta app; incluye los cambios ortográficos necesarios.'}
        if ending=='ar': conjugations[verb]['Indefinido'][0]=subjstem+'é'
    # Apetecer has the same -ecer alternation as parecer.
    if 'apetecer' not in conjugations:
        conjugations['apetecer'] = {k: [x.replace('parec','apetec').replace('parez','apetez') for x in v] if isinstance(v,list) else v.replace('parec','apetec').replace('parez','apetez') for k,v in conjugations['parecer'].items()}
        conjugations['apetecer']['note']='Formas adaptadas del paradigma de parecer: apetezco, apetezca.'
    if 'reunir' not in conjugations:
        conjugations['reunir'] = {
            'Presente':['reúno','reúnes','reúne','reunimos','reunís','reúnen'],
            'Indefinido':['reuní','reuniste','reunió','reunimos','reunisteis','reunieron'],
            'Imperfecto':['reunía','reunías','reunía','reuníamos','reuníais','reunían'],
            'Perfecto':[h+' reunido' for h in ['he','has','ha','hemos','habéis','han']],
            'Futuro':['reunir'+x for x in ['é','ás','á','emos','éis','án']],
            'Condicional':['reunir'+x for x in ['ía','ías','ía','íamos','íais','ían']],
            'Subjuntivo':['reúna','reúnas','reúna','reunamos','reunáis','reúnan'],
            'Gerundio':'reuniendo','Participio':'reunido'}
    for verb in 'adaptarse apuntarse bajarse conocerse cruzarse darse dirigirse llevarse presentarse relajarse reunirse reírse taparse tatuarse'.split():
        if verb in conjugations: continue
        base=verb[:-2]
        if base not in conjugations: raise ValueError('Missing reflexive base: '+base)
        original=conjugations[base]
        conjugations[verb]={k:[pronoun+' '+form for pronoun,form in zip(['me','te','se','nos','os','se'],forms)] for k,forms in original.items() if isinstance(forms,list) and not k.startswith('Imperativo')}
        conjugations[verb].update(Gerundio=original['Gerundio'],Participio=original['Participio'],note='Forma pronominal: me, te, se, nos, os, se. Gerundio y participio mostrados sin pronombre. Se incluyen siete tiempos; el imperativo no se muestra en esta adaptación.')
    rows = glossary()
    # Existing manually reviewed Unit 1 translations take precedence.
    reviewed = {norm(w['text']): w['translation'] for w in WORDS}
    for row in rows:
        row['en'] = reviewed.get(norm(row['es']), row['en'])
        if row['es'].startswith(('ser ', 'estar ')) and not row['en'].startswith('to '): row['en'] = 'to be ' + row['en']
    fixes = {'pelar':'to peel', 'ir de cámping':'to go camping', 'poner en el frigorífico':'to put in the fridge',
             'jugar con videojuegos':'to play video games', 'hacer un intercambio':'to do a language exchange',
             'ser seguro/a':'to be safe', 'darse la mano':'to shake hands', 'darse una ducha fresca':'to take a cool shower'}
    for row in rows:
        row['en'] = fixes.get(row['es'], row['en'])
    for word in WORDS:
        if not any(norm(r['es']) == norm(word['text']) for r in rows):
            rows.append({'es': word['text'], 'en': word['translation'], 'unit': 1, 'category': word['category'],
                         'source': 'Vitamina A2 · Libro del alumno · Glosario', 'page': 149})
    # Add previously curated terms only when the term occurs in a Ke OCR page.
    with sqlite3.connect(ROOT / 'content/textbook-index.sqlite3') as db:
        passages = [(s, p, norm(t)) for s, p, t in db.execute('select source,page,text from chunks')]
    evidence_cache = {}
    def evidence(term):
        term = norm(term)
        if term not in evidence_cache:
            evidence_cache[term] = next(((s, p) for s, p, text in passages if (' '+term+' ') in (' '+text+' ')), None)
        return evidence_cache[term]
    for title, bank in RAW_BANKS.items():
        for pair in bank.split(';'):
            term, translation = pair.split('|', 1)
            found = evidence(term)
            if found:
                rows.append({'es': term, 'en': translation, 'unit': 0, 'category': 'Ke · Vocabulario', 'source': found[0], 'page': found[1]})
    # Standalone verbs supplement both glossary phrases and the Ke exercise vocabulary.
    for verb, translation in translations.items():
        found = evidence(verb)
        if found:
            rows.append({'es': verb, 'en': translation, 'unit': 0, 'category': 'Ke · Verbos', 'source': found[0], 'page': found[1]})
    cards = {}
    missing = set()
    for row in rows:
        term = row['es'].strip()
        if len(term) < 2 or not row['en'].strip(): continue
        key = ' '.join(unicodedata.normalize('NFC', term.lower()).split())
        card = cards.setdefault(key, {'id': hashlib.sha256(key.encode()).hexdigest()[:12], 'es': term,
            'en': row['en'], 'units': [], 'categories': [], 'sources': [], 'verb': None})
        if row['unit'] and row['unit'] not in card['units']: card['units'].append(row['unit'])
        if row['category'] not in card['categories']: card['categories'].append(row['category'])
        source = {'book': row['source'], 'page': row['page']}
        if source not in card['sources']: card['sources'].append(source)
        first = term.lower().split()[0].replace('(se)', 'se')
        if first in {'sirve', 'sirven'}: first = 'servir'
        if first == 'es': first = 'ser'
        if first in conjugations:
            card['verb'] = first
        elif first.endswith(('ar', 'er', 'ir', 'arse', 'erse', 'irse', 'ír', 'írse')) and not first.startswith(('¿', '¡')) and first not in {'collar'}:
            missing.add(first)
    # Report missing paradigms; never silently invent irregular conjugations.
    print('MISSING VERBS', sorted(missing))
    if missing: raise ValueError('Every verb card needs a conjugation: '+', '.join(sorted(missing)))
    used = {c['verb'] for c in cards.values() if c['verb']}
    deck = {'version': '1.0.0', 'cards': list(cards.values()), 'verbs': {v: conjugations[v] for v in sorted(used)},
            'credit': 'Conjugaciones: Fred Jehle / Brian Ghidinelli · CC BY-NC-SA 3.0. Vocabulario: selección de los libros locales Ke y Vitamina; no es una transcripción completa de todos los libros.'}
    DEST.mkdir(parents=True, exist_ok=True)
    # Build artifacts, generated from source templates and the local books.
    html = (SOURCE / 'app.html').read_text().replace('/*__DECK__*/', 'const DECK = ' + json.dumps(deck, ensure_ascii=False).replace('</', '<\\/') + ';')
    cache_name = 'palabra-' + hashlib.sha256(html.encode()).hexdigest()[:12]
    html = html.replace('palabra-v1', cache_name)
    (DEST / 'index.html').write_text(html)
    offline = re.sub(r'<link rel="(?:manifest|icon)"[^>]*>', '', html)
    (DEST / 'EspanolFlashcards-offline.html').write_text(offline)
    (DEST / 'data-audit.json').write_text(json.dumps(deck, ensure_ascii=False, indent=2))
    for name in ['sw.js', 'manifest.webmanifest', 'icon.svg']:
        (DEST / name).write_text((SOURCE / name).read_text().replace('palabra-v1', cache_name))
    icon = pymupdf.open(stream=(SOURCE / 'icon.svg').read_bytes(), filetype='svg')
    for size in [192, 512]:
        icon[0].get_pixmap(matrix=pymupdf.Matrix(size / 192, size / 192), alpha=False).save(DEST / f'icon-{size}.png')
    (DEST / 'CONJUGATION-LICENSE.txt').write_text(Path('/tmp/espanol-jehle-license.txt').read_text())
    print('CARDS', len(cards), 'VERBS', len(used), 'UNITS', sorted({u for c in cards.values() for u in c['units']}))
    print('SOURCE ROWS', len(rows), 'GLOSSARY ROWS', len(glossary()))


if __name__ == '__main__': main()
