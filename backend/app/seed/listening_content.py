"""DELE-style audio scripts for the listening exercise of every unit.

Each script is a short announcement, message, or mini-dialogue at the unit's
CEFR level. The TTS speaks the script (not the answer), and the question checks
real comprehension of what was heard — like a DELE comprensión auditiva tarea.
"""

from typing import Any

# title -> spoken text that makes the lesson's listening question(s) answerable
LISTENING_SCRIPTS: dict[str, str] = {
    # --- A1 ---
    "En el café": "—Buenos días, un café con leche y una tostada, por favor. —Muy bien. Son cuatro euros con cincuenta. —Aquí tiene. —Gracias, ahora se lo traigo todo a la mesa.",
    "Primeras presentaciones": "Hola, me llamo Ana. Soy de México, pero ahora vivo en Valencia con mi familia. Trabajo en una escuela de idiomas y me gusta mucho esta ciudad.",
    "Mi familia y mi casa": "Nuestra casa no es grande, pero es muy cómoda. Tiene dos dormitorios, un salón luminoso y una cocina pequeña. Vivimos cuatro personas y un gato.",
    "Un día normal": "Todos los días me levanto a las siete, desayuno rápido y salgo de casa a las ocho menos cuarto. El autobús pasa a las ocho en punto, así que no puedo llegar tarde.",
    "En la consulta": "—Me duele la garganta desde ayer y tengo un poco de fiebre. —No es nada grave. Debe descansar y beber mucha agua. Y esta semana no haga ejercicio ni vaya a trabajar.",
    "Compras en el mercado": "—¿Cuánto cuestan los tomates? —Hoy están baratos: dos euros el kilo. —Pues un kilo, por favor. —¿Algo más? —No, gracias, eso es todo.",
    "Aprender juntos": "Esta persona aprende español porque quiere viajar por Sudamérica. Estudia vocabulario cada día con una aplicación y los lunes practica con un grupo online.",
    "A1 · Unidad 6: Esto me gusta": "—¿Qué película quieres ver esta noche? —No sé... no me gustan nada las películas de terror. —¿Y una comedia? —¡Sí, perfecto! Me encantan las comedias.",
    "A1 · Unidad 7: De aquí para allá": "—Perdone, ¿dónde está la estación? —Muy cerca: está al lado del mercado, a dos minutos andando. —¿Al lado del parque? —No, al lado del mercado.",
    "A1 · Unidad 8: ¿Qué hacemos?": "—¿Quedamos a las siete? —No puedo, trabajo hasta las siete y media. Mejor a las ocho. —Vale, a las ocho en la plaza. —Perfecto.",
    "A1 · Unidad 9: Tiempo y ropa": "—Qué frío hace hoy. ¿Qué abrigo me pongo, el negro o el azul? —El azul te queda muy bien. —Vale, pues el azul, y las botas marrones.",
    "A1 · Unidad 10: Ciudadanos del mundo": "—¿Has viajado alguna vez a Colombia? —Sí, dos veces. Allí aprendí a cocinar arepas. —¿Arepas? Qué interesante. Yo solo sé hacer paella.",
    # --- A2 ---
    "Charla con vecinos": "Lucía está muy contenta: este fin de semana irá a la playa con su familia y no tendrá que trabajar en casa. Además, los vecinos han decidido cenar en el restaurante nuevo el viernes por la noche. Todos están invitados.",
    "De viaje": "—Perdone, ¿cómo llego a la estación? —Siga todo recto y luego gire a la izquierda en el semáforo. —¿A la izquierda? —Sí, a la izquierda. La verá enseguida, junto a la farmacia.",
    "Buscar piso": "—El piso tiene dos dormitorios, ascensor y mucha luz. —¿Y cuánto cuesta? —Novecientos euros al mes, con los gastos incluidos. —De acuerdo, ¿puedo visitarlo mañana?",
    "Vitamina A2 · U1: Vamos a conocernos": "Leo estudia español desde hace un año. Escribe correos muy bien y lee novelas sin problema, pero le cuesta entender las conversaciones rápidas de sus compañeros de clase.",
    "Vitamina A2 · U2: Mi lugar en el mundo": "Si pudiera elegir, viviría en un pueblo tranquilo cerca del mar. El centro de una gran ciudad es demasiado ruidoso para mí, aunque tiene más servicios y más tiendas.",
    "Vitamina A2 · Repaso U1–U2": "Para mejorar la comprensión, Clara escucha diálogos cortos todos los días. Todavía no lee novelas largas, porque prefiere practicar el oído con audios breves.",
    "Una ruta de senderismo": "Atención, grupo: la ruta de mañana dura dos horas por el bosque. No hace falta maleta ni ordenador, pero deben llevar agua y calzado cómodo. Quedamos a primera hora.",
    "A2 · Unidad 10: Culturas": "Cuando llegué al barrio no conocía a nadie. Los vecinos me han ayudado mucho: me han explicado las costumbres, me han invitado a sus fiestas y ahora me siento en casa.",
    # --- B1 ---
    "Mensajes con intención": "Primer mensaje: «Hola, soy Marta de la imprenta. ¿Puedes enviarme la factura del mes pasado? La necesito para la contabilidad. Si puedes, adjúntala hoy. Muchas gracias.»",
    "B1 · Unidad 1: Volver a vernos": "—¡Cuánto tiempo! ¿Qué ha sido de ti? —Pues mira, he cambiado de trabajo: ahora trabajo desde casa. —¡Qué bien! ¿Y sigues hablando inglés? —Claro, el idioma no ha cambiado.",
    "B1 · Unidad 2: Recuerdos": "Cuando era pequeño, un día perdí las llaves mientras volvía a casa. Estaba lloviendo y no llevaba teléfono. Al final, una vecina llamó a mis padres y todo se arregló.",
    "B1 · Unidad 3: El mundo del futuro": "Según los expertos, dentro de veinte años las ciudades serán más verdes y usaremos menos coches privados. También habrá más parques públicos y la energía limpia será más barata.",
    "B1 · Unidad 4: Trabajo": "—¿Te interesa el puesto? —Mucho. El horario es flexible y solo hay reuniones presenciales dos días por semana. —¿Y el sueldo? —Normal, pero prefiero la flexibilidad.",
    "B1 · Unidad 5: Buen viaje": "Cuando llegamos al aeropuerto, el vuelo ya había salido. En el mostrador, la compañía nos ofreció un hotel para pasar la noche y otro vuelo a la mañana siguiente. No nos dieron ningún reembolso.",
    "B1 · Unidad 6: Vivienda": "En la reunión vecinal todos coinciden: hace falta mejorar el transporte nocturno. Los alquileres y la biblioteca pueden esperar, pero los autobuses de noche son prioritarios para el barrio.",
    "B1 · Unidad 7: Relaciones humanas": "—¿Qué te pasa? —Me molesta que algunas personas interrumpan siempre cuando hablo. —Entiendo. ¿Has hablado con ellas? —Sí, y prefiero que lo resolvamos con calma.",
    "B1 · Unidad 8: ¡Que aproveche!": "La salsa lleva especias que hacen que el sabor sea más intenso. Y recuerda: sírvela fría para conservar mejor el aroma. Nunca la sirvas caliente ni congelada.",
    "B1 · Unidad 9: Economía y consumo": "Según la encuesta, la mayoría de las familias intenta reducir sus gastos, pero uno de cada tres consumidores compra por impulso. Además, casi nadie repara todo lo que se estropea.",
    # --- B2 ---
    "B2 · Unidad 1: Señas de identidad": "Mi nombre tiene una historia: me lo pusieron por mi bisabuela paterna, una mujer muy querida en la familia. No tiene nada que ver con ninguna marca, aunque mi apellido coincide con una muy famosa.",
    "B2 · Unidad 2: Enigmas": "El misterio ocurrió en un faro de la costa. Una noche de tormenta, los tres vigilantes desaparecieron sin dejar rastro, y ni el barco cercano ni el museo del puerto aportaron pistas.",
    "B2 · Unidad 3: Al límite": "—¿Qué se siente al saltar en paracaídas? —Una mezcla de miedo y euforia. No es calma, desde luego, pero tampoco arrepentimiento. Si tuviera la oportunidad, repetiría mañana mismo.",
    "B2 · Unidad 4: Referentes": "Mi profesora de literatura fue quien me animó a escribir mis primeros relatos. Nunca me habló de viajar lejos ni de cambiar de carrera: simplemente me enseñó a escribir con valentía.",
    "B2 · Unidad 5: Evolución": "La novela me gustó mucho: el estilo es cuidado y la portada es preciosa. Lo único que me decepcionó un poco fue el final, demasiado lento para mi gusto.",
    "B2 · Unidad 6: El paso del tiempo": "Queríamos restaurar el reloj antiguo de la plaza, pero costaba demasiado dinero. No estaba perdido ni era nuevo: simplemente no había presupuesto suficiente.",
    "B2 · Unidad 7: Suerte": "Soy un poco supersticioso: cuando encuentre un trébol de cuatro hojas, lo guardaré para siempre. Las monedas antiguas y las herraduras, la verdad, no me dicen nada.",
    "B2 · Unidad 8: Con duende": "Cada verano, el pueblo celebra un rito antiguo junto a la hoguera. No es un mercado ni una carrera: es una tradición llena de encanto que atrae a cientos de visitantes.",
    "B2 · Unidad 9: Con sentido": "De todos los sentidos, el mío predominante es el oído: recuerdo todas las voces y las canciones de mi infancia. La vista y el olfato me ayudan mucho menos.",
    "B2 · Unidad 10: Historia": "El puente fue construido en el siglo XIX y todavía sigue en pie. No es del siglo XXI ni del año pasado, aunque lo restauraron hace muy poco.",
    "B2 · Unidad 11: La imagen": "Aquel hombretón, con sus dos metros y sus manos enormes, resultó ser la persona más dulce del barrio. Parecía serio y tímido, pero siempre estaba dispuesto a ayudar.",
    "B2 · Unidad 12: Más que palabras": "—El café está frío. —Normal: lo pediste hace media hora y no lo has tocado. —Es verdad. Pues pídeme otro, por favor, y esta vez me lo tomo enseguida.",
}


def enrich_listening(lessons: list[dict[str, Any]]) -> None:
    """Attach the DELE-style audio script to each lesson's listening exercises."""
    for lesson in lessons:
        script = LISTENING_SCRIPTS.get(lesson["title"])
        if not script:
            continue
        for exercise in lesson["exercises"]:
            if exercise["type"] == "listening" and exercise.get("audio"):
                exercise["audio_text"] = script
