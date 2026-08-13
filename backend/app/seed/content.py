"""Hand-made seed lessons for ¡Vamos!.

Three lessons with full transcripts, phrases (with pronunciation tips) and
exercises covering all five types. Structured as plain Python data so the
loader (load.py) can insert it idempotently.
"""

from typing import Any

LESSONS: list[dict[str, Any]] = [
    {
        "slug": "charla-con-vecinos",
        "title": "Charla con vecinos",
        "cefr_level": "A2",
        "topics": ["planes", "vida diaria"],
        "source": "local",
        "status": "published",
        "grammar_tip": {
            "wrong": "¿Qué planes tú tienes?",
            "right": "¿Qué planes tienes?",
            "explanation": "El pronombre no es necesario aquí.",
        },
        "segments": [
            {
                "start": 0.0,
                "end": 42.0,
                "transcript": [
                    {
                        "es": "¿Qué planes tienes para el fin de semana?",
                        "en": "What plans do you have for the weekend?",
                    },
                    {
                        "es": "Este sábado voy a visitar Madrid con mi hermana.",
                        "en": "This Saturday I'm going to visit Madrid with my sister.",
                    },
                    {
                        "es": "¡Qué bien! Yo voy a quedar con unos amigos el domingo.",
                        "en": "How nice! I'm going to meet up with some friends on Sunday.",
                    },
                ],
                "phrases": [
                    {
                        "text": "fin de semana",
                        "translation": "weekend",
                        "tip": "Suaviza la d entre vocales",
                    },
                    {
                        "text": "¿Qué planes tienes?",
                        "translation": "What plans do you have?",
                        "tip": None,
                    },
                    {
                        "text": "quedar con",
                        "translation": "to meet up with",
                        "tip": "La u de quedar casi no se oye: suena como 'kedar'",
                    },
                ],
            },
            {
                "start": 42.0,
                "end": 90.0,
                "transcript": [
                    {
                        "es": "¿Y tú, Lucía? ¿Qué vas a hacer?",
                        "en": "And you, Lucía? What are you going to do?",
                    },
                    {
                        "es": "Voy a ir a la playa, si hace buen tiempo.",
                        "en": "I'm going to go to the beach, if the weather is good.",
                    },
                    {
                        "es": "Yo tengo que trabajar en casa el sábado por la mañana.",
                        "en": "I have to work at home on Saturday morning.",
                    },
                ],
                "phrases": [
                    {
                        "text": "ir a la playa",
                        "translation": "to go to the beach",
                        "tip": "La y de playa suena fuerte, casi como una 'i' seguida",
                    },
                    {
                        "text": "hace buen tiempo",
                        "translation": "the weather is nice",
                        "tip": "La h nunca se pronuncia en español",
                    },
                    {
                        "text": "tener que trabajar",
                        "translation": "to have to work",
                        "tip": None,
                    },
                ],
            },
            {
                "start": 90.0,
                "end": 135.0,
                "transcript": [
                    {
                        "es": "¿Vas a salir el viernes por la noche?",
                        "en": "Are you going out on Friday night?",
                    },
                    {
                        "es": "No, el viernes prefiero descansar en casa.",
                        "en": "No, on Friday I prefer to rest at home.",
                    },
                    {
                        "es": "Nosotros vamos a cenar en el restaurante nuevo del barrio el viernes.",
                        "en": "We're going to have dinner at the new neighborhood restaurant on Friday.",
                    },
                ],
                "phrases": [
                    {
                        "text": "salir por la noche",
                        "translation": "to go out at night",
                        "tip": None,
                    },
                    {
                        "text": "descansar",
                        "translation": "to rest",
                        "tip": "La r final de descansar suena suave",
                    },
                    {
                        "text": "el restaurante nuevo",
                        "translation": "the new restaurant",
                        "tip": None,
                    },
                ],
            },
            {
                "start": 135.0,
                "end": 180.0,
                "transcript": [
                    {
                        "es": "¿Quedamos el lunes para tomar un café?",
                        "en": "Shall we meet on Monday for a coffee?",
                    },
                    {
                        "es": "¡Perfecto! Que tengas un buen fin de semana.",
                        "en": "Perfect! Have a good weekend.",
                    },
                    {
                        "es": "Igualmente, ¡hasta el lunes!",
                        "en": "Same to you, see you Monday!",
                    },
                ],
                "phrases": [
                    {
                        "text": "quedar",
                        "translation": "to meet up",
                        "tip": "Suaviza la d entre vocales",
                    },
                    {
                        "text": "tomar un café",
                        "translation": "to have a coffee",
                        "tip": None,
                    },
                    {
                        "text": "hasta el lunes",
                        "translation": "see you Monday",
                        "tip": "La h de hasta nunca se pronuncia",
                    },
                ],
            },
        ],
        "exercises": [
            {
                "type": "vocabulary",
                "instructions": "Relaciona las palabras.",
                "prompt": "quedar",
                "options": ["reunirse", "trabajar", "dormir"],
                "expected_answer": "reunirse",
                "skill_weights": {"vocabulary": 1.0},
            },
            {
                "type": "vocabulary",
                "instructions": "Relaciona las palabras.",
                "prompt": "descansar",
                "options": ["to rest", "to work", "to travel"],
                "expected_answer": "to rest",
                "skill_weights": {"vocabulary": 1.0},
            },
            {
                "type": "grammar",
                "instructions": "Completa la frase.",
                "prompt": "Este sábado ___ a visitar Madrid",
                "options": None,
                "expected_answer": "voy",
                "skill_weights": {"grammar": 1.0},
            },
            {
                "type": "grammar",
                "instructions": "Corrige la frase.",
                "prompt": "¿Qué planes tú tienes?",
                "options": None,
                "expected_answer": "¿Qué planes tienes?",
                "skill_weights": {"grammar": 1.0, "writing": 0.5},
            },
            {
                "type": "grammar",
                "instructions": "Completa la frase con la forma correcta de ir.",
                "prompt": "El domingo ellos ___ a cenar fuera.",
                "options": None,
                "expected_answer": "van",
                "skill_weights": {"grammar": 1.0},
            },
            {
                "type": "writing",
                "instructions": "Escribe 4 frases sobre tus planes.",
                "prompt": "Escribe 4 frases sobre tus planes. Empieza: Este fin de semana voy a...",
                "options": None,
                "expected_answer": (
                    "Este fin de semana voy a visitar a mi familia. "
                    "El sábado voy a quedar con mis amigos. "
                    "El domingo voy a descansar en casa. "
                    "También voy a estudiar español."
                ),
                "skill_weights": {"writing": 1.0, "grammar": 0.5},
            },
            {
                "type": "listening",
                "instructions": "Escucha y elige la respuesta correcta.",
                "prompt": "¿Qué hará Lucía este fin de semana?",
                "options": ["Visitará a sus vecinos", "Irá a la playa", "Trabajará en casa"],
                "expected_answer": "Irá a la playa",
                "audio": True,
                "skill_weights": {"listening": 1.0},
            },
            {
                "type": "listening",
                "instructions": "Escucha y elige la respuesta correcta.",
                "prompt": "¿Cuándo van a cenar en el restaurante nuevo?",
                "options": ["El viernes", "El sábado", "El domingo"],
                "expected_answer": "El viernes",
                "audio": True,
                "skill_weights": {"listening": 1.0},
            },
            {
                "type": "pronunciation",
                "instructions": "Escucha y repite la frase.",
                "prompt": "Repite la frase: fin de semana",
                "options": None,
                "expected_answer": "fin de semana",
                "audio": True,
                "skill_weights": {"pronunciation": 1.0, "fluency": 0.5},
            },
            {
                "type": "pronunciation",
                "instructions": "Escucha y repite la frase.",
                "prompt": "Repite la frase: ¿Qué planes tienes?",
                "options": None,
                "expected_answer": "¿Qué planes tienes?",
                "audio": True,
                "skill_weights": {"pronunciation": 1.0, "listening": 0.3},
            },
        ],
    },
    {
        "slug": "en-el-cafe",
        "title": "En el café",
        "cefr_level": "A1",
        "topics": ["comida", "restaurantes"],
        "source": "local",
        "status": "published",
        "grammar_tip": {
            "wrong": "¿Donde esta el baño?",
            "right": "¿Dónde está el baño?",
            "explanation": "Las palabras interrogativas llevan tilde, y 'está' también.",
        },
        "segments": [
            {
                "start": 0.0,
                "end": 35.0,
                "transcript": [
                    {
                        "es": "Buenos días. ¿Qué desea tomar?",
                        "en": "Good morning. What would you like to have?",
                    },
                    {
                        "es": "Un café con leche y un cruasán, por favor.",
                        "en": "A coffee with milk and a croissant, please.",
                    },
                    {
                        "es": "¿Para tomar aquí o para llevar?",
                        "en": "To have here or to go?",
                    },
                ],
                "phrases": [
                    {
                        "text": "un café con leche",
                        "translation": "a coffee with milk",
                        "tip": None,
                    },
                    {
                        "text": "por favor",
                        "translation": "please",
                        "tip": "La r final suena suave, sin vibrar",
                    },
                    {
                        "text": "para llevar",
                        "translation": "to go (takeaway)",
                        "tip": "Las dos eles de llevar suenan como una 'y'",
                    },
                ],
            },
            {
                "start": 35.0,
                "end": 70.0,
                "transcript": [
                    {
                        "es": "¿Algo más? Tenemos zumo de naranja natural.",
                        "en": "Anything else? We have fresh orange juice.",
                    },
                    {
                        "es": "Sí, un zumo y una tostada con tomate.",
                        "en": "Yes, a juice and a toast with tomato.",
                    },
                    {
                        "es": "Muy bien. Son cuatro euros con cincuenta.",
                        "en": "Very good. That's four euros fifty.",
                    },
                ],
                "phrases": [
                    {
                        "text": "zumo de naranja",
                        "translation": "orange juice",
                        "tip": "En España la z suena como la 'th' inglesa",
                    },
                    {
                        "text": "una tostada",
                        "translation": "a toast",
                        "tip": "Suaviza la d entre vocales",
                    },
                    {
                        "text": "¿algo más?",
                        "translation": "anything else?",
                        "tip": None,
                    },
                ],
            },
            {
                "start": 70.0,
                "end": 105.0,
                "transcript": [
                    {
                        "es": "Aquí tiene. ¡Que aproveche!",
                        "en": "Here you are. Enjoy your meal!",
                    },
                    {
                        "es": "Muchas gracias. ¿Dónde está el baño?",
                        "en": "Thank you very much. Where is the bathroom?",
                    },
                    {
                        "es": "Al fondo, a la derecha.",
                        "en": "At the back, on the right.",
                    },
                ],
                "phrases": [
                    {
                        "text": "que aproveche",
                        "translation": "enjoy your meal",
                        "tip": "La ch suena como en 'chocolate'",
                    },
                    {
                        "text": "muchas gracias",
                        "translation": "thank you very much",
                        "tip": None,
                    },
                    {
                        "text": "a la derecha",
                        "translation": "on the right",
                        "tip": None,
                    },
                ],
            },
        ],
        "exercises": [
            {
                "type": "vocabulary",
                "instructions": "Relaciona las palabras.",
                "prompt": "para llevar",
                "options": ["to go (takeaway)", "to eat here", "to pay"],
                "expected_answer": "to go (takeaway)",
                "skill_weights": {"vocabulary": 1.0},
            },
            {
                "type": "vocabulary",
                "instructions": "Relaciona las palabras.",
                "prompt": "la cuenta",
                "options": ["the bill", "the table", "the menu"],
                "expected_answer": "the bill",
                "skill_weights": {"vocabulary": 1.0},
            },
            {
                "type": "grammar",
                "instructions": "Completa la frase con la forma correcta de querer.",
                "prompt": "Yo ___ un café con leche, por favor.",
                "options": None,
                "expected_answer": "quiero",
                "skill_weights": {"grammar": 1.0},
            },
            {
                "type": "grammar",
                "instructions": "Completa la pregunta.",
                "prompt": "¿___ está el baño?",
                "options": ["Dónde", "Cuándo", "Quién"],
                "expected_answer": "Dónde",
                "skill_weights": {"grammar": 1.0},
            },
            {
                "type": "writing",
                "instructions": "Escribe 2 frases para pedir en un café.",
                "prompt": "Escribe 2 frases para pedir en un café.",
                "options": None,
                "expected_answer": "Quiero un café con leche, por favor. ¿Cuánto es?",
                "skill_weights": {"writing": 1.0, "grammar": 0.5},
            },
            {
                "type": "listening",
                "instructions": "Escucha y elige la respuesta correcta.",
                "prompt": "¿Cuánto cuesta todo?",
                "options": [
                    "Cuatro euros con cincuenta",
                    "Cinco euros",
                    "Tres euros con veinte",
                ],
                "expected_answer": "Cuatro euros con cincuenta",
                "audio": True,
                "skill_weights": {"listening": 1.0},
            },
            {
                "type": "pronunciation",
                "instructions": "Escucha y repite la frase.",
                "prompt": "Repite la frase: un café con leche, por favor",
                "options": None,
                "expected_answer": "un café con leche, por favor",
                "audio": True,
                "skill_weights": {"pronunciation": 1.0, "fluency": 0.5},
            },
        ],
    },
    {
        "slug": "de-viaje",
        "title": "De viaje",
        "cefr_level": "A2",
        "topics": ["viajes", "direcciones"],
        "source": "local",
        "status": "published",
        "grammar_tip": {
            "wrong": "Siga recto y gira a la izquierda",
            "right": "Siga recto y gire a la izquierda",
            "explanation": "Con el imperativo formal (usted) usamos 'gire', no 'gira'.",
        },
        "segments": [
            {
                "start": 0.0,
                "end": 40.0,
                "transcript": [
                    {
                        "es": "Perdone, ¿cómo llego a la estación de tren?",
                        "en": "Excuse me, how do I get to the train station?",
                    },
                    {
                        "es": "Siga todo recto y gire a la izquierda en el semáforo.",
                        "en": "Go straight ahead and turn left at the traffic light.",
                    },
                    {
                        "es": "¿Está lejos de aquí?",
                        "en": "Is it far from here?",
                    },
                ],
                "phrases": [
                    {
                        "text": "todo recto",
                        "translation": "straight ahead",
                        "tip": None,
                    },
                    {
                        "text": "¿cómo llego a...?",
                        "translation": "how do I get to...?",
                        "tip": None,
                    },
                    {
                        "text": "a la izquierda",
                        "translation": "on the left",
                        "tip": "En España la z suena como la 'th' inglesa",
                    },
                ],
            },
            {
                "start": 40.0,
                "end": 80.0,
                "transcript": [
                    {
                        "es": "No, está a cinco minutos a pie.",
                        "en": "No, it's five minutes on foot.",
                    },
                    {
                        "es": "¿Puedo comprar el billete en la estación?",
                        "en": "Can I buy the ticket at the station?",
                    },
                    {
                        "es": "Sí, pero es más barato por internet.",
                        "en": "Yes, but it's cheaper online.",
                    },
                ],
                "phrases": [
                    {
                        "text": "a pie",
                        "translation": "on foot",
                        "tip": None,
                    },
                    {
                        "text": "el billete",
                        "translation": "the ticket",
                        "tip": "Las dos eles suenan como una 'y'",
                    },
                    {
                        "text": "más barato",
                        "translation": "cheaper",
                        "tip": None,
                    },
                ],
            },
            {
                "start": 80.0,
                "end": 120.0,
                "transcript": [
                    {
                        "es": "Mi tren sale a las nueve y media.",
                        "en": "My train leaves at nine thirty.",
                    },
                    {
                        "es": "Entonces tiene tiempo para desayunar.",
                        "en": "Then you have time to have breakfast.",
                    },
                    {
                        "es": "¡Muchas gracias por su ayuda!",
                        "en": "Thank you very much for your help!",
                    },
                ],
                "phrases": [
                    {
                        "text": "sale a las nueve y media",
                        "translation": "leaves at nine thirty",
                        "tip": None,
                    },
                    {
                        "text": "desayunar",
                        "translation": "to have breakfast",
                        "tip": "La y suena fuerte, casi como una 'i' seguida",
                    },
                    {
                        "text": "gracias por su ayuda",
                        "translation": "thank you for your help",
                        "tip": "La y de ayuda suena fuerte",
                    },
                ],
            },
        ],
        "exercises": [
            {
                "type": "vocabulary",
                "instructions": "Relaciona las palabras.",
                "prompt": "girar a la izquierda",
                "options": ["to turn left", "to go straight", "to turn right"],
                "expected_answer": "to turn left",
                "skill_weights": {"vocabulary": 1.0},
            },
            {
                "type": "vocabulary",
                "instructions": "Relaciona las palabras.",
                "prompt": "el billete",
                "options": ["the ticket", "the train", "the platform"],
                "expected_answer": "the ticket",
                "skill_weights": {"vocabulary": 1.0},
            },
            {
                "type": "grammar",
                "instructions": "Completa la frase con la forma correcta de salir.",
                "prompt": "Mi tren ___ a las nueve y media.",
                "options": None,
                "expected_answer": "sale",
                "skill_weights": {"grammar": 1.0},
            },
            {
                "type": "grammar",
                "instructions": "Completa la frase con la forma correcta de llegar.",
                "prompt": "Perdone, ¿cómo ___ al museo?",
                "options": None,
                "expected_answer": "llego",
                "skill_weights": {"grammar": 1.0},
            },
            {
                "type": "writing",
                "instructions": "Escribe 3 frases para pedir direcciones.",
                "prompt": "Escribe 3 frases para pedir direcciones.",
                "options": None,
                "expected_answer": (
                    "Perdone, ¿cómo llego a la estación? "
                    "¿Está lejos de aquí? "
                    "Muchas gracias por su ayuda."
                ),
                "skill_weights": {"writing": 1.0, "grammar": 0.5},
            },
            {
                "type": "listening",
                "instructions": "Escucha y elige la respuesta correcta.",
                "prompt": "¿Dónde debe girar el viajero?",
                "options": ["A la izquierda", "A la derecha", "Todo recto"],
                "expected_answer": "A la izquierda",
                "audio": True,
                "skill_weights": {"listening": 1.0},
            },
            {
                "type": "pronunciation",
                "instructions": "Escucha y repite la frase.",
                "prompt": "Repite la frase: siga todo recto",
                "options": None,
                "expected_answer": "siga todo recto",
                "audio": True,
                "skill_weights": {"pronunciation": 1.0, "fluency": 0.5},
            },
        ],
    },
]
