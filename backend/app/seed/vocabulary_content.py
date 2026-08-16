"""Curated thematic word banks and vocabulary practice for every unit."""

import re
from typing import Any


def _pairs(items: str) -> list[tuple[str, str]]:
    return [tuple(item.split("|", 1)) for item in items.split(";")]


RAW_BANKS = {
    # A1: ten high-frequency words or chunks per unit.
    "En el café": "la mesa|table;la carta|menu;el camarero|waiter;pedir|to order;tomar|to have;un café con leche|coffee with milk;la cuenta|bill;por favor|please;para mí|for me;¿Algo más?|Anything else?",
    "Primeras presentaciones": "llamarse|to be called;ser de|to be from;vivir en|to live in;el nombre|first name;el apellido|surname;el país|country;el idioma|language;encantado|pleased to meet you;¿A qué te dedicas?|What do you do?;¿Cómo se escribe?|How is it written?",
    "Mi familia y mi casa": "la familia|family;los padres|parents;el hermano|brother;la hermana|sister;la pareja|partner;el salón|living room;el dormitorio|bedroom;la cocina|kitchen;vivir con|to live with;mi y mis|my",
    "Un día normal": "levantarse|to get up;desayunar|to have breakfast;empezar|to begin;trabajar|to work;comer|to have lunch;volver a casa|to return home;cenar|to have dinner;acostarse|to go to bed;por la mañana|in the morning;todos los días|every day",
    "Aprender juntos": "aprender|to learn;practicar|to practise;repetir|to repeat;entender|to understand;hablar|to speak;escuchar|to listen;una palabra|a word;una frase|a sentence;todavía|still;con fluidez|fluently",
    "A1 · Unidad 6: Esto me gusta": "gustar|to like;encantar|to love;preferir|to prefer;el tiempo libre|free time;cocinar|to cook;correr|to run;ver una película|to watch a film;quedar con amigos|to meet friends;yo también|me too;yo tampoco|me neither",
    "A1 · Unidad 7: De aquí para allá": "el barrio|neighbourhood;la estación|station;el mercado|market;la biblioteca|library;el parque|park;al lado de|next to;cerca de|near;lejos de|far from;ir en metro|to go by metro;¿Cómo voy a...?|How do I get to...?",
    "A1 · Unidad 8: ¿Qué hacemos?": "hacer planes|to make plans;quedar|to meet;tener hambre|to be hungry;tomar tapas|to have tapas;conocer un lugar|to know a place;la plaza|square;el viernes|Friday;a las ocho|at eight;buena idea|good idea;perfecto|perfect",
    "A1 · Unidad 9: Tiempo y ropa": "hacer frío|to be cold;hacer calor|to be hot;estar nublado|to be cloudy;llover|to rain;el abrigo|coat;las botas|boots;la camiseta|T-shirt;ponerse|to put on;azul|blue;negro|black",
    "A1 · Unidad 10: Ciudadanos del mundo": "viajar|to travel;visitar|to visit;alguna vez|ever;dos veces|twice;saber hacer|to know how to do;poder|can;bailar|to dance;cocinar|to cook;ya|already;todavía no|not yet",

    # A2: twelve words/chunks per unit, with more collocations.
    "Charla con vecinos": "los vecinos|neighbours;el fin de semana|weekend;tener planes|to have plans;quedar para comer|to meet for lunch;hacer una barbacoa|to have a barbecue;traer algo|to bring something;confirmar|to confirm;apuntarse|to join;venir bien|to suit;estar libre|to be free;pasarlo bien|to have a good time;nos vemos|see you",
    "De viaje": "el alojamiento|accommodation;reservar|to book;el billete|ticket;la ida|outward journey;la vuelta|return journey;el equipaje|luggage;facturar|to check in;la puerta de embarque|boarding gate;el retraso|delay;hacer escala|to have a stopover;alojarse|to stay;cancelar la reserva|to cancel the booking",
    "Compras en el mercado": "el puesto|stall;el kilo|kilogram;medio kilo|half a kilogram;maduro|ripe;fresco|fresh;barato|cheap;caro|expensive;pesar|to weigh;costar|to cost;llevarse|to take/buy;¿Cuánto cuesta?|How much is it?;¿Me pone...?|Could I have...?",
    "En la consulta": "la consulta|doctor's office;pedir cita|to make an appointment;doler|to hurt;tener fiebre|to have a fever;estar resfriado|to have a cold;la garganta|throat;la receta|prescription;tomar una pastilla|to take a tablet;descansar|to rest;encontrarse mejor|to feel better;desde ayer|since yesterday;dos veces al día|twice a day",
    "Buscar piso": "el alquiler|rent;el piso|flat;amueblado|furnished;luminoso|bright;los gastos|utilities;la fianza|deposit;el dormitorio|bedroom;el ascensor|lift;estar disponible|to be available;compartir piso|to share a flat;concertar una visita|to arrange a viewing;gastos incluidos|utilities included",
    "Vitamina A2 · U1: Vamos a conocernos": "los intereses|interests;el tiempo libre|free time;soler|to usually do;quedar con|to meet;hacer excursiones|to go hiking;ver series|to watch series;resultar difícil|to find difficult;me cuesta|I find it hard;me encanta|I love;prefiero|I prefer;tener en común|to have in common;dar una recomendación|to give advice",
    "Vitamina A2 · U2: Mi lugar en el mundo": "vivir en el extranjero|to live abroad;adaptarse|to adapt;las costumbres|customs;los trámites|paperwork;el transporte público|public transport;las afueras|outskirts;el campo|countryside;la ciudad|city;ruidoso|noisy;tranquilo|quiet;desde hace|for/since;lo más difícil|the hardest thing",
    "Vitamina A2 · Repaso U1–U2": "presentarse|to introduce oneself;describir una rutina|to describe a routine;expresar gustos|to express likes;comparar lugares|to compare places;dar consejos|to give advice;mejorar|to improve;la comprensión|comprehension;los compañeros|classmates;dos veces por semana|twice a week;a veces|sometimes;normalmente|normally;por eso|therefore",
    "Una ruta de senderismo": "la ruta|route;hacer senderismo|to hike;la parada de autobús|bus stop;el bosque|forest;durar|to last;el ritmo|pace;llevar agua|to bring water;el calzado cómodo|comfortable footwear;confirmar|to confirm;de momento|for now;ser el sexto|to be the sixth;a primera hora|early in the morning",
    "A2 · Unidad 10: Culturas": "las costumbres|customs;la convivencia|community life;sentirse en casa|to feel at home;pedir un favor|to ask a favour;ofrecer ayuda|to offer help;con confianza|confidently;respetar|to respect;el malentendido|misunderstanding;adaptarse a|to adapt to;desde que|since;otras formas de vivir|other ways of living;tener sal|to have salt",

    # B1: fifteen lexical items and discourse chunks per unit.
    "Mensajes con intención": "la intención|intention;dejar un mensaje|to leave a message;devolver la llamada|to return a call;ponerse en contacto|to get in touch;la factura|invoice;adjuntar|to attach;se ruega confirmación|confirmation is requested;la ceremonia|ceremony;comunicar|to inform;la entrada en vigor|entry into force;solicitar|to request;hacer una gestión|to handle a matter;en cuanto puedas|as soon as you can;quedar a la espera|to await;un saludo cordial|kind regards",
    "B1 · Unidad 1: Volver a vernos": "reencontrarse|to meet again;ponerse al día|to catch up;cambiar de trabajo|to change jobs;desde la última vez|since last time;seguir igual|to remain the same;estar cambiado|to look different;perder el contacto|to lose touch;retomar una amistad|to rekindle a friendship;recordar|to remember;resultar familiar|to look familiar;¡Cuánto tiempo!|Long time no see!;¿Qué ha sido de ti?|What have you been up to?;últimamente|lately;desde entonces|since then;tenemos que quedar|we must meet",
    "B1 · Unidad 2: Recuerdos": "la infancia|childhood;un recuerdo|memory;acordarse de|to remember;de pequeño|as a child;en aquella época|at that time;soler hacer|to used to do;mientras|while;de repente|suddenly;al final|in the end;resulta que|it turns out;perder las llaves|to lose the keys;estar lloviendo|to be raining;sin querer|accidentally;a propósito|on purpose;quedarse grabado|to remain etched",
    "B1 · Unidad 3: El mundo del futuro": "hacer una predicción|to make a prediction;dentro de veinte años|in twenty years;probablemente|probably;puede que|perhaps;ojalá|hopefully;la calidad de vida|quality of life;reducir el consumo|to reduce consumption;la energía renovable|renewable energy;el coche privado|private car;la inteligencia artificial|artificial intelligence;el avance|advance;la incertidumbre|uncertainty;será posible|it will be possible;es poco probable|it is unlikely;anticiparse|to anticipate",
    "B1 · Unidad 4: Trabajo": "el puesto|position;la oferta de empleo|job offer;la experiencia laboral|work experience;trabajar en equipo|to work in a team;el horario flexible|flexible schedule;la reunión presencial|in-person meeting;conciliar|to balance work and life;el currículum|CV;la entrevista|interview;contratar|to hire;cumplir los requisitos|to meet the requirements;estar a cargo de|to be responsible for;solicitar el puesto|to apply for the position;incorporarse|to start a job;las condiciones laborales|working conditions",
    "B1 · Unidad 5: Buen viaje": "la incidencia|incident;perder el vuelo|to miss the flight;la puerta de embarque|boarding gate;la compañía aérea|airline;hacer una reclamación|to make a complaint;ofrecer alojamiento|to offer accommodation;el seguro de viaje|travel insurance;la escala|stopover;el destino|destination;el trayecto|journey;viajar por libre|to travel independently;salir según lo previsto|to leave as scheduled;haber cambiado|to have changed;a pesar de|despite;resolver el problema|to solve the problem",
    "B1 · Unidad 6: Vivienda": "el ayuntamiento|town council;las zonas verdes|green spaces;el transporte nocturno|night transport;el tráfico|traffic;el alquiler asequible|affordable rent;las instalaciones|facilities;la asociación vecinal|neighbourhood association;presentar una propuesta|to submit a proposal;hace falta|it is necessary;debería haber|there should be;si hubiera|if there were;ser más agradable|to be nicer;rehabilitar|to renovate;peatonal|pedestrian;mejorar el barrio|to improve the neighbourhood",
    "B1 · Unidad 7: Relaciones humanas": "llevarse bien|to get along;interrumpir|to interrupt;hablar con sinceridad|to speak honestly;resolver un conflicto|to resolve a conflict;enfadarse|to get angry;apoyarse|to support each other;confiar en|to trust;sentirse decepcionado|to feel disappointed;me molesta que|it bothers me that;no soporto que|I cannot stand that;me encanta que|I love that;no estoy de acuerdo|I disagree;desde mi punto de vista|from my point of view;ponerse en el lugar de|to put oneself in someone's shoes;llegar a un acuerdo|to reach an agreement",
    "B1 · Unidad 8: ¡Que aproveche!": "la gastronomía|gastronomy;los ingredientes|ingredients;el sabor|flavour;el aroma|aroma;picante|spicy;suave|mild;la receta|recipe;mezclar|to mix;servir|to serve;conservar|to preserve;un truco de cocina|a cooking tip;para que|so that;puede que|it may;estar en su punto|to be perfectly cooked;¡Que aproveche!|Enjoy your meal!",
    "B1 · Unidad 9: Economía y consumo": "el ahorro|savings;los gastos|expenses;el presupuesto|budget;comprar por impulso|to buy impulsively;comparar precios|to compare prices;el consumo responsable|responsible consumption;desperdiciar|to waste;reparar|to repair;sustituir|to replace;la mayoría|the majority;uno de cada tres|one in three;según la encuesta|according to the survey;sin embargo|however;en lugar de|instead of;llegar a fin de mes|to make ends meet",

    # B2: fifteen lexical items and discourse chunks per unit.
    "B2 · Unidad 1: Señas de identidad": "el nombre propio|given name;el mote|nickname;el origen|origin;significar|to mean;poner el nombre|to name after;la bisabuela|great-grandmother;una tradición familiar|family tradition;coincidir con|to coincide with;la marca|brand;las señas de identidad|identity traits;de origen árabe|of Arabic origin;repetir un nombre|to repeat a name;llevar el nombre de|to bear someone's name;curiosamente|curiously;el sentido del humor|sense of humour",
    "B2 · Unidad 2: Enigmas": "el enigma|enigma;la incógnita|unknown;el misterio|mystery;el testigo|witness;la explicación lógica|logical explanation;debe de haber|there must be;puede que haya|there may have been;desaparecer|to disappear;exagerar|to exaggerate;los investigadores|researchers;sin rastro|without a trace;el faro|lighthouse;seguir siendo|to remain;hacer suposiciones|to make guesses;resolver el misterio|to solve the mystery",
    "B2 · Unidad 3: Al límite": "saltar en paracaídas|to skydive;la euforia|euphoria;el miedo|fear;la sensación|feeling;caer hacia el vacío|to fall into the void;tener valor|to have courage;escalar una montaña|to climb a mountain;una experiencia vital|life-changing experience;los derechos de los animales|animal rights;si tuviera|if I had;lo repetiría|I would repeat it;una aventura al límite|an extreme adventure;emocionarse|to get emotional;nunca olvidaré|I will never forget;al límite|at the limit",
    "B2 · Unidad 4: Referentes": "el referente|role model;dejar huella|to leave a mark;la profesora|teacher;animar a|to encourage;los primeros relatos|first short stories;las mujeres precursoras|pioneering women;no ser reconocido|to go unrecognised;en su época|in their time;el influencer|influencer;los seguidores|followers;convertirse en|to become;fue ella quien|it was she who;admirar|to admire;un ejemplo a seguir|an example to follow;inspirar|to inspire",
    "B2 · Unidad 5: Evolución": "la reseña|review;la novela|novel;el título|title;la autora|author;el estilo|style;los críticos|critics;elogiar|to praise;el final|ending;decepcionar|to disappoint;cuyo|whose;de quien|about whom;la evolución|evolution;los personajes|characters;la escritura formal|formal writing;una valoración|an assessment",
    "B2 · Unidad 6: El paso del tiempo": "el paso del tiempo|the passing of time;la estética|aesthetics;la belleza|beauty;un objeto dañado|a damaged object;el valor especial|special value;conservar el encanto|to keep the charm;restaurar|to restore;el reloj antiguo|old clock;me habría gustado|I would have liked;habríamos hecho|we would have done;costar demasiado|to cost too much;la nostalgia|nostalgia;cien años|a hundred years;los bisabuelos|great-grandparents;el siglo pasado|last century",
    "B2 · Unidad 7: Suerte": "la suerte|luck;la mala suerte|bad luck;tocar madera|to touch wood;el trébol de cuatro hojas|four-leaf clover;la manía|habit;ahuyentar|to ward off;la superstición|superstition;en cuanto|as soon as;cuando encuentre|when I find;guardar|to keep;el amuleto|amulet;la buena suerte|good luck;con esfuerzo|through effort;la obsesión|obsession;desarrollar manías|to develop habits",
    "B2 · Unidad 8: Con duende": "el duende|magic charm;con encanto|charming;un rincón del mundo|a corner of the world;fascinante|fascinating;el rito|rite;la hoguera|bonfire;un plan seductor|an enticing plan;salido de un cuento|out of a fairy tale;la mezcla de culturas|mix of cultures;lo fascinante|the fascinating thing;cada verano|every summer;celebrar un rito|to celebrate a rite;proponer un plan|to propose a plan;las calles empedradas|cobbled streets;enamorarse de un lugar|to fall in love with a place",
    "B2 · Unidad 9: Con sentido": "los sentidos|senses;el olor a café|smell of coffee;transportar|to transport;el gusto|sense of taste;oí cantar|I heard singing;los pájaros|birds;amanecer|to dawn;guardar recuerdos|to hold memories;el sentido predominante|predominant sense;el oído|hearing;la vista|eyesight;el olfato|sense of smell;el tacto|touch;la memoria sensorial|sensory memory;una obra de arte|a work of art",
    "B2 · Unidad 10: Historia": "la historia|history;el acontecimiento|event;la probabilidad|probability;sería|it could be;debió de ser|it must have been;el siglo XIX|nineteenth century;seguir en pie|to still stand;los habitantes|inhabitants;la historia alterna|alternate history;¿qué habría pasado?|what would have happened?;fue construido|was built;está destruido|is destroyed;una época difícil|a difficult time;las fotos antiguas|old photos;el documento|document",
    "B2 · Unidad 11: La imagen": "la imagen|image;la publicidad|advertising;ideas normativas|normative ideas;la sociedad|society;el sufijo apreciativo|appreciative suffix;el problemita|little problem;el hombretón|big burly man;el discursito|little speech;el desperdicio alimentario|food waste;la apariencia|appearance;merecer|to deserve;resultar ser|to turn out to be;el público|audience;cambiar de opinión|to change one's mind;con humor|with humour",
    "B2 · Unidad 12: Más que palabras": "el matiz|nuance;más que palabras|more than words;ser listo|to be clever;estar listo|to be ready;estar frío|to be cold;ser abierto|to be open;estar callado|to be quiet;la constancia|consistency;una cuestión de perspectiva|a matter of perspective;la combinación frecuente|frequent collocation;buscar sinónimos|to look for synonyms;el aprendizaje de idiomas|language learning;por carácter|by nature;un estado temporal|a temporary state;el significado|meaning",
}

VOCABULARY_BANKS = {title: _pairs(items) for title, items in RAW_BANKS.items()}


def _cloze_sentence(lesson: dict[str, Any], text: str) -> str | None:
    """Find a lesson sentence containing the word and blank it out (DELE cloze)."""
    needle = re.escape(text.lower())
    candidates = [line["es"] for segment in lesson["segments"] for line in segment["transcript"]]
    candidates += [
        ex["expected_answer"] for ex in lesson["exercises"] if ex["type"] == "writing"
    ]
    for sentence in candidates:
        match = re.search(rf"(?<!\w){needle}(?!\w)", sentence, flags=re.IGNORECASE)
        if match:
            return sentence[: match.start()] + "___" + sentence[match.end() :]
    return None


def enrich_lessons(lessons: list[dict[str, Any]]) -> None:
    """Add visible vocabulary and varied checks to the authored catalog."""
    targets = {"A1": 4, "A2": 5, "B1": 6, "B2": 7}
    for lesson in lessons:
        bank = VOCABULARY_BANKS.get(lesson["title"], [])
        if not bank:
            continue
        segments = lesson["segments"]
        existing_phrases = {
            phrase["text"] for segment in segments for phrase in segment["phrases"]
        }
        for index, (text, translation) in enumerate(bank):
            if text not in existing_phrases:
                segments[index % len(segments)]["phrases"].append(
                    {"text": text, "translation": translation, "tip": None}
                )

        vocabulary = [ex for ex in lesson["exercises"] if ex["type"] == "vocabulary"]
        existing_prompts = {ex["prompt"] for ex in vocabulary}
        candidates = [(text, translation) for text, translation in bank if text not in existing_prompts]
        needed = max(0, targets[lesson["cefr_level"]] - len(vocabulary))
        additions = []
        for index, (text, translation) in enumerate(candidates[:needed]):
            other_words = [word for word, _ in bank if word != text]
            distractors = [other_words[index % len(other_words)], other_words[(index + 3) % len(other_words)]]
            cloze = _cloze_sentence(lesson, text)
            if cloze:
                # DELE-style: complete the sentence with the right word.
                additions.append(
                    {
                        "type": "vocabulary",
                        "instructions": "Elige la palabra que completa la frase.",
                        "prompt": cloze,
                        "options": [text, *distractors],
                        "expected_answer": text,
                        "skill_weights": {"vocabulary": 1.0},
                    }
                )
            else:
                additions.append(
                    {
                        "type": "vocabulary",
                        "instructions": "Elige la palabra correcta.",
                        "prompt": f"¿Qué palabra significa «{translation}»?",
                        "options": [text, *distractors],
                        "expected_answer": text,
                        "skill_weights": {"vocabulary": 1.0},
                    }
                )
        lesson["exercises"] = vocabulary + additions + [
            ex for ex in lesson["exercises"] if ex["type"] != "vocabulary"
        ]

