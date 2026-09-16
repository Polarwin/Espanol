"""Unit 1 glossary, checked against Vitamina A2 p.148 and bilingual supplement.

Expand shared verbs into complete phrases; keep repeated source entries in their
categories. English glosses clarify the sense for the local definition model.
"""

TITLE = 'Vitamina A2 · U1: Vamos a conocernos'
GROUPS = {
    'Animales': 'la ardilla|squirrel;el caballo|horse;el delfín|dolphin;el oso|bear',
    'Comida': 'desayunar|to have breakfast;comer|to eat, have lunch;cenar|to have dinner;la carne|meat;el dulce|sweet;la fruta|fruit',
    'Tiempo libre': 'correr|to run;estar en casa|to be at home;hacer amigos|to make friends;hacer deporte|to exercise;hacer planes|to make plans;hacer un intercambio|to do a language exchange;hacer yoga|to do yoga;ir de compras|to go shopping;ir de vacaciones|to go on holiday;jugar al fútbol|to play football;jugar con videojuegos|to play video games;leer libros|to read books;pasar tiempo en casa|to spend time at home;ponerse en forma|to get fit;quedar a una hora|to agree on a meeting time;quedar con amigos|to meet friends;relajarse|to relax;salir por la noche|to go out at night;tomar el sol|to sunbathe;tomar un café|to have a coffee;ver películas|to watch films;ver series|to watch series',
    'Intereses': 'el arte|art;el cine|cinema;la comida|food;la cultura|culture;el deporte|sport;la historia|history;la moda|fashion;la música|music;la naturaleza|nature;la tecnología|technology',
    'Ropa': 'el abrigo|coat;la camiseta|T-shirt;el traje|suit;los vaqueros|jeans',
    'Carácter': 'abierto/a|open, outgoing;alegre|cheerful;ambicioso/a|ambitious;casero/a|home-loving;cosmopolita|cosmopolitan;deportista|sporty;dinámico/a|energetic;divertido/a|fun;generoso/a|generous;individualista|individualistic;nervioso/a|nervous;perezoso/a|lazy;positivo/a|positive;relajado/a|relaxed;sociable|sociable;tímido/a|shy;tranquilo/a|calm;vago/a|lazy;buena persona|a good person',
    'Redes sociales': 'apuntarse a un evento|to sign up for an event;compartir el evento|to share the event;compartir el tiempo libre|to share free time;conocer gente|to meet people;crear un evento|to create an event;escribir en el muro|to post on a social media wall;hacer amigos|to make friends;juntar grupos de personas|to bring groups of people together;ligar|to flirt;votar a un jugador|to vote for a player;la aplicación|app;la app|app;el evento|event;el perfil|profile;el muro|social media wall',
    'En la escuela de español': 'aprovechar el tiempo|to make good use of time;apuntarse a una actividad|to sign up for an activity;asistir a una actividad|to attend an activity;ayudar a los compañeros|to help classmates;conocer a otros estudiantes|to meet other students;descubrir el significado de algo|to discover what something means;entender las noticias|to understand the news;escribir cartas|to write letters;escuchar con atención|to listen carefully;hacer actividades al aire libre|to do outdoor activities;hacer cosas divertidas|to do fun things;hacer los deberes|to do homework;hacer un intercambio|to do a language exchange;leer libros|to read books;mejorar la pronunciación|to improve pronunciation;opinar|to give an opinion;practicar un idioma|to practise a language;recordar el vocabulario|to remember vocabulary;tener curiosidad|to be curious;tener dudas|to have questions or doubts;tener fluidez|to speak fluently;trabajar en equipo|to work as a team;traducir|to translate;la actividad lúdica|playful learning activity;la biblioteca|library;la cafetería|café;el cómic|comic;el cuento|short story;el experto / la experta|expert;la gramática|grammar;la historia|story or history;el punto de encuentro|meeting point;la recepción|reception;el relato|story;el taller de escritura|writing workshop;el tema de conversación|conversation topic;la pronunciación|pronunciation;el vocabulario|vocabulary',
    'En la ciudad': 'alquilar una bici|to rent a bike;montar en bici|to ride a bike;recorrer el casco antiguo|to explore the old town;el cuadro|painting;el museo|museum;el parque|park;el puente|bridge;el río|river;la salida del metro|metro exit;la visita|visit',
    'Para preguntar': '¿Cómo se dice / se escribe…?|How do you say / write…?;¿Lleva tilde esta palabra?|Does this word have an accent mark?;¿Puedes ayudarme?|Can you help me?;¿Puedes repetir, por favor?|Can you repeat, please?;¿Qué has dicho?|What did you say?;¿Qué quiere decir…?|What does … mean?;¿Qué significa…?|What does … mean?',
}
WORDS = [
    {'id': f'{group_index}-{word_index}', 'category': category, 'text': pair.split('|')[0],
     'translation': pair.split('|')[1]}
    for group_index, (category, items) in enumerate(GROUPS.items())
    for word_index, pair in enumerate(items.split(';'))
]

GRAMMAR = [
    {'prompt': 'Me ___ los idiomas.', 'answer': 'gustan', 'rule': 'Gustar concuerda con lo que gusta: los idiomas es plural.'},
    {'prompt': 'Me ___ conocer gente.', 'answer': 'gusta', 'rule': 'Con un infinitivo, usamos gusta: me gusta conocer gente.'},
    {'prompt': 'No me gusta ir de compras. —A mí ___.', 'answer': 'tampoco', 'rule': 'Para coincidir con una frase negativa usamos tampoco.'},
    {'prompt': 'Me ___ las conversaciones rápidas.', 'answer': 'cuestan', 'rule': 'Costar concuerda con las conversaciones: plural, cuestan.'},
    {'prompt': 'Me cuesta ___ amigos. (hacer / hago)', 'answer': 'hacer', 'rule': 'Me cuesta + infinitivo expresa dificultad.'},
    {'prompt': 'Te recomiendo ___ español cada día. (practicar / practicas)', 'answer': 'practicar', 'rule': 'Te recomiendo + infinitivo sirve para dar un consejo.'},
    {'prompt': 'Hay que ___ con atención. (escuchar / escuchas)', 'answer': 'escuchar', 'rule': 'Hay que + infinitivo expresa una recomendación general.'},
    {'prompt': '¿___ quieres practicar? (Tu / Tú)', 'answer': 'tú', 'rule': 'Tú es la persona; tu indica posesión, como en tu compañero.'},
]
