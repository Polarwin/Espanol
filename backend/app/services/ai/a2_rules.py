"""Selected high-confidence checks mapped to the ten Vitamina A2 topics.

These are bounded patterns, not a full Spanish parser. Avoid guessing tense
from time adverbs, regional pronoun choices, or the intended meaning of ser/estar.
"""
import re

UNITS = [
    '1 · Conocer y conocerse: gustos, dificultades y consejos',
    '2 · Mi lugar en el mundo: participios del pretérito perfecto',
    '3 · La vida secreta de los objetos: se puede + infinitivo',
    '4 · Tiempo de ocio: gerundios frecuentes',
    '5 · Biografías: formas de tú en indefinido',
    '6 · Gastronomía: soler + infinitivo y cantidades',
    '7 · De compras: tan/tanto en comparaciones',
    '8 · Otras épocas: imperfectos irregulares y se lo/se la',
    '9 · La salud: doler y perífrasis con infinitivo',
    '10 · Culturas: concordancia de posesivos',
]

FINITE = dict(zip(
    'hablas comes bebes estudias practicas escuchas cocinas lees escribes trabajas compras descansas'.split(),
    'hablar comer beber estudiar practicar escuchar cocinar leer escribir trabajar comprar descansar'.split()))
NOUNS = {'agua': ('s', 'f'), 'leche': ('s', 'f'), 'sal': ('s', 'f'), 'comida': ('s', 'f'),
         'arroz': ('s', 'm'), 'pan': ('s', 'm'), 'queso': ('s', 'm'),
         'manzanas': ('p', 'f'), 'verduras': ('p', 'f'), 'frutas': ('p', 'f'),
         'libros': ('p', 'm'), 'regalos': ('p', 'm'), 'camisas': ('p', 'f'), 'zapatos': ('p', 'm')}


def detect(text):
    issues = []

    def add(m, replacement, unit, rule, explanation, query):
        original = m.group('edit')
        if original == replacement:
            return
        if original[0].isupper():
            replacement = replacement.capitalize()
        issues.append(dict(start=m.start('edit'), end=m.end('edit'), original=original,
                           replacement=replacement, unit=unit, rule=rule,
                           explanation=explanation, query=query))

    def mapped(pattern, forms, unit, rule, explanation, query):
        for m in re.finditer(pattern, text, re.I):
            add(m, forms[m.group('edit').lower()], unit, rule, explanation, query)

    participles = {'hacido': 'hecho', 'escribido': 'escrito', 'abrido': 'abierto',
                  'ponido': 'puesto', 'volvido': 'vuelto', 'rompido': 'roto',
                  'morido': 'muerto', 'decido': 'dicho', 'vido': 'visto'}
    mapped(r'\b(?:he|has|ha|hemos|habéis|han)\s+(?P<edit>' + '|'.join(participles) + r')\b', participles, 2,
           'perfect-participle', 'Este verbo tiene un participio irregular. Con haber usamos esa forma para el pretérito perfecto.', 'participio')
    finite = '|'.join(FINITE)
    mapped(r'\bse\s+puede\s+(?P<edit>' + finite + r')\b', FINITE, 3,
           'impersonal-infinitive', 'Después de «se puede» usamos un infinitivo: se puede hablar.', 'infinitivo')
    gerunds = {'leiendo': 'leyendo', 'dormiendo': 'durmiendo', 'morriendo': 'muriendo',
               'podiendo': 'pudiendo', 'veniendo': 'viniendo',
               'sigiendo': 'siguiendo', 'construiendo': 'construyendo'}
    mapped(r'\b(?:estoy|estás|está|estamos|estáis|están|estaba|estaban)\s+(?P<edit>' + '|'.join(gerunds) + r')\b', gerunds, 4,
           'progressive-gerund', 'Con estar, la acción en curso se expresa con un gerundio. Revisa la forma de este gerundio irregular.', 'gerundio')
    past = {word + 's': word for word in 'fuiste dijiste hiciste tuviste estuviste comiste hablaste estudiaste viniste viste compraste'.split()}
    mapped(r'\b(?P<edit>' + '|'.join(past) + r')\b', past, 5,
           'preterite-tu', 'La forma de tú del pretérito indefinido termina en -ste, sin una s final.', 'indefinido')
    mapped(r'\b(?:suelo|sueles|suele|solemos|soléis|suelen)\s+(?P<edit>' + finite + r')\b', FINITE, 6,
           'soler-infinitive', 'Soler expresa un hábito y va seguido de infinitivo: suelo cocinar.', 'soler')
    for m in re.finditer(r'\b(?P<edit>much[oa]s?|demasiad[oa]s?|poc[oa]s?)\s+(?P<noun>' + '|'.join(NOUNS) + r')\b', text, re.I):
        number, gender = NOUNS[m.group('noun').lower()]
        base = re.sub(r'[oa]s?$', '', m.group('edit').lower())
        add(m, base + ('a' if gender == 'f' else 'o') + ('s' if number == 'p' else ''), 6,
            'quantity-agreement', 'La cantidad concuerda con el nombre en género y número: mucha agua, muchas manzanas.', 'cuantificadores')
    for m in re.finditer(r'\b(?P<edit>tan)\s+(?P<noun>' + '|'.join(NOUNS) + r')\s+como\b', text, re.I):
        number, gender = NOUNS[m.group('noun').lower()]
        add(m, 'tant' + ('a' if gender == 'f' else 'o') + ('s' if number == 'p' else ''), 7,
            'comparison-noun', 'Para comparar cantidades usamos tanto/a/os/as + nombre + como.', 'tanto')
    mapped(r'\b(?P<edit>tanto|tanta|tantos|tantas)\s+(?:alto|alta|altos|altas|caro|cara|caros|caras|barato|barata|grande|pequeño|pequeña)\s+como\b',
           dict.fromkeys(['tanto', 'tanta', 'tantos', 'tantas'], 'tan'), 7,
           'comparison-adjective', 'Con un adjetivo usamos tan + adjetivo + como.', 'comparativos')
    imperfect = {'eraba': 'era', 'erabas': 'eras', 'erábamos': 'éramos', 'eraban': 'eran',
                 'veiba': 'veía', 'veibas': 'veías', 'veibamos': 'veíamos', 'veiban': 'veían'}
    mapped(r'\b(?P<edit>' + '|'.join(imperfect) + r')\b', imperfect, 8,
           'imperfect-irregular', 'Ser y ver tienen formas irregulares en imperfecto: era y veía.', 'imperfecto')
    mapped(r'\b(?P<edit>le|les)\s+(?:lo|la|los|las)\s+(?:doy|das|da|damos|dan|di|dio|dieron|he|has|ha|hemos|han|envío|envía|envió|presto|prestó)\b',
           {'le': 'se', 'les': 'se'}, 8, 'object-pronouns',
           'Delante de lo, la, los o las, le y les cambian a se: se lo doy.', 'pronombres')
    for m in re.finditer(r'\b(?:me|te|le|nos|os|les)\s+(?P<edit>duele|duelen)\s+(?P<body>(?:la cabeza|el estómago|la espalda|los pies|las piernas|los brazos|los dientes))(?=[.!?;\n]|$)', text, re.I):
        plural = m.group('body').lower().startswith(('los ', 'las '))
        add(m, 'duelen' if plural else 'duele', 9, 'doler-agreement',
            'Doler concuerda con la parte del cuerpo: me duele la cabeza; me duelen los pies.', 'doler')
    mapped(r'\b(?:empiezo a|empiezas a|empieza a|vuelvo a|vuelves a|vuelve a|acabo de|acabas de|acaba de|dejo de|dejas de|deja de)\s+(?P<edit>' + finite + r')\b',
           FINITE, 9, 'verbal-periphrasis', 'Después de empezar a, volver a, acabar de y dejar de usamos infinitivo.', 'infinitivo')
    for m in re.finditer(r'\b(?:es|son|era|eran)\s+(?P<article>el|la|los|las)\s+(?P<edit>mío|mía|míos|mías|tuyo|tuya|tuyos|tuyas|suyo|suya|suyos|suyas)(?=[.!?;\n]|$)', text, re.I):
        article = m.group('article').lower()
        base = re.sub(r'[oa]s?$', '', m.group('edit').lower())
        add(m, base + ('a' if article in {'la', 'las'} else 'o') + ('s' if article in {'los', 'las'} else ''),
            10, 'possessive-agreement', 'El posesivo concuerda con lo poseído: el mío, la mía, los míos, las mías.', 'posesivos')
    return issues
