"""Original companion units following Vitamina's action-oriented progression."""

from typing import Any

# Two wrong forms per unit turn the grammar cloze into a DELE-style
# multiple-choice task (slug -> distractors for the correct form).
GRAMMAR_DISTRACTORS: dict[str, list[str]] = {
    "companion-a1-gustos": ["gusta", "gusto"],
    "companion-a1-ciudad": ["está", "son"],
    "companion-a1-planes": ["de", "en"],
    "companion-a1-tiempo-ropa": ["negro", "negra"],
    "companion-a1-experiencias": ["ha", "has"],
    "companion-a2-culturas": ["desde", "hago"],
    "companion-b1-reencuentros": ["ha", "hemos"],
    "companion-b1-recuerdos": ["veía", "ve"],
    "companion-b1-futuro": ["son", "serán"],
    "companion-b1-trabajo": ["sabe", "sabrá"],
    "companion-b1-buen-viaje": ["ha", "hubo"],
    "companion-b1-vivienda": ["será", "es"],
    "companion-b1-relaciones": ["podemos", "podríamos"],
    "companion-b1-gastronomia": ["pruebas", "probarás"],
    "companion-b1-consumo": ["compramos", "compraremos"],
    "companion-b2-senas-de-identidad": ["puso", "puse"],
    "companion-b2-enigmas": ["ser", "tener"],
    "companion-b2-al-limite": ["tendría", "tuve"],
    "companion-b2-referentes": ["que", "cual"],
    "companion-b2-evolucion": ["que", "quienes"],
    "companion-b2-paso-del-tiempo": ["habrá", "hubiera"],
    "companion-b2-suerte": ["encuentro", "encontraré"],
    "companion-b2-con-duende": ["El", "Un"],
    "companion-b2-con-sentido": ["juegan", "jugado"],
    "companion-b2-historia": ["está", "era"],
    "companion-b2-la-imagen": ["problemón", "problemazo"],
    "companion-b2-mas-que-palabras": ["es", "sea"],
}


def _unit(spec: dict[str, Any]) -> dict[str, Any]:
    lines = spec["lines"]
    # gTTS narration averages roughly half a second per Spanish word. Keeping
    # authored segment times close to the generated clip duration makes seeking
    # and Mi Ruta's per-clip progression work on both web and Android.
    duration = sum(len(es.split()) for es, _ in lines) * 0.49
    return {
        "slug": spec["slug"],
        "title": spec["title"],
        "cefr_level": spec["level"],
        "topics": ["Vitamina companion", *spec["topics"]],
        "source": "original companion",
        "status": "published",
        "grammar_tip": {
            "wrong": spec["wrong"],
            "right": spec["right"],
            "explanation": spec["explanation"],
        },
        "segments": [
            {
                "start": index * duration / 2,
                "end": (index + 1) * duration / 2,
                "transcript": [
                    {"es": es, "en": en}
                    for es, en in lines[index * 2 : index * 2 + 2]
                ],
                "phrases": [
                    {
                        "text": lines[index * 2][0],
                        "translation": lines[index * 2][1],
                        "tip": spec["pronunciation"],
                    }
                ],
            }
            for index in range(2)
        ],
        "exercises": [
            {
                "type": "vocabulary",
                "instructions": "Elige el significado.",
                "prompt": spec["vocab"][0],
                "options": [spec["vocab"][1], spec["distractors"][0], spec["distractors"][1]],
                "expected_answer": spec["vocab"][1],
                "skill_weights": {"vocabulary": 1.0},
            },
            {
                "type": "grammar",
                "instructions": "Completa la frase con la forma correcta.",
                "prompt": spec["grammar_prompt"],
                "options": (
                    [spec["grammar_answer"], *GRAMMAR_DISTRACTORS[spec["slug"]]]
                    if spec["slug"] in GRAMMAR_DISTRACTORS
                    else None
                ),
                "expected_answer": spec["grammar_answer"],
                "skill_weights": {"grammar": 1.0},
            },
            {
                "type": "writing",
                "instructions": "Realiza la tarea final con tus palabras.",
                "prompt": spec["task"],
                "options": None,
                "expected_answer": spec["model"],
                "skill_weights": {"writing": 1.0, "grammar": 0.4},
            },
            {
                "type": "listening",
                "instructions": "Escucha y elige.",
                "prompt": spec["listen_prompt"],
                "options": spec["listen_options"],
                "expected_answer": spec["listen_answer"],
                "audio": True,
                "skill_weights": {"listening": 1.0},
            },
            {
                "type": "pronunciation",
                "instructions": "Escucha y repite.",
                "prompt": f"Repite: {spec['repeat']}",
                "options": None,
                "expected_answer": spec["repeat"],
                "audio": True,
                "skill_weights": {"pronunciation": 1.0, "fluency": 0.5},
            },
        ],
    }


SPECS = [
    # Five units complete the existing A1 catalog: tastes, places, plans,
    # weather/clothes and first experiences mirror Vitamina A1's progression.
    dict(slug="companion-a1-gustos", title="A1 · Unidad 6: Esto me gusta", level="A1", topics=["gustos", "tiempo libre"],
         lines=[("Me encanta cocinar con mis vecinos.", "I love cooking with my neighbours."), ("A mí también, pero no me gusta correr.", "Me too, but I do not like running."), ("¿Quieres venir al cine el viernes?", "Do you want to come to the cinema on Friday?"), ("Sí, quiero ver una comedia.", "Yes, I want to see a comedy.")],
         wrong="Me gusta las películas.", right="Me gustan las películas.", explanation="Gustar concuerda con la cosa que gusta.", pronunciation="Une me y encanta con suavidad.", vocab=("tiempo libre", "free time"), distractors=["working day", "appointment"], grammar_prompt="Me ___ las comedias.", grammar_answer="gustan", task="Cuenta dos cosas que te gustan y una que no.", model="Me gusta cocinar, me encanta el cine y no me gusta correr.", listen_prompt="¿Qué película quieren ver?", listen_options=["Una comedia", "Un documental", "Una película de terror"], listen_answer="Una comedia", repeat="Me encanta cocinar con mis vecinos."),
    dict(slug="companion-a1-ciudad", title="A1 · Unidad 7: De aquí para allá", level="A1", topics=["ciudad", "direcciones"],
         lines=[("En mi barrio hay una biblioteca y dos parques.", "There is a library and two parks in my neighbourhood."), ("La estación está al lado del mercado.", "The station is next to the market."), ("¿Cómo voy al centro desde aquí?", "How do I get downtown from here?"), ("Puedes ir en metro; es rápido y fácil.", "You can go by metro; it is fast and easy.")],
         wrong="La estación hay al lado.", right="La estación está al lado.", explanation="Usamos hay para existencia y estar para ubicación.", pronunciation="Marca claramente barrio y biblioteca.", vocab=("al lado de", "next to"), distractors=["behind", "far from"], grammar_prompt="En el barrio ___ dos parques.", grammar_answer="hay", task="Describe tu barrio y recomienda un lugar.", model="En mi barrio hay un parque. Está cerca de casa y puedes pasear allí.", listen_prompt="¿Dónde está la estación?", listen_options=["Al lado del mercado", "Delante del parque", "Lejos del centro"], listen_answer="Al lado del mercado", repeat="La estación está al lado del mercado."),
    dict(slug="companion-a1-planes", title="A1 · Unidad 8: ¿Qué hacemos?", level="A1", topics=["planes", "restaurante"],
         lines=[("Tengo hambre. ¿Tomamos unas tapas?", "I am hungry. Shall we have some tapas?"), ("Buena idea. Conozco un bar tranquilo.", "Good idea. I know a quiet bar."), ("Después vamos a escuchar música en la plaza.", "Afterwards we are going to listen to music in the square."), ("Perfecto, quedamos a las ocho.", "Perfect, let us meet at eight.")],
         wrong="Vamos escuchar música.", right="Vamos a escuchar música.", explanation="Ir a más infinitivo expresa un plan próximo.", pronunciation="Mantén el ritmo de vamos a.", vocab=("quedamos", "we meet"), distractors=["we return", "we pay"], grammar_prompt="Después vamos ___ escuchar música.", grammar_answer="a", task="Propón un plan para el sábado con hora y lugar.", model="El sábado vamos a cenar. Quedamos a las ocho en la plaza.", listen_prompt="¿A qué hora quedan?", listen_options=["A las ocho", "A las siete", "A las nueve"], listen_answer="A las ocho", repeat="Perfecto, quedamos a las ocho."),
    dict(slug="companion-a1-tiempo-ropa", title="A1 · Unidad 9: Tiempo y ropa", level="A1", topics=["clima", "ropa"],
         lines=[("Hoy hace frío y está nublado.", "Today it is cold and cloudy."), ("Voy a ponerme el abrigo azul.", "I am going to put on the blue coat."), ("¿Te gustan estas botas negras?", "Do you like these black boots?"), ("Sí, pero las prefiero en marrón.", "Yes, but I prefer them in brown." )],
         wrong="El abrigo azul es muy bonita.", right="El abrigo azul es muy bonito.", explanation="El adjetivo concuerda en género y número.", pronunciation="Pronuncia las cinco vocales de forma clara.", vocab=("está nublado", "it is cloudy"), distractors=["it is windy", "it is sunny"], grammar_prompt="Las botas son ___.", grammar_answer="negras", task="Di qué tiempo hace y qué ropa vas a llevar.", model="Hace frío, así que voy a llevar un abrigo y unas botas.", listen_prompt="¿De qué color es el abrigo?", listen_options=["Azul", "Negro", "Marrón"], listen_answer="Azul", repeat="Hoy hace frío y está nublado."),
    dict(slug="companion-a1-experiencias", title="A1 · Unidad 10: Ciudadanos del mundo", level="A1", topics=["experiencias", "habilidades"],
         lines=[("¿Has viajado alguna vez a México?", "Have you ever travelled to Mexico?"), ("No, pero he visitado Colombia dos veces.", "No, but I have visited Colombia twice."), ("Sé cocinar arepas y puedo bailar salsa.", "I know how to cook arepas and I can dance salsa."), ("¡Qué interesante! Yo todavía no he aprendido.", "How interesting! I have not learned yet." )],
         wrong="He visitado Colombia ayer.", right="Visité Colombia ayer.", explanation="El perfecto conecta una experiencia con el presente; ayer pide indefinido.", pronunciation="Eleva la entonación en ¿alguna vez?.", vocab=("alguna vez", "ever"), distractors=["every day", "never again"], grammar_prompt="Yo ___ visitado Colombia.", grammar_answer="he", task="Cuenta una experiencia y una habilidad.", model="He viajado a Portugal y sé preparar una tortilla.", listen_prompt="¿Qué sabe cocinar?", listen_options=["Arepas", "Paella", "Tacos"], listen_answer="Arepas", repeat="¿Has viajado alguna vez a México?"),

    # One unit completes A2, using the final urban/cultural action theme.
    dict(slug="companion-a2-culturas", title="A2 · Unidad 10: Culturas", level="A2", topics=["convivencia", "cultura"],
         lines=[("Desde que llegué, conozco mejor las costumbres del barrio.", "Since I arrived, I understand the neighbourhood customs better."), ("Mis vecinos me han ayudado a sentirme en casa.", "My neighbours have helped me feel at home."), ("Si necesitas algo, puedes pedirlo con confianza.", "If you need something, you can ask confidently."), ("Lo más importante es escuchar y respetar otras formas de vivir.", "The most important thing is to listen and respect other ways of living." )],
         wrong="Vivo aquí desde tres años.", right="Vivo aquí desde hace tres años.", explanation="Desde hace expresa una duración que continúa ahora.", pronunciation="Enlaza desde hace sin añadir una pausa.", vocab=("sentirse en casa", "to feel at home"), distractors=["to move house", "to be alone"], grammar_prompt="Vivo aquí desde ___ tres años.", grammar_answer="hace", task="Explica una costumbre de tu comunidad y da un consejo a una persona nueva.", model="Aquí saludamos a los vecinos. Si eres nuevo, puedes presentarte y escuchar sus consejos.", listen_prompt="¿Qué han hecho los vecinos?", listen_options=["Le han ayudado", "Le han llamado", "Le han vendido una casa"], listen_answer="Le han ayudado", repeat="Mis vecinos me han ayudado a sentirme en casa."),

    # Nine units complete the B1 catalog with Vitamina B1's communicative arc.
    dict(slug="companion-b1-reencuentros", title="B1 · Unidad 1: Volver a vernos", level="B1", topics=["reencuentros", "cambios"],
         lines=[("¡Cuánto tiempo! Te veo muy cambiado.", "Long time no see! You look very different."), ("Sí, desde que nos vimos he cambiado de trabajo.", "Yes, since we last met I have changed jobs."), ("Antes vivía lejos, pero ahora trabajo desde casa.", "I used to live far away, but now I work from home."), ("Tenemos que quedar y ponernos al día.", "We must meet and catch up." )],
         wrong="Desde que nos vimos cambié mucho.", right="Desde que nos vimos he cambiado mucho.", explanation="El perfecto presenta cambios conectados con el presente.", pronunciation="Da énfasis natural a ¡cuánto tiempo!.", vocab=("ponerse al día", "to catch up"), distractors=["to be late", "to make a date"], grammar_prompt="Desde entonces ___ cambiado de trabajo.", grammar_answer="he", task="Escribe a una amistad y resume dos cambios recientes.", model="¡Cuánto tiempo! He cambiado de trabajo y ahora vivo cerca. ¿Quedamos pronto?", listen_prompt="¿Qué ha cambiado?", listen_options=["Su trabajo", "Su nombre", "Su idioma"], listen_answer="Su trabajo", repeat="Tenemos que quedar y ponernos al día."),
    dict(slug="companion-b1-recuerdos", title="B1 · Unidad 2: Recuerdos", level="B1", topics=["infancia", "anécdotas"],
         lines=[("Cuando era pequeño, jugábamos en la calle hasta tarde.", "When I was little, we played outside until late."), ("Un día perdí las llaves mientras volvía a casa.", "One day I lost the keys while returning home."), ("Estaba lloviendo y no llevaba teléfono.", "It was raining and I had no phone."), ("Al final, una vecina llamó a mis padres.", "In the end, a neighbour called my parents." )],
         wrong="Cuando era pequeño, jugué cada día.", right="Cuando era pequeño, jugaba cada día.", explanation="El imperfecto describe hábitos y contexto; el indefinido narra hechos.", pronunciation="Haz una pausa breve antes de al final.", vocab=("al final", "in the end"), distractors=["at first", "meanwhile"], grammar_prompt="Mientras yo volvía, una vecina me ___.", grammar_answer="vio", task="Narra un recuerdo con contexto, problema y final.", model="Era verano y estaba de viaje. Perdí el tren, pero al final llegué en autobús.", listen_prompt="¿Quién llamó a sus padres?", listen_options=["Una vecina", "Un profesor", "Un policía"], listen_answer="Una vecina", repeat="Cuando era pequeño, jugábamos en la calle."),
    dict(slug="companion-b1-futuro", title="B1 · Unidad 3: El mundo del futuro", level="B1", topics=["tecnología", "predicciones"],
         lines=[("Dentro de veinte años, las ciudades serán más verdes.", "In twenty years, cities will be greener."), ("Probablemente usaremos menos coches privados.", "We will probably use fewer private cars."), ("Puede que la tecnología reduzca el consumo de energía.", "Technology may reduce energy consumption."), ("Ojalá estos cambios mejoren nuestra calidad de vida.", "Hopefully these changes improve our quality of life." )],
         wrong="Puede que será más fácil.", right="Puede que sea más fácil.", explanation="Puede que y ojalá introducen subjuntivo.", pronunciation="Marca la sílaba tónica de probablemente.", vocab=("calidad de vida", "quality of life"), distractors=["cost of living", "working life"], grammar_prompt="Puede que las ciudades ___ más verdes.", grammar_answer="sean", task="Haz tres predicciones y expresa un deseo para 2040.", model="Habrá menos coches. Puede que trabajemos menos. Ojalá vivamos mejor.", listen_prompt="¿Qué usarán menos?", listen_options=["Coches privados", "Energía limpia", "Parques públicos"], listen_answer="Coches privados", repeat="Dentro de veinte años, las ciudades serán más verdes."),
    dict(slug="companion-b1-trabajo", title="B1 · Unidad 4: Trabajo", level="B1", topics=["empleo", "conciliación"],
         lines=[("Buscamos a una persona que tenga experiencia internacional.", "We are looking for someone with international experience."), ("Es importante que sepa trabajar en equipo.", "It is important that they know how to work in a team."), ("Aunque el horario es flexible, hay reuniones presenciales.", "Although the schedule is flexible, there are in-person meetings."), ("Me interesa el puesto porque permite conciliar mejor.", "I am interested in the role because it enables better work-life balance." )],
         wrong="Buscamos alguien que tiene experiencia.", right="Buscamos a alguien que tenga experiencia.", explanation="Una persona no identificada se presenta con subjuntivo.", pronunciation="Mantén el acento de experiencia y presencial.", vocab=("conciliar", "to balance work and personal life"), distractors=["to resign", "to recruit"], grammar_prompt="Buscan a alguien que ___ trabajar en equipo.", grammar_answer="sepa", task="Presenta tu perfil para un puesto y explica por qué te interesa.", model="Tengo experiencia internacional, sé trabajar en equipo y me interesa el horario flexible.", listen_prompt="¿Cómo es el horario?", listen_options=["Flexible", "Nocturno", "Fijo"], listen_answer="Flexible", repeat="Es importante que sepa trabajar en equipo."),
    dict(slug="companion-b1-buen-viaje", title="B1 · Unidad 5: Buen viaje", level="B1", topics=["viajes", "incidencias"],
         lines=[("Cuando llegamos al aeropuerto, el vuelo ya había salido.", "When we arrived at the airport, the flight had already left."), ("Resulta que habían cambiado la puerta de embarque.", "It turns out they had changed the boarding gate."), ("La compañía nos ofreció un hotel y otro vuelo.", "The airline offered us a hotel and another flight."), ("A pesar del problema, el viaje terminó bien.", "Despite the problem, the trip ended well." )],
         wrong="Cuando llegamos, el vuelo salió ya.", right="Cuando llegamos, el vuelo ya había salido.", explanation="El pluscuamperfecto indica una acción anterior a otra pasada.", pronunciation="Enlaza puerta de embarque como un grupo.", vocab=("puerta de embarque", "boarding gate"), distractors=["baggage claim", "check-in desk"], grammar_prompt="El vuelo ya ___ salido.", grammar_answer="había", task="Cuenta una incidencia de viaje y cómo se resolvió.", model="Perdí el tren porque había cambiado el horario. Compré otro billete y llegué esa noche.", listen_prompt="¿Qué ofreció la compañía?", listen_options=["Un hotel y otro vuelo", "Un reembolso", "Un taxi"], listen_answer="Un hotel y otro vuelo", repeat="Cuando llegamos, el vuelo ya había salido."),
    dict(slug="companion-b1-vivienda", title="B1 · Unidad 6: Vivienda", level="B1", topics=["barrio", "propuestas"],
         lines=[("El ayuntamiento debería crear más zonas verdes.", "The council should create more green spaces."), ("Hace falta que mejore el transporte nocturno.", "The night transport needs to be improved."), ("Si hubiera menos tráfico, el barrio sería más agradable.", "If there were less traffic, the neighbourhood would be nicer."), ("Propongo que los vecinos presentemos un plan común.", "I suggest that the neighbours submit a shared plan." )],
         wrong="Si habría menos tráfico, sería mejor.", right="Si hubiera menos tráfico, sería mejor.", explanation="En hipótesis improbables usamos si más imperfecto de subjuntivo y condicional.", pronunciation="Distingue debería y sería con ritmo claro.", vocab=("hace falta", "it is necessary"), distractors=["it is forbidden", "it is enough"], grammar_prompt="Si hubiera menos tráfico, el barrio ___ mejor.", grammar_answer="sería", task="Propón tres mejoras para tu barrio.", model="Debería haber más árboles. Hace falta mejorar el autobús y propongo crear un huerto.", listen_prompt="¿Qué quieren mejorar?", listen_options=["El transporte nocturno", "Los alquileres", "La biblioteca"], listen_answer="El transporte nocturno", repeat="Si hubiera menos tráfico, el barrio sería más agradable."),
    dict(slug="companion-b1-relaciones", title="B1 · Unidad 7: Relaciones humanas", level="B1", topics=["emociones", "desacuerdo"],
         lines=[("Me molesta que algunas personas interrumpan siempre.", "It bothers me that some people always interrupt."), ("A mí me encanta que podamos hablar con sinceridad.", "I love that we can speak honestly."), ("No estoy de acuerdo con que ignores el problema.", "I disagree with you ignoring the problem."), ("Prefiero que lo resolvamos antes de enfadarnos.", "I prefer that we solve it before getting angry." )],
         wrong="Me molesta que interrumpen.", right="Me molesta que interrumpan.", explanation="Las reacciones emocionales con que llevan subjuntivo.", pronunciation="Suaviza la d de sinceridad entre sonidos.", vocab=("con sinceridad", "honestly"), distractors=["secretly", "rudely"], grammar_prompt="Me encanta que ___ hablar así.", grammar_answer="podamos", task="Expresa una emoción, un desacuerdo y una solución.", model="Me preocupa que discutamos. No estoy de acuerdo con gritar y prefiero que hablemos tranquilos.", listen_prompt="¿Qué le molesta?", listen_options=["Que interrumpan", "Que escuchen", "Que hablen despacio"], listen_answer="Que interrumpan", repeat="Prefiero que lo resolvamos antes de enfadarnos."),
    dict(slug="companion-b1-gastronomia", title="B1 · Unidad 8: ¡Que aproveche!", level="B1", topics=["gastronomía", "finalidad"],
         lines=[("He preparado una salsa para que pruebes algo diferente.", "I prepared a sauce so that you can try something different."), ("Lleva especias que hacen que el sabor sea más intenso.", "It contains spices that make the flavour more intense."), ("Quizá te parezca picante al principio.", "It may seem spicy at first."), ("Sírvela fría para conservar mejor el aroma.", "Serve it cold to preserve the aroma better." )],
         wrong="La preparo para que pruebas.", right="La preparo para que pruebes.", explanation="Para que introduce subjuntivo cuando cambia el sujeto.", pronunciation="Pronuncia que aproveche sin cortar la frase.", vocab=("sabor intenso", "intense flavour"), distractors=["mild smell", "sweet dish"], grammar_prompt="La preparo para que la ___.", grammar_answer="pruebes", task="Explica una receta, un truco y cómo servirla.", model="Mezcla los ingredientes para que tengan más sabor. Sírvelo frío.", listen_prompt="¿Cómo hay que servir la salsa?", listen_options=["Fría", "Caliente", "Congelada"], listen_answer="Fría", repeat="He preparado una salsa para que pruebes algo diferente."),
    dict(slug="companion-b1-consumo", title="B1 · Unidad 9: Economía y consumo", level="B1", topics=["ahorro", "consumo responsable"],
         lines=[("Según la encuesta, la mayoría intenta reducir sus gastos.", "According to the survey, most people try to reduce expenses."), ("Sin embargo, uno de cada tres compra por impulso.", "However, one in three buys impulsively."), ("Es preocupante que desperdiciemos tantos productos.", "It is worrying that we waste so many products."), ("Podríamos reparar más cosas en lugar de sustituirlas.", "We could repair more things instead of replacing them." )],
         wrong="Es preocupante que desperdiciamos.", right="Es preocupante que desperdiciemos.", explanation="Las valoraciones impersonales con que suelen llevar subjuntivo.", pronunciation="Separa según la encuesta con una pausa ligera.", vocab=("comprar por impulso", "to buy impulsively"), distractors=["to save regularly", "to compare prices"], grammar_prompt="Es preocupante que ___ tanto.", grammar_answer="compremos", task="Resume un dato y recomienda dos hábitos responsables.", model="Muchas personas compran por impulso. Deberíamos comparar precios y reparar más objetos.", listen_prompt="¿Qué hace uno de cada tres?", listen_options=["Compra por impulso", "Ahorra la mitad", "Repara todo"], listen_answer="Compra por impulso", repeat="Podríamos reparar más cosas en lugar de sustituirlas."),

    # Twelve units complete the B2 catalog following Vitamina B2's Guía didáctica.
    dict(slug="companion-b2-senas-de-identidad", title="B2 · Unidad 1: Señas de identidad", level="B2", topics=["identidad", "nombres"],
         lines=[("Mi nombre es de origen árabe y significa 'la esperanza'.", "My name is of Arabic origin and means 'hope'."), ("A mí me pusieron el nombre por mi bisabuela paterna.", "I was named after my paternal great-grandmother."), ("En mi familia hay una tradición de repetir los nombres.", "In my family there is a tradition of repeating names."), ("Curiosamente, mi apellido coincide con el de una marca famosa.", "Curiously, my surname matches that of a famous brand.")],
         wrong="Me puse el nombre por mi bisabuela.", right="Me pusieron el nombre por mi bisabuela.", explanation="El plural impersonal (me pusieron) describe la decisión de otros, no la propia.", pronunciation="Pronuncia bisabuela manteniendo el diptongo ue.", vocab=("las señas de identidad", "identity traits"), distractors=["business card", "signature"], grammar_prompt="A mí me ___ el nombre por mi abuela.", grammar_answer="pusieron", task="Explica el origen de tu nombre y una tradición familiar.", model="Mi nombre viene del latín. Me lo pusieron por mi tío y en mi familia se repite cada generación.", listen_prompt="¿Por quién le pusieron ese nombre?", listen_options=["Por su bisabuela", "Por una marca", "Por un amigo"], listen_answer="Por su bisabuela", repeat="A mí me pusieron el nombre por mi bisabuela."),
    dict(slug="companion-b2-enigmas", title="B2 · Unidad 2: Enigmas", level="B2", topics=["misterio", "suposiciones"],
         lines=[("Nadie sabe qué ocurrió aquella noche en el faro.", "Nobody knows what happened that night at the lighthouse."), ("Debe de haber una explicación lógica, aunque no la conozcamos.", "There must be a logical explanation, even if we do not know it."), ("Puede que hayan exagerado los testigos después de tantos años.", "The witnesses may have exaggerated after so many years."), ("El misterio sigue siendo una incógnita para los investigadores.", "The mystery remains an enigma for researchers.")],
         wrong="Puede que ha desaparecido.", right="Puede que haya desaparecido.", explanation="Puede que exige subjuntivo: haya desaparecido.", pronunciation="Enlaza debe de haber como un solo grupo sonoro.", vocab=("la incógnita", "enigma"), distractors=["the clue", "the verdict"], grammar_prompt="Debe de ___ una explicación lógica.", grammar_answer="haber", task="Describe un misterio y haz dos suposiciones sobre lo que pasó.", model="El barco desapareció sin rastro. Debe de haber habido una tormenta y puede que la tripulación se refugiara en una isla.", listen_prompt="¿Dónde ocurrió el misterio?", listen_options=["En un faro", "En un barco", "En un museo"], listen_answer="En un faro", repeat="Debe de haber una explicación lógica."),
    dict(slug="companion-b2-al-limite", title="B2 · Unidad 3: Al límite", level="B2", topics=["experiencias", "emociones"],
         lines=[("Cuando salté en paracaídas, sentí una mezcla de miedo y euforia.", "When I went skydiving, I felt a mix of fear and euphoria."), ("Nunca olvidaré la sensación de caer hacia el vacío.", "I will never forget the feeling of falling into the void."), ("Si tuviera más valor, escalaría una montaña como esa.", "If I had more courage, I would climb a mountain like that one."), ("Si fuera más joven, viviría una aventura al límite cada año.", "If I were younger, I would live an extreme adventure every year.")],
         wrong="Si tendría más valor, lo haría.", right="Si tuviera más valor, lo haría.", explanation="Las condiciones improbables usan si + imperfecto de subjuntivo y condicional.", pronunciation="Marca el contraste de miedo y euforia con la entonación.", vocab=("el vacío", "the void"), distractors=["the summit", "the rope"], grammar_prompt="Si ___ más valor, escalaría esa montaña.", grammar_answer="tuviera", task="Cuenta una experiencia intensa y lo que harías si pudieras repetirla.", model="Salté en paracaídas y sentí euforia. Si tuviera la oportunidad, repetiría mañana mismo.", listen_prompt="¿Qué sintió al saltar?", listen_options=["Miedo y euforia", "Solo calma", "Arrepentimiento"], listen_answer="Miedo y euforia", repeat="Si tuviera más valor, escalaría una montaña."),
    dict(slug="companion-b2-referentes", title="B2 · Unidad 4: Referentes", level="B2", topics=["referentes", "logros"],
         lines=[("Mi profesora de literatura fue quien me enseñó a pensar.", "My literature teacher was the one who taught me to think."), ("Fue ella quien me animó a escribir mis primeros relatos.", "It was she who encouraged me to write my first short stories."), ("Muchas mujeres precursoras no fueron reconocidas en su época.", "Many pioneering women were not recognised in their time."), ("Hoy los influencers se han convertido en referentes para los jóvenes.", "Today influencers have become role models for young people.")],
         wrong="Fue ella que me animó.", right="Fue ella quien me animó.", explanation="En las construcciones enfáticas con fue usamos quien para personas.", pronunciation="Haz una pausa leve tras fue ella para dar énfasis.", vocab=("el referente", "role model"), distractors=["the referee", "the report"], grammar_prompt="Fue mi madre ___ me enseñó a cocinar.", grammar_answer="quien", task="Presenta a una persona que sea un referente para ti y explica por qué.", model="Mi abuela es mi referente. Fue ella quien me enseñó a trabajar duro y nunca se rindió.", listen_prompt="¿Qué le animó a hacer su profesora?", listen_options=["A escribir relatos", "A viajar lejos", "A cambiar de carrera"], listen_answer="A escribir relatos", repeat="Fue ella quien me animó a escribir."),
    dict(slug="companion-b2-evolucion", title="B2 · Unidad 5: Evolución", level="B2", topics=["reseñas", "crítica cultural"],
         lines=[("La novela, cuyo título no recuerdo, trata la evolución de una familia.", "The novel, whose title I cannot recall, deals with the evolution of a family."), ("Es una autora de quien se ha hablado mucho este año.", "She is an author people have talked about a lot this year."), ("Los críticos, quienes suelen ser duros, han elogiado su estilo.", "The critics, who are usually harsh, have praised her style."), ("En mi reseña explicaré por qué el final me decepcionó un poco.", "In my review I will explain why the ending disappointed me a little.")],
         wrong="Es una autora de que se ha hablado mucho.", right="Es una autora de quien se ha hablado mucho.", explanation="Tras preposición, para personas usamos quien o quienes, no que.", pronunciation="Pronuncia cuyo con un diptongo corto y claro.", vocab=("la reseña", "review"), distractors=["the interview", "the summary"], grammar_prompt="Es el escritor de ___ hablo.", grammar_answer="quien", task="Escribe una mini reseña con un relativo (cuyo o quien) y una valoración.", model="Leí una novela cuyos personajes evolucionan mucho. Es una escritora de quien admiro el estilo, aunque el final es lento.", listen_prompt="¿Qué le decepcionó del libro?", listen_options=["El final", "El precio", "La portada"], listen_answer="El final", repeat="Es una autora de quien se ha hablado mucho."),
    dict(slug="companion-b2-paso-del-tiempo", title="B2 · Unidad 6: El paso del tiempo", level="B2", topics=["tiempo", "nostalgia"],
         lines=[("Esta casa tiene cien años y conserva su encanto original.", "This house is a hundred years old and keeps its original charm."), ("Con el paso del tiempo, los objetos rotos adquieren un valor especial.", "With the passing of time, broken objects acquire a special value."), ("Me habría gustado conocer a mis bisabuelos.", "I would have liked to meet my great-grandparents."), ("Habríamos restaurado el reloj antiguo, pero costaba demasiado.", "We would have restored the old clock, but it cost too much.")],
         wrong="Me habría gustar conocerlos.", right="Me habría gustado conocerlos.", explanation="El condicional compuesto lleva habría más participio: habría gustado.", pronunciation="No cortes habría gustado: une las dos palabras.", vocab=("el paso del tiempo", "the passing of time"), distractors=["the weather forecast", "the time zone"], grammar_prompt="Nos ___ gustado restaurarlo.", grammar_answer="habría", task="Describe un objeto antiguo valioso y algo que te habría gustado hacer.", model="Guardo un reloj antiguo de mi abuelo. Me habría gustado restaurarlo, pero nunca encontré un buen relojero.", listen_prompt="¿Por qué no restauraron el reloj?", listen_options=["Porque costaba demasiado", "Porque estaba perdido", "Porque era nuevo"], listen_answer="Porque costaba demasiado", repeat="Me habría gustado conocer a mis bisabuelos."),
    dict(slug="companion-b2-suerte", title="B2 · Unidad 7: Suerte", level="B2", topics=["suerte", "supersticiones"],
         lines=[("Mi abuela toca madera en cuanto alguien habla de mala suerte.", "My grandmother touches wood as soon as anyone mentions bad luck."), ("Cuando encuentre un trébol de cuatro hojas, lo guardaré.", "When I find a four-leaf clover, I will keep it."), ("Muchas personas desarrollan manías para ahuyentar la mala suerte.", "Many people develop habits to ward off bad luck."), ("Yo creo que la buena suerte se construye con esfuerzo.", "I believe good luck is built through effort.")],
         wrong="En cuanto terminaré, te llamo.", right="En cuanto termine, te llamo.", explanation="Las oraciones temporales de futuro llevan subjuntivo tras cuando o en cuanto.", pronunciation="Une en cuanto y cuatro hojas sin pausa.", vocab=("ahuyentar", "to ward off"), distractors=["to attract", "to forget"], grammar_prompt="Cuando ___ un trébol, lo guardaré.", grammar_answer="encuentre", task="Habla de una superstición y de lo que harás cuando ocurra algo.", model="Tocar madera es una manía común. Cuando tenga un examen, llevaré mi amuleto de la suerte.", listen_prompt="¿Qué guardará si lo encuentra?", listen_options=["Un trébol de cuatro hojas", "Una moneda antigua", "Una herradura"], listen_answer="Un trébol de cuatro hojas", repeat="Cuando encuentre un trébol, lo guardaré."),
    dict(slug="companion-b2-con-duende", title="B2 · Unidad 8: Con duende", level="B2", topics=["encanto", "lugares"],
         lines=[("Este pueblo tiene duende: sus calles parecen salidas de un cuento.", "This village has magic: its streets look like they came out of a fairy tale."), ("Lo fascinante del lugar es la mezcla de culturas.", "The fascinating thing about the place is the mix of cultures."), ("Cada verano celebran un rito antiguo lleno de encanto.", "Every summer they celebrate an ancient rite full of charm."), ("Te propongo un plan seductor: cenar junto a la hoguera.", "I propose an enticing plan: dinner by the bonfire.")],
         wrong="El fascinante del lugar es su historia.", right="Lo fascinante del lugar es su historia.", explanation="Lo convierte un adjetivo en sustantivo abstracto: lo fascinante.", pronunciation="Deja caer la voz al final de un cuento.", vocab=("el duende", "magic charm"), distractors=["the goblin's house", "the festival ticket"], grammar_prompt="___ fascinante del lugar es su historia.", grammar_answer="Lo", task="Describe un rincón con encanto y propón un plan allí.", model="Lo fascinante de mi pueblo es su plaza antigua. Propongo cenar allí y escuchar las historias de los vecinos.", listen_prompt="¿Qué celebran cada verano?", listen_options=["Un rito antiguo", "Un mercado nuevo", "Una carrera"], listen_answer="Un rito antiguo", repeat="Lo fascinante del lugar es la mezcla de culturas."),
    dict(slug="companion-b2-con-sentido", title="B2 · Unidad 9: Con sentido", level="B2", topics=["sentidos", "memoria"],
         lines=[("El olor a café me transporta a la cocina de mi infancia.", "The smell of coffee transports me to the kitchen of my childhood."), ("Oí cantar a los pájaros mientras amanecía.", "I heard the birds singing as dawn broke."), ("Cada sentido guarda recuerdos que las palabras no explican.", "Each sense holds memories that words cannot explain."), ("Mi sentido predominante es el oído; recuerdo todas las voces.", "My predominant sense is hearing; I remember every voice.")],
         wrong="Oí a los pájaros que cantaban en el jardín.", right="Oí cantar a los pájaros en el jardín.", explanation="Con verbos de percepción preferimos el infinitivo: oí cantar.", pronunciation="Marca las vocales de amanecía con ritmo claro.", vocab=("el oído", "hearing"), distractors=["the eyesight", "the touch"], grammar_prompt="Vi ___ a los niños en el parque. (jugar)", grammar_answer="jugar", task="Describe un recuerdo asociado a un sentido.", model="El olor a pan recién hecho me transporta a mi infancia. Oía cantar a mi abuela mientras cocinaba.", listen_prompt="¿Cuál es su sentido predominante?", listen_options=["El oído", "La vista", "El olfato"], listen_answer="El oído", repeat="Oí cantar a los pájaros mientras amanecía."),
    dict(slug="companion-b2-historia", title="B2 · Unidad 10: Historia", level="B2", topics=["historia", "probabilidad"],
         lines=[("El puente fue construido en el siglo XIX y sigue en pie.", "The bridge was built in the nineteenth century and still stands."), ("¿Quién sería aquel hombre que aparece en todas las fotos?", "Who could that man be, the one who appears in all the photos?"), ("Debió de ser una época difícil para los habitantes del pueblo.", "It must have been a difficult time for the village inhabitants."), ("La historia alterna imagina qué habría pasado con otro final.", "Alternate history imagines what would have happened with a different ending.")],
         wrong="El puente está construido en 1900.", right="El puente fue construido en 1900.", explanation="La acción pasiva usa ser más participio; estar más participio describe el resultado.", pronunciation="Eleva la entonación en ¿quién sería? como suposición.", vocab=("seguir en pie", "to still stand"), distractors=["to be fashionable", "to lie down"], grammar_prompt="La muralla ___ construida en el siglo XV. (fue/está)", grammar_answer="fue", task="Haz dos suposiciones sobre un hecho histórico de tu ciudad.", model="El castillo debió de ser una fortaleza. Quien viviera allí sería una familia poderosa.", listen_prompt="¿Cuándo se construyó el puente?", listen_options=["En el siglo XIX", "En el siglo XXI", "El año pasado"], listen_answer="En el siglo XIX", repeat="Debió de ser una época difícil."),
    dict(slug="companion-b2-la-imagen", title="B2 · Unidad 11: La imagen", level="B2", topics=["imagen", "sociedad"],
         lines=[("La publicidad transmite ideas normativas sobre la imagen.", "Advertising transmits normative ideas about image."), ("Es solo un problemita; no merece tanto drama.", "It is just a little problem; it does not deserve so much drama."), ("Aquel hombretón resultó ser la persona más dulce del barrio.", "That big burly man turned out to be the sweetest person in the neighbourhood."), ("Con unas fotos y un discursito, cambió la opinión del público.", "With some photos and a little speech, he changed the audience's opinion.")],
         wrong="Queda un pocoquito de comida.", right="Queda un poquito de comida.", explanation="El diminutivo de poco es poquito, no pocoquito.", pronunciation="Suaviza la t en problemita y discursito.", vocab=("el hombretón", "big burly man"), distractors=["the young boy", "the short man"], grammar_prompt="No te preocupes, es solo un ___. (problema pequeño)", grammar_answer="problemita", task="Opina sobre la imagen en la sociedad usando un sufijo apreciativo.", model="La publicidad exagera la imagen perfecta. Un retoquete en las fotos es solo un problemita si lo tomamos con humor.", listen_prompt="¿Cómo resultó ser el hombretón?", listen_options=["Dulce", "Serio", "Tímido"], listen_answer="Dulce", repeat="Es solo un problemita; no merece tanto drama."),
    dict(slug="companion-b2-mas-que-palabras", title="B2 · Unidad 12: Más que palabras", level="B2", topics=["matices", "aprendizaje"],
         lines=[("Ser listo y estar listo no significan lo mismo.", "Ser listo and estar listo do not mean the same thing."), ("El café está frío; lo pedí hace media hora.", "The coffee is cold; I ordered it half an hour ago."), ("Mi hermano es muy abierto, pero hoy está callado.", "My brother is very open, but today he is quiet."), ("Aprender un idioma es cuestión de perspectiva y constancia.", "Learning a language is a matter of perspective and consistency.")],
         wrong="El café es frío; pídele otro.", right="El café está frío; pídele otro.", explanation="Estar con adjetivo describe un estado o cambio; ser describe un rasgo.", pronunciation="Contrasta es y está marcando la tilde.", vocab=("el matiz", "nuance"), distractors=["the mistake", "the synonym"], grammar_prompt="La sopa ___ fría; caliéntala un poco.", grammar_answer="está", task="Explica la diferencia entre ser y estar con un adjetivo que elijas.", model="Mi amiga es alegre por carácter, pero hoy está triste porque perdió su tren.", listen_prompt="¿Por qué está frío el café?", listen_options=["Lo pidió hace media hora", "No lo pidió", "Es de ayer"], listen_answer="Lo pidió hace media hora", repeat="Ser listo y estar listo no significan lo mismo."),
]


CURRICULUM_LESSONS = [_unit(spec) for spec in SPECS]
