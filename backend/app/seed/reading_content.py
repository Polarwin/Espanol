"""DELE-style reading tasks for every unit, matched to its CEFR level.

Each entry is a short text in an authentic exam genre (mensaje, anuncio,
correo, noticia, artículo, blog, informe) with two comprehension questions:
A1/A2 ask for concrete details; B1 adds "según el texto" formulations; B2
includes inference questions ("se deduce", "se desprende"). C1/C2 use longer,
genre-framed texts (artículo de opinión, reseña, crónica, ensayo breve) and
add inference, attitude and tone items ("la intención del autor", "el tono
del texto").
"""

from typing import Any

INSTRUCTIONS = {
    "A1": "Lee el texto y elige la respuesta correcta.",
    "A2": "Lee el texto y elige la opción correcta.",
    "B1": "Lee el texto. Según lo que lees, elige la opción correcta.",
    "B2": "Lee el texto y elige la opción que mejor refleja su contenido.",
    "C1": "Lee el texto y elige la opción que mejor refleja su contenido y la intención del autor.",
    "C2": "Lee el texto y elige la opción que mejor recoge su contenido, la intención y el tono del autor.",
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
    # --- C1: artículos de opinión, reseñas, crónicas y ensayos con inferencia y actitud ---
    "C1 · Unidad 1: Individuo": {
        "passage": "Artículo de opinión:\n«Se ha puesto de moda hablar de la autenticidad como si fuera una mercancía más: algo que se exhibe, se mide y, en última instancia, se vende. Sin embargo, quienes defienden esa autenticidad de escaparate olvidan que el individuo se construye precisamente en los márgenes, en aquello que no se cuenta ni se etiqueta. No estoy diciendo que deba uno esconderse; digo que la identidad es un proceso y no un producto terminado. Las redes sociales premian la coherencia inmediata, esa marca personal que nunca duda, mientras que dudar, contradecirse y cambiar de opinión son quizá las señas más honestas de una persona. Me pregunto si el empeño en parecer únicos no nos estará haciendo sospechosamente parecidos. Tal vez la verdadera singularidad consista en aceptar que somos, ante todo, una suma provisional de influencias, recuerdos y contradicciones que no caben en ningún perfil».",
        "questions": [
            ("¿Cuál es la intención principal del autor?", ["Cuestionar la idea de autenticidad que se vende en las redes", "Enseñar a crear una marca personal", "Animar a usar más las redes sociales"], "Cuestionar la idea de autenticidad que se vende en las redes"),
            ("Según el texto, ¿qué premian las redes sociales?", ["La coherencia inmediata", "Las contradicciones", "El cambio de opinión"], "La coherencia inmediata"),
        ],
    },
    "C1 · Unidad 2: Tiempo libre": {
        "passage": "Crónica:\n«Los domingos por la mañana, la plaza de Chamberí se llena de un rumor peculiar: el chasquido de las fichas de dominó contra las mesas de mármol. Llevo meses acudiendo a este club improvisado que reunió en su día a jubilados del barrio y que ahora atrae también a estudiantes y teletrabajadores con horarios imposibles. Nadie cobra entrada ni reparte premios; el único requisito es respetar el turno y aguantar las bromas de Marcial, el decano, que a sus ochenta y dos años recuerda cada partida jugada desde 1998. Conversando con él, uno comprende que el tiempo libre no siempre necesita una aplicación que lo organice ni una foto que lo certifique. A veces basta una mesa, cuatro vecinos y la lentitud deliberada de quien no tiene ninguna prisa por llegar a ninguna parte. Quizá por eso, cuando suena el mediodía, cuesta tanto recoger las fichas».",
        "questions": [
            ("Se deduce que la narradora valora el club porque…", ["ofrece un ocio sencillo y sin prisas", "reparte premios todos los domingos", "está organizado por una aplicación"], "ofrece un ocio sencillo y sin prisas"),
            ("¿Qué papel tiene Marcial en el club?", ["Es el decano, que recuerda las partidas antiguas", "Es el dueño de la plaza", "Es un estudiante recién llegado"], "Es el decano, que recuerda las partidas antiguas"),
        ],
    },
    "C1 · Unidad 3: Mundo laboral": {
        "passage": "Artículo de opinión:\n«El teletrabajo se ha instalado entre nosotros con la naturalidad de quien siempre estuvo ahí, pero sus efectos más profundos aún están por verse. Trabajar desde casa ha devuelto a muchas personas horas de transporte y una flexibilidad impensable hace una década; sin embargo, también ha difuminado la frontera entre la oficina y el salón, convirtiendo la cocina en sala de reuniones y la noche en prolongación de la jornada. Los defensores del modelo presencial alegan que la creatividad necesita del encuentro casual, de esa conversación junto a la máquina de café que ninguna videollamada reproduce. Los del modelo a distancia responden que la confianza se demuestra con autonomía y no con fichajes. Probablemente ambos tengan razón a medias. Lo que parece claro es que el debate ya no trata de dónde trabajamos, sino de qué tipo de vida queremos construir alrededor del trabajo».",
        "questions": [
            ("La intención del autor es…", ["reflexionar sobre los efectos del teletrabajo en la vida", "demostrar que el trabajo presencial es mejor", "criticar a las empresas tecnológicas"], "reflexionar sobre los efectos del teletrabajo en la vida"),
            ("Según el texto, ¿qué alegan los defensores del modelo presencial?", ["Que la creatividad necesita del encuentro casual", "Que el transporte es demasiado caro", "Que las videollamadas son ilegales"], "Que la creatividad necesita del encuentro casual"),
        ],
    },
    "C1 · Unidad 4: Experiencia gastronómica": {
        "passage": "Reseña de restaurante:\n«No todos los días se encuentra uno con un restaurante que cumpla lo que promete sin aspavientos. La Taberna del Puerto, regentada por los hermanos Sotelo desde hace tres décadas, es de esos locales que no necesitan carta de treinta platos: bastan seis guisos de temporada y una vitrina con el pescado del día. El arroz caldoso con bogavante, servido sin prisa y con el punto justo de fumet, justifica por sí solo la espera en la barra. Menos afortunado resulta el comedor, algo ruidoso cuando el local se llena, y la carta de vinos, correcta pero poco ambiciosa. El servicio, cercano sin ser invasivo, redondea una experiencia que apuesta por el producto por encima de cualquier postureo. Sale uno con la sensación de haber pagado un precio honesto por una cocina honesta, algo que hoy, por desgracia, empieza a ser noticia».",
        "questions": [
            ("Según la reseña, ¿qué aspecto del restaurante se critica?", ["El comedor ruidoso y la carta de vinos", "La calidad del pescado", "La lentitud del servicio"], "El comedor ruidoso y la carta de vinos"),
            ("El tono general de la reseña es…", ["positivo, con algunas reservas menores", "duramente negativo", "completamente neutro"], "positivo, con algunas reservas menores"),
        ],
    },
    "C1 · Unidad 5: Alternativas ambientales": {
        "passage": "Ensayo breve:\n«Los cafés de reparación que han surgido en los barrios de media Europa plantean una pregunta incómoda: ¿cuándo decidimos que arreglar era cosa de nostálgicos? Durante décadas, la economía del usar y tirar se nos vendió como progreso, y reparar un electrodoméstico pasó a costar más que comprar uno nuevo. Frente a esta lógica, estos espacios comunitarios recuperan oficios casi perdidos y, sobre todo, una manera distinta de relacionarse con los objetos. No se trata solo de ahorrar recursos, que también, sino de comprender que cada aparato desechado antes de tiempo representa energía, materiales y horas de trabajo que no vuelven. Sería ingenuo pensar que un café de reparación va a frenar el cambio climático por sí solo. Pero sería igual de ingenuo despreciar el poder de un gesto que, repetido miles de veces, empieza a cambiar la cultura del consumo desde abajo».",
        "questions": [
            ("Se deduce que los cafés de reparación…", ["recuperan oficios y otra relación con los objetos", "venden electrodomésticos nuevos", "son negocios muy rentables"], "recuperan oficios y otra relación con los objetos"),
            ("¿Qué actitud adopta el autor hacia estos espacios?", ["Los considera valiosos, aunque no milagrosos", "Los desprecia por nostálgicos", "Cree que frenarán el cambio climático por sí solos"], "Los considera valiosos, aunque no milagrosos"),
        ],
    },
    "C1 · Unidad 6: Educación": {
        "passage": "Ensayo breve:\n«Cada cierto tiempo, el debate educativo español vuelve a enfrentar a dos fantasmas: el de la memorización pura y el de la creatividad sin contenidos. La dicotomía es falsa, y sin embargo sigue condicionando leyes, programas y conversaciones de patio. Memorizar sin comprender produce alumnos que recitan sin pensar; pero fomentar el pensamiento crítico sin una base sólida de conocimientos produce opiniones sin fundamento. La experiencia de los países con mejores resultados sugiere que el equilibrio no es un término medio perezoso, sino una secuencia: primero dominar los contenidos básicos, después aprender a interrogarlos. Quizá el verdadero problema no esté en elegir un bando, sino en la precariedad de quienes deberían aplicar cualquier pedagogía: docentes sobrecargados, ratios imposibles y una formación permanente que se financia con buenas intenciones. Sin maestros bien tratados, todo debate metodológico es pura teoría».",
        "questions": [
            ("Según el autor, ¿en qué consiste el equilibrio educativo?", ["En dominar primero los contenidos y luego interrogarlos", "En elegir entre memorizar y crear", "En eliminar los exámenes"], "En dominar primero los contenidos y luego interrogarlos"),
            ("¿Cuál es, para el autor, el verdadero problema de la educación?", ["La precariedad de los docentes", "Los alumnos que memorizan", "Las leyes educativas extranjeras"], "La precariedad de los docentes"),
        ],
    },
    "C1 · Unidad 7: Paisajes urbanos": {
        "passage": "Crónica:\n«El mercado de la Cebada amanece estos días entre andamios. Donde antes se alineaban los puestos de fruta de toda la vida, ahora conviven paradistas veteranos con obreros, turistas despistados y arquitectos con cascos blancos. La reforma, prometida desde hace quince años, llega por fin, y con ella la mezcla habitual de esperanza y recelo. Los vecinos celebran que el edificio deje de gotear cada vez que llueve, pero temen que el nuevo mercado, moderno y luminoso, acabe siendo otra sucursal más de las cadenas que ya pueblan el barrio. Carmen, que lleva cuarenta años vendiendo pescado, resume el ambiente con una frase: que mejoren el techo, pero que no nos quiten el alma. La ciudad, una vez más, se enfrenta a su dilema eterno: cómo renovarse sin convertirse en el decorado de sí misma».",
        "questions": [
            ("¿Qué temen los vecinos del nuevo mercado?", ["Que acabe siendo una sucursal más de las cadenas", "Que las obras se retrasen de nuevo", "Que llueva dentro del edificio"], "Que acabe siendo una sucursal más de las cadenas"),
            ("Se deduce que Carmen…", ["quiere mejoras sin perder la identidad del mercado", "se opone a cualquier reforma", "lleva poco tiempo en el barrio"], "quiere mejoras sin perder la identidad del mercado"),
        ],
    },
    "C1 · Unidad 8: Geografías y viajes": {
        "passage": "Crónica de viajes:\n«Viajar despacio es una forma de resistencia. Lo descubrí en el tren regional que une León con Gijón, tres horas de paisaje por las que ningún pasajero pagaría un suplemento de velocidad. En mi compartimento, una mujer mayor señalaba por la ventana cada pueblo donde había pasado un verano de su infancia; en el vagón cafetería, dos ciclistas estudiaban un mapa de papel como si el teléfono no existiera. El turismo de imprescindibles, ese que colecciona monumentos como quien sella un pasaporte, nos ha enseñado a mirar sin ver. Frente a él, el viaje lento propone otra economía de la mirada: menos destinos, más permanencia; menos fotos, más conversaciones con desconocidos. No es una cuestión de dinero ni de edad, sino de disponibilidad interior. Al llegar a la costa, llovía, y a nadie del tren pareció importarle demasiado».",
        "questions": [
            ("¿Qué propone el viaje lento, según la autora?", ["Menos destinos y más permanencia", "Coleccionar más monumentos", "Viajar siempre en avión"], "Menos destinos y más permanencia"),
            ("El tono de la crónica hacia el turismo de imprescindibles es…", ["crítico", "admirado", "indiferente"], "crítico"),
        ],
    },
    "C1 · Unidad 9: Deporte y bienestar": {
        "passage": "Artículo de opinión:\n«El deporte amateur vive una paradoja curiosa: nunca hubo tantas personas corriendo por los parques y nunca fue tan difícil encontrar a alguien que corra sin auriculares, reloj inteligente y aplicación que registre cada zancada. La medición constante ha traído beneficios evidentes (motivación, prevención de lesiones, comunidades virtuales de apoyo), pero también ha convertido el ocio en una segunda jornada laboral, con sus objetivos, sus informes y sus comparaciones. Varios estudios recientes advierten de que una parte de los deportistas populares entrena más para alimentar su estadística que para disfrutar del esfuerzo. Nadie sugiere volver a la sandalia de esparto; se trata, más bien, de recuperar algo que el deporte siempre ofreció gratis: el aburrimiento fecundo de una carrera sin cronómetro, la conversación a pie de pista, la aceptación de que no toda actividad necesita ser optimizada para merecer la pena».",
        "questions": [
            ("Se deduce del texto que la medición constante del deporte…", ["puede convertir el ocio en una obligación", "siempre perjudica la salud", "ha acabado con el deporte amateur"], "puede convertir el ocio en una obligación"),
            ("¿Qué defiende el autor al final?", ["Recuperar el disfrute del deporte sin optimizarlo todo", "Entrenar solo con reloj inteligente", "Volver a la sandalia de esparto"], "Recuperar el disfrute del deporte sin optimizarlo todo"),
        ],
    },
    "C1 · Unidad 10: Economía y negocios": {
        "passage": "Artículo de opinión:\n«Cada vez que cierra una tienda de barrio, los comentarios se repiten: qué pena, era de toda la vida. Pero la pena, por sincera que sea, no paga alquileres. El pequeño comercio agoniza bajo una doble presión: la de las plataformas digitales, que venden comodidad a precios imposibles, y la de los alquileres comerciales, que crecen al ritmo de la especulación y no de las ventas. Frente a esto, algunos barrios ensayan respuestas interesantes: bonos de consumo local, cooperativas de reparto propio, mercadillos que combinan tienda física y pedido en línea. Ninguna de estas fórmulas es milagrosa, y probablemente ninguna salve por sí sola a la librería de la esquina. Pero plantean la pregunta correcta: no si el comercio de proximidad puede sobrevivir, sino qué tipo de ciudad queremos cuando las calles se queden sin escaparates. Porque una ciudad sin tiendas no es más barata; es, sencillamente, más pobre».",
        "questions": [
            ("Según el autor, ¿cuál es la pregunta correcta sobre el pequeño comercio?", ["Qué tipo de ciudad queremos cuando desaparezcan las tiendas", "Cómo comprar más por internet", "Cuánto subirán los alquileres"], "Qué tipo de ciudad queremos cuando desaparezcan las tiendas"),
            ("La frase final sugiere que la pérdida del comercio local…", ["empobrece la vida de la ciudad", "hace subir los precios", "es inevitable y positiva"], "empobrece la vida de la ciudad"),
        ],
    },
    "C1 · Unidad 11: Palabras, palabras": {
        "passage": "Ensayo breve:\n«Los diccionarios, nos guste o no, llegan siempre tarde a la fiesta. Cuando una palabra nueva aparece por fin en sus páginas, lleva años circulando por las conversaciones, los titulares y los mensajes de los adolescentes. Este retraso no es un defecto, sino la prueba de que la lengua pertenece a quienes la hablan y no a quienes la registran. Ahora bien, reconocer esto no obliga a aplaudirlo todo. La velocidad actual del cambio léxico, alimentada por las redes y por el préstamo indiscriminado del inglés, plantea un problema real: no el de la pureza, concepto discutible, sino el de la comunicación entre generaciones. Cuando un abuelo y su nieto necesitan traductor para hablar del trabajo, algo se ha roto. La actitud razonable no es ni la alarma ni la unción de cada novedad, sino la curiosidad crítica: preguntarse qué necesidad cubre cada palabra nueva y qué palabra antigua estamos dejando morir al adoptarla».",
        "questions": [
            ("Según el texto, ¿qué demuestra el retraso de los diccionarios?", ["Que la lengua pertenece a quienes la hablan", "Que los diccionarios son inútiles", "Que los adolescentes escriben mal"], "Que la lengua pertenece a quienes la hablan"),
            ("¿Qué actitud considera razonable el autor ante las palabras nuevas?", ["La curiosidad crítica", "La alarma", "Aplaudirlo todo"], "La curiosidad crítica"),
        ],
    },
    "C1 · Unidad 12: Siglo XXI": {
        "passage": "Artículo de opinión:\n«Se habla mucho de la atención como la nueva moneda del siglo XXI, pero quizá convendría precisar el símil: nuestra atención no es una moneda que gastamos, sino un recurso que nos extraen. Las plataformas digitales compiten por ella con algoritmos diseñados para interrumpir, precisamente porque la interrupción es rentable. Frente a esta economía extractiva, han surgido movimientos que reivindican el derecho a la desconexión, aplicaciones que prometen calma y hasta retiros sin teléfono que se pagan a precio de hotel de lujo. La ironía es evidente: convertimos hasta el silencio en producto. Tal vez la respuesta no pase por comprar herramientas contra la distracción, sino por recuperar hábitos que nunca debimos abandonar: leer textos largos, pasear sin destino, mantener conversaciones que no se interrumpen cada treinta segundos. El siglo XXI no será recordado por sus inventos, sino por cómo decidimos vivir con ellos».",
        "questions": [
            ("¿A qué se refiere el autor al hablar de «economía extractiva»?", ["A que las plataformas extraen nuestra atención", "A la minería del siglo XXI", "A la venta de aplicaciones de calma"], "A que las plataformas extraen nuestra atención"),
            ("Se deduce que el autor ve con ironía…", ["que hasta el silencio se haya convertido en producto", "los paseos sin destino", "la lectura de textos largos"], "que hasta el silencio se haya convertido en producto"),
        ],
    },
    # --- C2: textos formales con ironía, matización y preguntas de tono e intención ---
    "C2 · Unidad 1: Retórica y debate": {
        "passage": "Ensayo breve:\n«La oratoria política contemporánea padece una curiosa metamorfosis: cuanto más sofisticados se vuelven los instrumentos de medición del discurso, más elemental resulta el discurso medido. El debate parlamentario, concebido en su origen como confrontación de argumentos, ha devendido con frecuencia en sucedáneo televisivo donde la réplica se sustituye por el titular y la refutación, por el aspaviento. No se trata de idealizar un pasado que también conoció sus demagogos, sino de constatar un desplazamiento: el éxito ya no se evalúa por la solidez del razonamiento, sino por la viralidad del fragmento. Que esta transformación responda a incentivos del mercado informativo resulta plausible; que sea irreversible, menos. La recuperación de la retórica como disciplina ciudadana, no como artefacto de persuasión sino como ejercicio de escucha argumentada, constituiría, a juicio de quien esto escribe, la reforma institucional más urgente y, previsiblemente, la menos aplaudida».",
        "questions": [
            ("El tono del texto es…", ["crítico y reflexivo, con cierta ironía", "entusiasta y celebratorio", "puramente descriptivo"], "crítico y reflexivo, con cierta ironía"),
            ("Se deduce que, para el autor, el éxito del discurso político actual se mide por…", ["la viralidad del fragmento", "la solidez del razonamiento", "el número de asistentes al debate"], "la viralidad del fragmento"),
        ],
    },
    "C2 · Unidad 2: Lengua y sociedad": {
        "passage": "Artículo de opinión:\n«Pocas cuestiones concentran tanta pasión con tan escasa evidencia como el debate sobre el lenguaje inclusivo. A un lado, quienes sostienen que la lengua moldea la realidad y que, en consecuencia, toda innovación morfológica constituye un avance democrático; al otro, quienes denuncian una ingeniería social disfrazada de cortesía gramatical. Cabría preguntarse, sin embargo, si ambos contendientes no sobrestiman el poder de la norma y subestiman el del uso. La historia de las lenguas ofrece escasos ejemplos de reformas impuestas desde arriba que hayan prosperado, y numerosos ejemplos de usos espontáneos que acabaron por imponerse sin decreto alguno. Lo que la controversia oculta es una constatación más incómoda: las desigualdades que se pretenden corregir por vía léxica suelen requerir intervenciones de otra índole: laborales, educativas, económicas. Cambiar una desinencia resulta, al fin y al cabo, considerablemente más económico que cambiar un salario».",
        "questions": [
            ("La intención del autor es…", ["matizar el debate mostrando los límites de ambas posturas", "defender el lenguaje inclusivo sin matices", "atacar a las instituciones lingüísticas"], "matizar el debate mostrando los límites de ambas posturas"),
            ("¿Qué sugiere la frase final del texto?", ["Que corregir desigualdades reales cuesta más que cambiar la gramática", "Que cambiar una desinencia es muy caro", "Que los salarios dependen de la lengua"], "Que corregir desigualdades reales cuesta más que cambiar la gramática"),
        ],
    },
    "C2 · Unidad 3: Ciencia y divulgación": {
        "passage": "Reseña de ensayo:\n«El último ensayo de Lucía Ferrán, El azar domesticado, llega a las librerías precedido de una expectación que la propia autora, con prudencia encomiable, se ha encargado de moderar. La tesis central, según la cual la estadística, lejos de ser un instrumento técnico, constituye una gramática de la incertidumbre cotidiana, se expone con una elegancia expositiva poco frecuente en un género que tiende a oscilar entre la simplificación condescendiente y la jerga inexpugnable. Ferrán evita ambos escollos, aunque no siempre: los capítulos dedicados a la inteligencia artificial, por momentos, sucumben a esa tentación tan propia del divulgador de confundir lo verosímil con lo demostrado. Son, en cualquier caso, deslices menores en una obra que logra lo esencial: hacer sentir al lector no que ha comprendido la estadística, sino que ha estado toda la vida pensando estadísticamente sin saberlo. Distinción sutil, y quizá la única que importa».",
        "questions": [
            ("Según la reseña, ¿qué defecto se señala en algunos capítulos?", ["Confunden lo verosímil con lo demostrado", "Abusan de las estadísticas", "Son demasiado cortos"], "Confunden lo verosímil con lo demostrado"),
            ("El tono de la reseña es…", ["favorable, aunque con reservas precisas", "demoledor", "indiferente"], "favorable, aunque con reservas precisas"),
        ],
    },
    "C2 · Unidad 4: Literatura": {
        "passage": "Reseña literaria:\n«Releer ahora Los inviernos de la casa, la novela que consagró a Andrés Solana hace cuarenta años, permite comprobar hasta qué punto el prestigio literario se nutre tanto del olvido como del recuerdo. La prosa de Solana, celebrada entonces por su sobriedad, revela hoy una economía expresiva que roza la avaricia: frases de una contundencia casi hostil que el lector contemporáneo, acostumbrado a la sobreexplicación, recibe con desconcierto. La trama, el deterioro silencioso de una familia de industriales asturianos, interesa menos que el punto de vista: una narradora que miente sin que el texto se permita jamás desmentirla. Ahí reside la modernidad intacta de la novela. Si algo ha envejecido es su envoltorio moral, esa severidad con el mundo rural que los críticos de la época confundieron con lucidez. Recomendable, en suma, con la advertencia de que no estamos ante una obra maestra intocable, sino ante algo mejor: una obra maestra discutible».",
        "questions": [
            ("¿Qué considera la reseñista que ha envejecido de la novela?", ["Su envoltorio moral", "El punto de vista narrativo", "La economía expresiva de la prosa"], "Su envoltorio moral"),
            ("Se deduce que para la reseñista el prestigio literario…", ["depende tanto del olvido como del recuerdo", "es siempre merecido", "desaparece con los años"], "depende tanto del olvido como del recuerdo"),
        ],
    },
    "C2 · Unidad 5: Medios y opinión": {
        "passage": "Artículo de opinión:\n«El periodismo de opinión atraviesa una edad de oro que, según se mire, podría pasar por su ocaso. Nunca hubo tantas columnas, tantos análisis, tantas firmas; y rara vez el conjunto produjo una sensación tan uniforme de déjà vu. La explicación no es misteriosa: el columnista contemporáneo no escribe para convencer al escéptico, sino para confirmar al converso, y ese cometido exige una previsibilidad que el oficio antes castigaba con el desprecio. El lector, por su parte, ha desarrollado una destreza notable para el consumo ritual del artículo: lo comparte antes de leerlo, lo aprueba antes de entenderlo, lo olvida antes de almorzar. Sería injusto, no obstante, atribuir la decadencia a la pereza de unos u otros. El mercado de la atención premia la certidumbre instantánea y penaliza la duda elaborada, y contra esa economía no hay talento que valga. Los que todavía dudan en público merecen, cuando menos, la cortesía de la suscripción».",
        "questions": [
            ("Según el autor, el columnista contemporáneo escribe para…", ["confirmar al converso", "convencer al escéptico", "informar al lector despistado"], "confirmar al converso"),
            ("¿Cuál es la actitud del autor hacia quienes «todavía dudan en público»?", ["De respeto", "De desprecio", "De indiferencia"], "De respeto"),
        ],
    },
    "C2 · Unidad 6: Memoria histórica": {
        "passage": "Crónica:\n«El acto comenzó, como tantos, con veinte minutos de retraso y una lista de nombres. En la plaza del pueblo, unos sesenta vecinos escuchaban la lectura de las víctimas de la represión mientras el viento obligaba a sujetar el micrófono. No hubo discursos largos: la nieta de uno de los fusilados leyó una carta que su abuelo escribió desde la cárcel, y el alcalde, visiblemente incómodo con el protocolo, prefirió ceder la palabra a la historiadora que documentó los casos. Cabría preguntarse qué efecto tiene esta liturgia laica sobre una comunidad que ya conoce los hechos. La respuesta, quizá, no esté en la información, sino en la repetición: nombrar cada año a los muertos no añade datos, pero sostiene una exigencia, la de que el pasado no se archive, que ningún libro, por riguroso que sea, puede mantener solo. Al terminar, alguien aplaudió; la mayoría, sencillamente, se quedó un rato más».",
        "questions": [
            ("¿Qué sugiere la cronista sobre el valor del acto anual?", ["Que la repetición sostiene una exigencia que los libros no pueden mantener solos", "Que aporta datos nuevos cada año", "Que es una costumbre vacía"], "Que la repetición sostiene una exigencia que los libros no pueden mantener solos"),
            ("El tono de la crónica es…", ["respetuoso y reflexivo", "burlón", "sensacionalista"], "respetuoso y reflexivo"),
        ],
    },
    "C2 · Unidad 7: Humor e ironía": {
        "passage": "Columna de humor:\n«Me he apuntado a un retiro de silencio. La decisión, confieso, la tomé tras leer que el silencio previene el estrés, la hipertensión y, según un estudio que no he leído pero cuyo titular me convenció, prácticamente todo lo demás. El retiro, situado en un valle de belleza ofensiva, prohíbe el teléfono, la conversación y, por lo visto, el sentido del humor: la monitora me miró con compasión clínica cuando pregunté si el silencio incluía los ronquidos. He pasado tres días contemplando mi respiración, actividad que, sorprendentemente, me ha dejado sin nada que contar. Lo cual, ahora que lo pienso, es exactamente lo que buscaba: volver con anécdotas habría sido fracasar. Regreso, pues, renovado y en paz, dispuesto a explicar a todo el que quiera escucharme, y a varios que no, las incomparables ventajas de callarse».",
        "questions": [
            ("El tono de la columna es…", ["irónico y autocrítico", "solemne", "didáctico"], "irónico y autocrítico"),
            ("Se deduce que la narradora vuelve del retiro…", ["tan locuaz como antes, pese a las lecciones del silencio", "decidida a no hablar nunca más", "decepcionada con la monitora"], "tan locuaz como antes, pese a las lecciones del silencio"),
        ],
    },
    "C2 · Unidad 8: Lenguaje administrativo": {
        "passage": "Artículo de opinión:\n«La Administración española ha perfeccionado un género literario propio: el texto que informa de todo salvo de lo que interesa. Cualquier ciudadano que haya solicitado una subvención conoce la experiencia: páginas de considerandos, referencias normativas remitidas a otras normas que remiten a las primeras, y un plazo final expresado en días hábiles contados desde una fecha que depende de un boletín. Sería tentador atribuir esta prosa a la maldad o a la incompetencia, cuando lo más probable es que responda a algo más prosaico: el miedo. Cada circunlocución es un escudo jurídico; cada subordinada, un parapeto ante el recurso contencioso. El resultado, sin embargo, es una ciudadanía que necesita gestores para relacionarse con su propio Estado, lo que constituye, pensándolo bien, la privatización más eficaz jamás diseñada: la del derecho a entender. Las administraciones que han apostado por el lenguaje claro demuestran que otra burocracia es posible; que sea rentable para alguien, ya es otro asunto».",
        "questions": [
            ("Según el autor, ¿qué explica la prosa administrativa?", ["El miedo jurídico de la Administración", "La maldad de los funcionarios", "La falta de formación literaria"], "El miedo jurídico de la Administración"),
            ("¿A qué llama el autor «la privatización más eficaz jamás diseñada»?", ["A la pérdida del derecho a entender, delegado en gestores", "A la venta de empresas públicas", "A las subvenciones privadas"], "A la pérdida del derecho a entender, delegado en gestores"),
        ],
    },
    "C2 · Unidad 9: Identidades": {
        "passage": "Ensayo breve:\n«Toda identidad, sostenía un antropólogo que ahora no viene al caso, es una biografía escrita por otros. La formulación resulta incómoda porque desmonta la fantasía de la autenticidad: nadie se inventa a sí mismo, y lo que llamamos identidad no es más que la negociación permanente entre lo que creemos ser y lo que los demás están dispuestos a reconocer. Las sociedades contemporáneas han intensificado esa negociación hasta convertirla en espectáculo: nunca fue tan fácil declarar una pertenencia ni tan arduo sostenerla sin etiqueta visible. Cabría preguntarse si la multiplicación de identidades disponibles ha ampliado la libertad individual o si, por el contrario, ha sofisticado la obligación de definirse. No hay respuesta cómoda. Quizá lo sensato sea aceptar que la identidad funciona menos como esencia que como cortesía: el nombre provisional que damos a una conversación que no termina nunca, y que empezó, además, mucho antes de que llegáramos nosotros».",
        "questions": [
            ("La intención del autor es…", ["reflexionar sobre la identidad como negociación social", "catalogar los tipos de identidad", "defender que nadie cambia nunca"], "reflexionar sobre la identidad como negociación social"),
            ("¿Qué metáfora usa el autor al final para definir la identidad?", ["Una cortesía: un nombre provisional", "Una esencia inmutable", "Un escaparate"], "Una cortesía: un nombre provisional"),
        ],
    },
    "C2 · Unidad 10: El siglo digital": {
        "passage": "Ensayo breve:\n«La promesa fundacional de internet, el acceso universal al conocimiento, se ha cumplido con una puntualidad que roza lo sarcástico: nunca dispusimos de tanta información ni de menos criterios para evaluarla. La desaparición de los intermediarios tradicionales, celebrada como emancipación, ha comportado la sustitución del editor por el algoritmo, es decir, de un filtro imperfecto pero legible por otro opaco e indiferente a la verdad. No se trata de añorar las redacciones de antaño, que también mintieron con métodos más artesanales, sino de reconocer que la verificación se ha convertido en una tarea individual en un entorno diseñado para impedirla. Frente a quienes anuncian la muerte de la credibilidad, convendría señalar que los bulos siempre circularon con eficacia admirable; lo que ha cambiado es su coste de producción, hoy cercano a cero. La alfabetización digital, esa asignatura pendiente, debería enseñar menos a desconfiar de todo, receta del cinismo, que a merecer confianza: un arte más lento y, por desgracia, menos viral».",
        "questions": [
            ("Se deduce que, para el autor, el problema actual no es la cantidad de bulos, sino…", ["su coste de producción cercano a cero", "la existencia de editores", "la falta de información"], "su coste de producción cercano a cero"),
            ("¿Qué debería enseñar la alfabetización digital, según el texto?", ["A merecer confianza, más que a desconfiar de todo", "A usar más redes sociales", "A programar algoritmos"], "A merecer confianza, más que a desconfiar de todo"),
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
