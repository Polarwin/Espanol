"""Original companion units following Vitamina's action-oriented progression."""

from typing import Any


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
                "instructions": "Completa la frase.",
                "prompt": spec["grammar_prompt"],
                "options": None,
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
]


CURRICULUM_LESSONS = [_unit(spec) for spec in SPECS]
