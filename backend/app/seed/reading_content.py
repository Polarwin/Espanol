"""DELE-style reading tasks for every unit, matched to its CEFR level.

Each entry is a short text in an authentic exam genre (mensaje, anuncio,
correo, noticia, artículo, blog, informe) with two comprehension questions:
A1/A2 ask for concrete details; B1 adds "según el texto" formulations; B2
includes inference questions ("se deduce", "se desprende").
"""

from typing import Any

INSTRUCTIONS = {
    "A1": "Lee el texto y elige la respuesta correcta.",
    "A2": "Lee el texto y elige la opción correcta.",
    "B1": "Lee el texto. Según lo que lees, elige la opción correcta.",
    "B2": "Lee el texto y elige la opción que mejor refleja su contenido.",
}

# title -> {"passage": text, "questions": [(prompt, options, answer), ...]}
READING: dict[str, dict[str, Any]] = {
    # --- A1: mensajes, notas y anuncios cortos ---
    "En el café": {
        "passage": "Nota en la puerta del café:\n«Esta mañana, café con leche + tostada por solo 2 €. El camarero Luis os atiende en la barra. Hay mesas libres junto a la ventana».",
        "questions": [
            ("¿Cuánto cuesta la oferta de esta mañana?", ["Dos euros", "Cuatro euros", "Cinco euros"], "Dos euros"),
            ("¿Dónde hay mesas libres?", ["Junto a la ventana", "En la terraza", "En la barra"], "Junto a la ventana"),
        ],
    },
    "Primeras presentaciones": {
        "passage": "Tarjeta de presentación:\nHola, me llamo Diego y soy de Chile. Ahora vivo en Madrid con mi hermana. Soy profesor de inglés y en mi tiempo libre toco la guitarra.",
        "questions": [
            ("¿De dónde es Diego?", ["De Chile", "De Madrid", "De México"], "De Chile"),
            ("¿Qué hace Diego en su tiempo libre?", ["Toca la guitarra", "Cocina", "Corre"], "Toca la guitarra"),
        ],
    },
    "Mi familia y mi casa": {
        "passage": "Mensaje de Carmen a su amiga:\n«Vivo con mi pareja y mis dos hijos en un piso pequeño. El salón es luminoso y la cocina es nueva. Mi habitación favorita es el dormitorio de los niños, porque tiene muchos colores».",
        "questions": [
            ("¿Con quién vive Carmen?", ["Con su pareja y sus hijos", "Con sus padres", "Sola"], "Con su pareja y sus hijos"),
            ("¿Cómo es la cocina?", ["Nueva", "Vieja", "Grande"], "Nueva"),
        ],
    },
    "Un día normal": {
        "passage": "Ana escribe en su agenda:\n«Me levanto a las siete y desayuno café con tostadas. Empiezo a trabajar a las nueve. Como en casa a las dos y por la noche veo una serie».",
        "questions": [
            ("¿A qué hora empieza a trabajar Ana?", ["A las nueve", "A las siete", "A las dos"], "A las nueve"),
            ("¿Qué hace Ana por la noche?", ["Ve una serie", "Cena con amigos", "Estudia"], "Ve una serie"),
        ],
    },
    "Aprender juntos": {
        "passage": "Comentario en un foro de idiomas:\n«Aprendo español con una aplicación. Practico diez minutos todos los días y escribo las palabras nuevas en un cuaderno. Los lunes hablo con un grupo online».",
        "questions": [
            ("¿Cuánto practica esta persona cada día?", ["Diez minutos", "Una hora", "Veinte minutos"], "Diez minutos"),
            ("¿Qué hace los lunes?", ["Habla con un grupo online", "Va a clase", "Mira vídeos"], "Habla con un grupo online"),
        ],
    },
    "A1 · Unidad 6: Esto me gusta": {
        "passage": "Mensaje de Carla al grupo de amigas:\n«Me encanta el cine, pero no me gustan las películas de terror. ¿Quedamos el viernes para ver una comedia? Después puedo cocinar algo con Rosa, mi vecina».",
        "questions": [
            ("¿Qué películas no le gustan a Carla?", ["Las de terror", "Las comedias", "Los documentales"], "Las de terror"),
            ("¿Con quién cocina Carla?", ["Con su vecina Rosa", "Con su madre", "Sola"], "Con su vecina Rosa"),
        ],
    },
    "A1 · Unidad 7: De aquí para allá": {
        "passage": "Anuncio del ayuntamiento:\n«Nuestro barrio estrena biblioteca junto al mercado. Recuerda: hay dos parques cerca de la estación. Para llegar al centro, el metro es rápido y barato».",
        "questions": [
            ("¿Qué hay junto al mercado?", ["Una biblioteca", "Una estación", "Un cine"], "Una biblioteca"),
            ("¿Cómo recomienda ir al centro?", ["En metro", "En autobús", "Andando"], "En metro"),
        ],
    },
    "A1 · Unidad 8: ¿Qué hacemos?": {
        "passage": "Mensaje de Pablo:\n«El sábado quedamos a las ocho en la plaza. Primero tomamos unas tapas en un bar tranquilo que yo conozco y después escuchamos música. ¿Te apuntas?»",
        "questions": [
            ("¿A qué hora quedan?", ["A las ocho", "A las siete", "A las nueve"], "A las ocho"),
            ("¿Quién conoce el bar?", ["Pablo", "La narradora", "El camarero"], "Pablo"),
        ],
    },
    "A1 · Unidad 9: Tiempo y ropa": {
        "passage": "Pronóstico del tiempo:\n«Hoy hace frío y está nublado. Recomendamos llevar abrigo y botas. Marta elige su abrigo azul y unas botas negras; su hermana prefiere las botas marrones».",
        "questions": [
            ("¿Qué tiempo hace hoy?", ["Frío y está nublado", "Calor", "Viento"], "Frío y está nublado"),
            ("¿De qué color es el abrigo de Marta?", ["Azul", "Negro", "Marrón"], "Azul"),
        ],
    },
    "A1 · Unidad 10: Ciudadanos del mundo": {
        "passage": "Entrada de blog:\n«He viajado a Colombia dos veces y allí he aprendido a bailar salsa. Todavía no he visitado México, pero quiero ir el año que viene. También sé cocinar arepas».",
        "questions": [
            ("¿Cuántas veces ha viajado a Colombia?", ["Dos", "Una", "Tres"], "Dos"),
            ("¿Qué país quiere visitar el año que viene?", ["México", "Colombia", "Argentina"], "México"),
        ],
    },
    # --- A2: correos, anuncios y textos breves con pasado/futuro ---
    "Charla con vecinos": {
        "passage": "Nota en el portal:\n«Este fin de semana organizamos una barbacoa en el patio. Lucía traerá la ensalada y Marcos ha confirmado que lleva la bebida. Apúntate en la lista antes del viernes».",
        "questions": [
            ("¿Qué organizan los vecinos?", ["Una barbacoa", "Una fiesta de cumpleaños", "Una reunión de trabajo"], "Una barbacoa"),
            ("¿Qué lleva Marcos?", ["La bebida", "La ensalada", "El postre"], "La bebida"),
        ],
    },
    "De viaje": {
        "passage": "Correo de una agencia de viajes:\n«Mañana sale su vuelo a Lisboa. Su alojamiento está reservado cerca del centro y su billete es de ida y vuelta. El vuelo hace escala en Madrid; le recomendamos llevar solo una maleta pequeña para no facturar equipaje».",
        "questions": [
            ("¿Adónde viaja la clienta?", ["A Lisboa", "A Madrid", "A Valencia"], "A Lisboa"),
            ("¿Por qué se recomienda una maleta pequeña?", ["Para no facturar equipaje", "Porque es más barata", "Porque el vuelo es corto"], "Para no facturar equipaje"),
        ],
    },
    "Compras en el mercado": {
        "passage": "Cartel en un puesto del mercado:\n«Sábados: fruta fresca de temporada. Hoy, tomates maduros a dos euros el kilo. Y si preguntas, te ponemos también medio kilo de fresas al mismo precio».",
        "questions": [
            ("¿Cuánto cuestan los tomates?", ["Dos euros el kilo", "Tres euros el kilo", "Un euro el kilo"], "Dos euros el kilo"),
            ("¿Qué más ofrece el vendedor?", ["Medio kilo de fresas", "Un kilo de manzanas", "Pan"], "Medio kilo de fresas"),
        ],
    },
    "En la consulta": {
        "passage": "Nota de la médica:\n«Paciente con dolor de garganta y un poco de fiebre desde ayer. Diagnóstico: resfriado. Le doy una receta y le recomiendo descansar y beber mucha agua».",
        "questions": [
            ("¿Desde cuándo está enfermo el paciente?", ["Desde ayer", "Desde hace una semana", "Desde hoy"], "Desde ayer"),
            ("¿Qué recomienda la médica?", ["Descansar y beber agua", "Hacer ejercicio", "Trabajar"], "Descansar y beber agua"),
        ],
    },
    "Buscar piso": {
        "passage": "Anuncio inmobiliario:\n«Se alquila piso amueblado y luminoso cerca del centro. Dos dormitorios y ascensor. Alquiler: novecientos euros al mes, gastos incluidos. Visitas concertadas a partir de mañana».",
        "questions": [
            ("¿Cuántos dormitorios tiene el piso?", ["Dos", "Uno", "Tres"], "Dos"),
            ("¿Qué incluye el alquiler?", ["Los gastos", "Los muebles nuevos", "El garaje"], "Los gastos"),
        ],
    },
    "Vitamina A2 · U1: Vamos a conocernos": {
        "passage": "Mensaje en el foro de la clase:\n«En nuestro grupo de español hay personas de cinco países. Yo suelo quedar con una compañera de Japón para hacer excursiones los domingos. Me cuesta hablar rápido, pero ella me ayuda; tenemos mucho en común».",
        "questions": [
            ("¿Con quién queda los domingos?", ["Con una compañera de Japón", "Con su profesor", "Con su familia"], "Con una compañera de Japón"),
            ("¿Qué le cuesta a esta persona?", ["Hablar rápido", "Escribir", "Leer"], "Hablar rápido"),
        ],
    },
    "Vitamina A2 · U2: Mi lugar en el mundo": {
        "passage": "Entrada de blog:\n«Vivo en el extranjero desde hace un año. Al principio, los trámites fueron difíciles, pero ahora conozco bien las costumbres del barrio. Lo más difícil fue adaptarme al transporte público».",
        "questions": [
            ("¿Cuánto tiempo lleva la autora en el extranjero?", ["Un año", "Un mes", "Dos años"], "Un año"),
            ("¿Qué fue lo más difícil?", ["Adaptarse al transporte público", "El idioma", "El clima"], "Adaptarse al transporte público"),
        ],
    },
    "Vitamina A2 · Repaso U1–U2": {
        "passage": "Correo de la profesora:\n«Esta semana repasamos las unidades uno y dos. Cada estudiante presenta su rutina y comparamos lugares para vivir. Recuerda: el grupo de conversación practica dos veces por semana, normalmente por la tarde».",
        "questions": [
            ("¿Qué se repasa esta semana?", ["Las unidades uno y dos", "El examen final", "Los verbos irregulares"], "Las unidades uno y dos"),
            ("¿Cuándo practica el grupo normalmente?", ["Por la tarde", "Por la mañana", "Los lunes"], "Por la tarde"),
        ],
    },
    "Una ruta de senderismo": {
        "passage": "Mensaje de la organizadora:\n«El domingo hacemos una ruta por el bosque. Quedamos a primera hora en la parada de autobús. La ruta dura dos horas, así que lleva agua y calzado cómodo».",
        "questions": [
            ("¿Dónde queda el grupo?", ["En la parada de autobús", "En el bosque", "En la estación"], "En la parada de autobús"),
            ("¿Cuánto dura la ruta?", ["Dos horas", "Tres horas", "Una hora"], "Dos horas"),
        ],
    },
    "A2 · Unidad 10: Culturas": {
        "passage": "Carta al periódico local:\n«Cuando llegué al barrio, los vecinos me ayudaron a sentirme en casa: me explicaron las costumbres y me invitaron a una comida comunitaria. A quien necesite algo aquí, le aconsejo pedirlo con confianza».",
        "questions": [
            ("¿Quién ayudó a la autora al llegar?", ["Sus vecinos", "Su familia", "Sus compañeros de trabajo"], "Sus vecinos"),
            ("¿A qué la invitaron?", ["A una comida comunitaria", "A una fiesta de cumpleaños", "A un concierto"], "A una comida comunitaria"),
        ],
    },
    # --- B1: blogs, noticias y entrevistas con conectores ---
    "Mensajes con intención": {
        "passage": "Correo profesional:\n«Esta mañana he llamado para una gestión, pero la persona responsable no estaba. La recepcionista ha tomado un mensaje y me ha pedido confirmación por correo. Le he adjuntado la factura y quedo a la espera de su respuesta».",
        "questions": [
            ("¿Por qué no habló con la persona responsable?", ["Porque no estaba", "Porque no contestaba el correo", "Porque estaba de vacaciones"], "Porque no estaba"),
            ("¿Qué ha adjuntado en el correo?", ["La factura", "El currículum", "Una foto"], "La factura"),
        ],
    },
    "B1 · Unidad 1: Volver a vernos": {
        "passage": "Entrada de blog:\n«El pasado sábado me reencontré con una amiga del instituto. Había cambiado mucho: ahora trabaja desde casa y vive cerca del mar. Hemos quedado el mes que viene para ponernos al día con más tiempo».",
        "questions": [
            ("¿Dónde trabaja ahora la amiga?", ["Desde casa", "En una oficina", "En una tienda"], "Desde casa"),
            ("¿Cuándo han quedado?", ["El mes que viene", "Mañana", "El sábado"], "El mes que viene"),
        ],
    },
    "B1 · Unidad 2: Recuerdos": {
        "passage": "Relato en un foro:\n«Cuando era pequeño, mi abuelo me llevaba al río los domingos. Un día perdí mi gorra mientras pescábamos y me enfadé mucho. Al final, mi abuelo me regaló la suya y todavía la guardo».",
        "questions": [
            ("¿Qué perdió el narrador en el río?", ["Su gorra", "Su caña", "Sus llaves"], "Su gorra"),
            ("¿Qué hizo su abuelo?", ["Le regaló su gorra", "Le compró otra", "Se enfadó"], "Le regaló su gorra"),
        ],
    },
    "B1 · Unidad 3: El mundo del futuro": {
        "passage": "Noticia:\n«Según un informe publicado esta semana, las ciudades españolas serán más verdes en los próximos veinte años. Los expertos creen que se usarán menos coches privados y que la energía renovable será más barata. Sin embargo, advierten de que estos cambios requieren inversión».",
        "questions": [
            ("Según el texto, ¿qué será más barato?", ["La energía renovable", "Los coches privados", "La vivienda"], "La energía renovable"),
            ("¿Qué necesitan estos cambios?", ["Inversión", "Más tiempo", "Más coches"], "Inversión"),
        ],
    },
    "B1 · Unidad 4: Trabajo": {
        "passage": "Anuncio de empleo:\n«Empresa tecnológica de Valencia busca personal con experiencia internacional. Ofrecemos horario flexible y la posibilidad de trabajar desde casa dos días por semana. Los candidatos deben saber trabajar en equipo y enviar su currículum antes del día 30».",
        "questions": [
            ("¿Qué destaca la oferta?", ["El horario flexible", "El sueldo alto", "Los viajes"], "El horario flexible"),
            ("¿Qué deben enviar los candidatos?", ["Su currículum", "Una carta de recomendación", "Una foto"], "Su currículum"),
        ],
    },
    "B1 · Unidad 5: Buen viaje": {
        "passage": "Relato de un viajero:\n«Cuando llegamos al aeropuerto, el vuelo ya había salido porque habían cambiado la puerta de embarque. La compañía nos ofreció un hotel y otro vuelo a la mañana siguiente. A pesar de todo, llegamos a tiempo a la boda de mi prima».",
        "questions": [
            ("¿Por qué perdieron el vuelo?", ["Porque cambiaron la puerta de embarque", "Porque llegaron tarde", "Porque hubo una tormenta"], "Porque cambiaron la puerta de embarque"),
            ("¿Qué les ofreció la compañía?", ["Un hotel y otro vuelo", "Un reembolso", "Un taxi"], "Un hotel y otro vuelo"),
        ],
    },
    "B1 · Unidad 6: Vivienda": {
        "passage": "Noticia local:\n«El ayuntamiento ha anunciado un plan para crear más zonas verdes y mejorar el transporte nocturno. La asociación vecinal ha presentado una propuesta con doce mejoras para el barrio. Según la alcaldesa, las obras empezarán en primavera si el presupuesto lo permite».",
        "questions": [
            ("¿Qué ha presentado la asociación vecinal?", ["Una propuesta con mejoras", "Una queja formal", "Una fiesta"], "Una propuesta con mejoras"),
            ("Según la alcaldesa, ¿cuándo empezarán las obras?", ["En primavera", "Mañana", "El año que viene"], "En primavera"),
        ],
    },
    "B1 · Unidad 7: Relaciones humanas": {
        "passage": "Mensaje a una amiga:\n«Me molesta que algunas personas interrumpan siempre cuando hablo. Ayer lo hablé con sinceridad con mi compañero de piso y me alegró que escuchara sin enfadarse. Al final llegamos a un acuerdo sobre las tareas de la casa».",
        "questions": [
            ("¿Qué le molesta a la narradora?", ["Que la interrumpan", "Que le griten", "Que lleguen tarde"], "Que la interrumpan"),
            ("¿Sobre qué llegaron a un acuerdo?", ["Sobre las tareas de la casa", "Sobre el alquiler", "Sobre las vacaciones"], "Sobre las tareas de la casa"),
        ],
    },
    "B1 · Unidad 8: ¡Que aproveche!": {
        "passage": "Noticia gastronómica:\n«Un restaurante del barrio ha ganado un premio por su cocina tradicional. La chef explica que prepara sus salsas con especias que hacen que el sabor sea más intenso y recomienda servir los platos fríos en verano para conservar mejor el aroma».",
        "questions": [
            ("¿Por qué ha ganado el premio el restaurante?", ["Por su cocina tradicional", "Por su terraza", "Por sus precios"], "Por su cocina tradicional"),
            ("¿Qué recomienda la chef en verano?", ["Servir los platos fríos", "Cocinar sin especias", "Comer pronto"], "Servir los platos fríos"),
        ],
    },
    "B1 · Unidad 9: Economía y consumo": {
        "passage": "Artículo de consumo:\n«Según una encuesta reciente, la mayoría de las familias intenta reducir sus gastos, pero uno de cada tres consumidores compra por impulso. Los expertos recomiendan comparar precios y reparar objetos en lugar de sustituirlos».",
        "questions": [
            ("Según la encuesta, ¿qué intenta la mayoría?", ["Reducir sus gastos", "Comprar más", "Viajar más"], "Reducir sus gastos"),
            ("¿Qué recomiendan los expertos?", ["Reparar en lugar de sustituir", "Comprar por internet", "Pagar con tarjeta"], "Reparar en lugar de sustituir"),
        ],
    },
    # --- B2: artículos e informes con inferencia ---
    "B2 · Unidad 1: Señas de identidad": {
        "passage": "Artículo de sociedad:\n«Un estudio del Instituto de Onomástica revela que los nombres más frecuentes del país han cambiado menos de lo que se cree. Los investigadores subrayan que la tradición de poner a los hijos el nombre de los abuelos sigue viva en las zonas rurales. Curiosamente, cada vez más padres eligen nombres de origen árabe o latino por su significado».",
        "questions": [
            ("Según el texto, ¿qué tradición sigue viva en las zonas rurales?", ["Poner a los hijos el nombre de los abuelos", "Usar nombres de marcas", "Cambiar de apellido"], "Poner a los hijos el nombre de los abuelos"),
            ("Se deduce que los nombres del país…", ["han cambiado poco", "ya no tienen significado", "son todos modernos"], "han cambiado poco"),
        ],
    },
    "B2 · Unidad 2: Enigmas": {
        "passage": "Artículo de misterio:\n«El faro de Cabo Finisterre guarda un enigma sin resolver: en 1972, tres vigilantes desaparecieron sin dejar rastro. Debe de haber una explicación lógica, pero los investigadores no han encontrado pruebas concluyentes. Puede que los testigos hayan exagerado, o puede que el mar oculte todavía la verdad».",
        "questions": [
            ("¿Qué ocurrió en 1972?", ["Desaparecieron tres vigilantes", "Se hundió un barco", "Se quemó el faro"], "Desaparecieron tres vigilantes"),
            ("¿Qué han encontrado los investigadores?", ["Nada concluyente", "Pruebas claras", "A los vigilantes"], "Nada concluyente"),
        ],
    },
    "B2 · Unidad 3: Al límite": {
        "passage": "Noticia deportiva:\n«Una deportista valenciana ha completado la escalada de una de las montañas más peligrosas del país. Al llegar a la cima, confesó que había sentido una mezcla de miedo y euforia durante la ascensión. “Si tuviera que repetirla, lo haría mañana mismo”, declaró a los periodistas».",
        "questions": [
            ("¿Qué ha hecho la deportista?", ["Escalar una montaña peligrosa", "Cruzar un desierto", "Saltar en paracaídas"], "Escalar una montaña peligrosa"),
            ("¿Qué declaró a los periodistas?", ["Que repetiría la experiencia", "Que no volvería a intentarlo", "Que tuvo un accidente"], "Que repetiría la experiencia"),
        ],
    },
    "B2 · Unidad 4: Referentes": {
        "passage": "Noticia cultural:\n«La universidad ha rendido homenaje a varias mujeres precursoras de la ciencia que no fueron reconocidas en su época. Fue una estudiante quien propuso la iniciativa, y fueron sus profesores quienes la apoyaron. El acto ha reunido a investigadoras que hoy son referentes para las nuevas generaciones».",
        "questions": [
            ("¿Quién propuso la iniciativa?", ["Una estudiante", "Una profesora", "La rectora"], "Una estudiante"),
            ("Se desprende del texto que las mujeres homenajeadas…", ["no tuvieron reconocimiento en vida", "fueron profesoras famosas", "trabajaron en la universidad"], "no tuvieron reconocimiento en vida"),
        ],
    },
    "B2 · Unidad 5: Evolución": {
        "passage": "Reseña literaria:\n«La nueva novela de Carmen Ruiz, cuyo título hace referencia al paso del tiempo, ha recibido elogios de los críticos. Es una autora de quien se destaca el estilo cuidado, aunque algunos lectores opinan que el final resulta demasiado lento. En las reseñas se subraya la evolución de sus personajes».",
        "questions": [
            ("¿Qué han hecho los críticos con la novela?", ["Elogiarla", "Criticarla duramente", "Ignorarla"], "Elogiarla"),
            ("¿Qué opinan algunos lectores del final?", ["Que es demasiado lento", "Que es perfecto", "Que es confuso"], "Que es demasiado lento"),
        ],
    },
    "B2 · Unidad 6: El paso del tiempo": {
        "passage": "Noticia local:\n«Un taller de restauración ha devuelto la vida a un reloj de la plaza que llevaba cuarenta años parado. Los vecinos habrían pagado cualquier precio por conservarlo, pero el ayuntamiento ha asumido el coste. Con el paso del tiempo, el reloj se había convertido en un símbolo del barrio».",
        "questions": [
            ("¿Cuánto tiempo llevaba parado el reloj?", ["Cuarenta años", "Cien años", "Una década"], "Cuarenta años"),
            ("Se deduce que para los vecinos el reloj…", ["tiene un gran valor sentimental", "ya no importa", "era demasiado caro"], "tiene un gran valor sentimental"),
        ],
    },
    "B2 · Unidad 7: Suerte": {
        "passage": "Artículo de psicología:\n«Una encuesta sobre supersticiones revela que uno de cada cuatro españoles toca madera cuando alguien habla de mala suerte. Muchos entrevistados admiten que llevan un amuleto a los exámenes y que evitan pasar bajo las escaleras. Los psicólogos explican que estas manías dan una sensación de control».",
        "questions": [
            ("¿Cuántos españoles tocan madera, según la encuesta?", ["Uno de cada cuatro", "Uno de cada tres", "La mitad"], "Uno de cada cuatro"),
            ("Según los psicólogos, ¿qué dan estas manías?", ["Sensación de control", "Mala suerte", "Estrés"], "Sensación de control"),
        ],
    },
    "B2 · Unidad 8: Con duende": {
        "passage": "Artículo de viajes:\n«Un pueblo de montaña ha sido elegido uno de los rincones con más encanto del país. Lo fascinante del lugar es la mezcla de culturas que se respira en sus calles empedradas. Cada verano, los vecinos celebran un rito antiguo junto a la hoguera que atrae a cientos de visitantes».",
        "questions": [
            ("¿Qué es lo fascinante del pueblo?", ["La mezcla de culturas", "Su playa", "Su gastronomía"], "La mezcla de culturas"),
            ("¿Cuándo celebran el rito antiguo?", ["Cada verano", "Cada invierno", "Cada mes"], "Cada verano"),
        ],
    },
    "B2 · Unidad 9: Con sentido": {
        "passage": "Artículo científico:\n«Un experimento con voluntarios ha demostrado que el olfato es el sentido que despierta recuerdos más intensos. Los participantes oían una canción, veían fotos antiguas y olían diferentes aromas mientras describían su infancia. Los investigadores creen que la memoria sensorial podría ayudar a personas con pérdida de memoria».",
        "questions": [
            ("¿Qué sentido despierta recuerdos más intensos?", ["El olfato", "El oído", "La vista"], "El olfato"),
            ("¿A quiénes podría ayudar este descubrimiento?", ["A personas con pérdida de memoria", "A niños pequeños", "A músicos"], "A personas con pérdida de memoria"),
        ],
    },
    "B2 · Unidad 10: Historia": {
        "passage": "Noticia de arqueología:\n«Unos trabajos de renovación han sacado a la luz una muralla que fue construida en el siglo XV. Los historiadores creen que debió de ser una época de gran actividad comercial en la ciudad. “Quien viviera detrás de estos muros sería una familia poderosa”, explica la arqueóloga responsable».",
        "questions": [
            ("¿Cuándo fue construida la muralla?", ["En el siglo XV", "En el siglo XIX", "En la época romana"], "En el siglo XV"),
            ("¿Qué creen los historiadores sobre esa época?", ["Que fue de gran actividad comercial", "Que fue de guerra constante", "Que fue una época tranquila"], "Que fue de gran actividad comercial"),
        ],
    },
    "B2 · Unidad 11: La imagen": {
        "passage": "Informe sobre publicidad:\n«Un informe sobre publicidad digital advierte de que las imágenes retocadas transmiten ideas normativas sobre la belleza. Los expertos recomiendan etiquetar los retoques para que el público, especialmente los jóvenes, pueda distinguir la realidad de la ficción. “No es un problemita, es un problemón”, afirma una de las autoras».",
        "questions": [
            ("¿Qué recomiendan los expertos?", ["Etiquetar los retoques", "Prohibir la publicidad", "Usar más filtros"], "Etiquetar los retoques"),
            ("¿Qué afirma una de las autoras?", ["Que es un problemón", "Que es un problemita", "Que no es importante"], "Que es un problemón"),
        ],
    },
    "B2 · Unidad 12: Más que palabras": {
        "passage": "Artículo de divulgación:\n«Un equipo de lingüistas ha analizado cómo los hispanohablantes eligen entre ser y estar con el mismo adjetivo. El estudio muestra que ser listo y estar listo no significan lo mismo, y que la elección depende de la perspectiva del hablante. Los investigadores han creado una herramienta para buscar combinaciones frecuentes de palabras».",
        "questions": [
            ("¿De qué depende la elección entre ser y estar?", ["De la perspectiva del hablante", "Del país", "De la edad"], "De la perspectiva del hablante"),
            ("¿Qué han creado los investigadores?", ["Una herramienta para buscar combinaciones", "Un diccionario", "Una aplicación de citas"], "Una herramienta para buscar combinaciones"),
        ],
    },
}


def enrich_reading(lessons: list[dict[str, Any]]) -> None:
    """Append DELE-style reading-comprehension exercises at each unit's level."""
    for lesson in lessons:
        entry = READING.get(lesson["title"])
        if not entry:
            continue
        instructions = INSTRUCTIONS.get(lesson["cefr_level"], INSTRUCTIONS["A1"])
        for prompt, options, answer in entry["questions"]:
            lesson["exercises"].append(
                {
                    "type": "reading",
                    "instructions": instructions,
                    "prompt": prompt,
                    "passage": entry["passage"],
                    "options": options,
                    "expected_answer": answer,
                    "skill_weights": {"reading": 1.0},
                }
            )
