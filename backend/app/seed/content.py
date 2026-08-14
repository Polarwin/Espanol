"""Hand-made seed lessons for ¡Vamos!.

Twelve lessons with full transcripts, phrases (with pronunciation tips) and
exercises covering all five types. Structured as plain Python data so the
loader (load.py) can insert it idempotently.
"""

from typing import Any
from .curriculum_content import CURRICULUM_LESSONS
from .video_content import VIDEO_LESSONS
from .vocabulary_content import enrich_lessons

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
    {
        "slug": "primeras-presentaciones",
        "title": "Primeras presentaciones",
        "cefr_level": "A1",
        "topics": ["presentaciones", "datos personales", "vida diaria"],
        "source": "original",
        "status": "published",
        "grammar_tip": {
            "wrong": "Yo es Ana.",
            "right": "Yo soy Ana.",
            "explanation": "Usamos soy para hablar de nuestra identidad.",
        },
        "segments": [
            {
                "start": 0.0, "end": 35.0,
                "transcript": [
                    {"es": "Hola, me llamo Ana. ¿Cómo te llamas?", "en": "Hello, my name is Ana. What is your name?"},
                    {"es": "Me llamo Daniel. Encantado.", "en": "My name is Daniel. Nice to meet you."},
                    {"es": "Encantada. ¿De dónde eres?", "en": "Nice to meet you. Where are you from?"},
                ],
                "phrases": [
                    {"text": "me llamo", "translation": "my name is", "tip": "La ll suele sonar como una y"},
                    {"text": "¿Cómo te llamas?", "translation": "What is your name?", "tip": "Marca la primera sílaba de cómo"},
                    {"text": "encantado", "translation": "nice to meet you", "tip": "Suaviza la d entre vocales"},
                ],
            },
            {
                "start": 35.0, "end": 75.0,
                "transcript": [
                    {"es": "Soy de México, pero vivo en Valencia.", "en": "I am from Mexico, but I live in Valencia."},
                    {"es": "Yo soy de Irlanda. Estudio español aquí.", "en": "I am from Ireland. I study Spanish here."},
                    {"es": "¡Qué bien! Hasta mañana, Daniel.", "en": "Great! See you tomorrow, Daniel."},
                ],
                "phrases": [
                    {"text": "soy de", "translation": "I am from", "tip": "Une soy y de con ritmo natural"},
                    {"text": "vivo en", "translation": "I live in", "tip": "La v española suele sonar cercana a b"},
                    {"text": "hasta mañana", "translation": "see you tomorrow", "tip": "La h no se pronuncia"},
                ],
            },
        ],
        "exercises": [
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "me llamo", "options": ["my name is", "I live in", "I study"], "expected_answer": "my name is", "skill_weights": {"vocabulary": 1.0}},
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "hasta mañana", "options": ["see you tomorrow", "good morning", "good night"], "expected_answer": "see you tomorrow", "skill_weights": {"vocabulary": 1.0}},
            {"type": "grammar", "instructions": "Completa con ser.", "prompt": "Yo ___ de México.", "options": None, "expected_answer": "soy", "skill_weights": {"grammar": 1.0}},
            {"type": "grammar", "instructions": "Completa con vivir.", "prompt": "Yo ___ en Valencia.", "options": None, "expected_answer": "vivo", "skill_weights": {"grammar": 1.0}},
            {"type": "writing", "instructions": "Preséntate en tres frases.", "prompt": "Escribe tu nombre, tu país y dónde vives.", "options": None, "expected_answer": "Me llamo Alex. Soy de Canadá. Vivo en Valencia.", "skill_weights": {"writing": 1.0, "grammar": 0.5}},
            {"type": "listening", "instructions": "Escucha y elige.", "prompt": "¿Dónde vive Ana?", "options": ["En Valencia", "En México", "En Irlanda"], "expected_answer": "En Valencia", "audio": True, "skill_weights": {"listening": 1.0}},
            {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": "Repite: Hola, me llamo Ana", "options": None, "expected_answer": "Hola, me llamo Ana", "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
        ],
    },
    {
        "slug": "compras-en-el-mercado",
        "title": "Compras en el mercado",
        "cefr_level": "A2",
        "topics": ["comida", "compras", "cantidades"],
        "source": "original",
        "status": "published",
        "grammar_tip": {
            "wrong": "Quiero dos kilo de tomates.",
            "right": "Quiero dos kilos de tomates.",
            "explanation": "Las cantidades mayores de uno llevan el sustantivo en plural.",
        },
        "segments": [
            {
                "start": 0.0, "end": 40.0,
                "transcript": [
                    {"es": "Buenos días. ¿Cuánto cuestan los tomates?", "en": "Good morning. How much are the tomatoes?"},
                    {"es": "Cuestan dos euros el kilo.", "en": "They cost two euros per kilo."},
                    {"es": "Póngame un kilo, por favor.", "en": "Give me one kilo, please."},
                ],
                "phrases": [
                    {"text": "¿Cuánto cuesta?", "translation": "How much does it cost?", "tip": "La c de cuesta suena como k"},
                    {"text": "un kilo", "translation": "one kilogram", "tip": None},
                    {"text": "póngame", "translation": "give me", "tip": "Marca la sílaba pón"},
                ],
            },
            {
                "start": 40.0, "end": 85.0,
                "transcript": [
                    {"es": "También necesito medio kilo de naranjas.", "en": "I also need half a kilo of oranges."},
                    {"es": "Muy bien. Son cuatro euros con cincuenta en total.", "en": "All right. It is four euros fifty in total."},
                    {"es": "Aquí tiene. Muchas gracias.", "en": "Here you are. Thank you very much."},
                ],
                "phrases": [
                    {"text": "medio kilo", "translation": "half a kilogram", "tip": "Suaviza la d de medio"},
                    {"text": "en total", "translation": "in total", "tip": None},
                    {"text": "aquí tiene", "translation": "here you are", "tip": "Aquí lleva el acento al final"},
                ],
            },
        ],
        "exercises": [
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "medio kilo", "options": ["half a kilo", "two kilos", "one quarter"], "expected_answer": "half a kilo", "skill_weights": {"vocabulary": 1.0}},
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "en total", "options": ["in total", "on sale", "in cash"], "expected_answer": "in total", "skill_weights": {"vocabulary": 1.0}},
            {"type": "grammar", "instructions": "Completa con costar.", "prompt": "Los tomates ___ dos euros el kilo.", "options": None, "expected_answer": "cuestan", "skill_weights": {"grammar": 1.0}},
            {"type": "grammar", "instructions": "Completa la cantidad.", "prompt": "Quiero dos ___ de tomates.", "options": None, "expected_answer": "kilos", "skill_weights": {"grammar": 1.0}},
            {"type": "writing", "instructions": "Escribe un pedido breve.", "prompt": "Pide tres productos y pregunta el precio.", "options": None, "expected_answer": "Quiero un kilo de tomates y medio kilo de naranjas. También necesito pan. ¿Cuánto cuesta todo?", "skill_weights": {"writing": 1.0, "grammar": 0.5}},
            {"type": "listening", "instructions": "Escucha y elige.", "prompt": "¿Cuánto cuestan los tomates?", "options": ["Dos euros el kilo", "Cuatro euros el kilo", "Un euro el kilo"], "expected_answer": "Dos euros el kilo", "audio": True, "skill_weights": {"listening": 1.0}},
            {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": "Repite: Póngame un kilo, por favor", "options": None, "expected_answer": "Póngame un kilo, por favor", "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
        ],
    },
    {
        "slug": "mi-familia-y-mi-casa",
        "title": "Mi familia y mi casa",
        "cefr_level": "A1",
        "topics": ["familia", "casa", "descripciones"],
        "source": "original",
        "status": "published",
        "grammar_tip": {
            "wrong": "Mi hermano tienen veinte años.",
            "right": "Mi hermano tiene veinte años.",
            "explanation": "Con él o ella usamos tiene; tienen corresponde a ellos o ellas.",
        },
        "segments": [
            {
                "start": 0.0, "end": 38.0,
                "transcript": [
                    {"es": "Esta es una foto de mi familia.", "en": "This is a photo of my family."},
                    {"es": "Mi madre se llama Carmen y mi padre se llama Luis.", "en": "My mother's name is Carmen and my father's name is Luis."},
                    {"es": "También tengo un hermano. Tiene veinte años.", "en": "I also have a brother. He is twenty years old."},
                ],
                "phrases": [
                    {"text": "mi familia", "translation": "my family", "tip": "La primera i es breve y clara"},
                    {"text": "se llama", "translation": "is called", "tip": "La ll suele sonar como una y"},
                    {"text": "tiene veinte años", "translation": "is twenty years old", "tip": "Une tiene y veinte con ritmo regular"},
                ],
            },
            {
                "start": 38.0, "end": 78.0,
                "transcript": [
                    {"es": "Vivimos en una casa pequeña con dos dormitorios.", "en": "We live in a small house with two bedrooms."},
                    {"es": "La cocina está al lado del salón.", "en": "The kitchen is next to the living room."},
                    {"es": "Mi habitación tiene una ventana grande.", "en": "My bedroom has a large window."},
                ],
                "phrases": [
                    {"text": "una casa pequeña", "translation": "a small house", "tip": "La ñ se pronuncia como ny"},
                    {"text": "al lado de", "translation": "next to", "tip": "La d entre vocales es suave"},
                    {"text": "una ventana grande", "translation": "a large window", "tip": "La g de grande suena fuerte"},
                ],
            },
        ],
        "exercises": [
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "el hermano", "options": ["brother", "father", "uncle"], "expected_answer": "brother", "skill_weights": {"vocabulary": 1.0}},
            {"type": "vocabulary", "instructions": "Elige el lugar.", "prompt": "¿Dónde cocinamos?", "options": ["En la cocina", "En el dormitorio", "En el salón"], "expected_answer": "En la cocina", "skill_weights": {"vocabulary": 1.0}},
            {"type": "grammar", "instructions": "Completa con tener.", "prompt": "Mi hermana ___ dieciocho años.", "options": None, "expected_answer": "tiene", "skill_weights": {"grammar": 1.0}},
            {"type": "grammar", "instructions": "Completa el adjetivo.", "prompt": "Es una casa ___.", "options": ["pequeña", "pequeño", "pequeños"], "expected_answer": "pequeña", "skill_weights": {"grammar": 1.0}},
            {"type": "writing", "instructions": "Describe tu casa.", "prompt": "Escribe tres frases sobre las habitaciones de tu casa.", "options": None, "expected_answer": "Vivo en una casa pequeña. Tiene dos dormitorios. La cocina está al lado del salón.", "skill_weights": {"writing": 1.0, "grammar": 0.5}},
            {"type": "listening", "instructions": "Escucha y elige.", "prompt": "¿Cuántos dormitorios tiene la casa?", "options": ["Dos", "Uno", "Tres"], "expected_answer": "Dos", "audio": True, "skill_weights": {"listening": 1.0}},
            {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": "Repite: Mi familia vive en una casa pequeña", "options": None, "expected_answer": "Mi familia vive en una casa pequeña", "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
        ],
    },
    {
        "slug": "un-dia-normal",
        "title": "Un día normal",
        "cefr_level": "A1",
        "topics": ["rutina", "horarios", "vida diaria"],
        "source": "original",
        "status": "published",
        "grammar_tip": {
            "wrong": "Me levanto a las siete y desayuno después.",
            "right": "Me levanto a las siete y después desayuno.",
            "explanation": "Después puede ir antes del verbo para ordenar claramente las acciones.",
        },
        "segments": [
            {
                "start": 0.0, "end": 40.0,
                "transcript": [
                    {"es": "Me levanto a las siete y me ducho.", "en": "I get up at seven and take a shower."},
                    {"es": "Después desayuno café con leche y tostadas.", "en": "Then I have coffee with milk and toast for breakfast."},
                    {"es": "Salgo de casa a las ocho menos cuarto.", "en": "I leave home at quarter to eight."},
                ],
                "phrases": [
                    {"text": "me levanto", "translation": "I get up", "tip": "La v suena cercana a una b suave"},
                    {"text": "después desayuno", "translation": "then I have breakfast", "tip": "Distingue las dos sílabas iniciales des"},
                    {"text": "a las ocho menos cuarto", "translation": "at quarter to eight", "tip": "La h de ocho no se pronuncia"},
                ],
            },
            {
                "start": 40.0, "end": 82.0,
                "transcript": [
                    {"es": "Trabajo de nueve a cinco en una oficina.", "en": "I work from nine to five in an office."},
                    {"es": "Por la tarde hago ejercicio en el parque.", "en": "In the afternoon I exercise in the park."},
                    {"es": "Ceno a las nueve y me acuesto a las once.", "en": "I have dinner at nine and go to bed at eleven."},
                ],
                "phrases": [
                    {"text": "de nueve a cinco", "translation": "from nine to five", "tip": "Une de y nueve suavemente"},
                    {"text": "por la tarde", "translation": "in the afternoon", "tip": "La r de tarde es breve"},
                    {"text": "me acuesto", "translation": "I go to bed", "tip": "Cuesto empieza con sonido k"},
                ],
            },
        ],
        "exercises": [
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "me levanto", "options": ["I get up", "I go to bed", "I eat"], "expected_answer": "I get up", "skill_weights": {"vocabulary": 1.0}},
            {"type": "vocabulary", "instructions": "Ordena la rutina.", "prompt": "¿Qué haces normalmente por la mañana?", "options": ["Desayuno", "Ceno", "Me acuesto"], "expected_answer": "Desayuno", "skill_weights": {"vocabulary": 1.0}},
            {"type": "grammar", "instructions": "Completa el verbo reflexivo.", "prompt": "Yo ___ levanto a las siete.", "options": None, "expected_answer": "me", "skill_weights": {"grammar": 1.0}},
            {"type": "grammar", "instructions": "Completa la hora.", "prompt": "Salgo de casa ___ las ocho.", "options": ["a", "en", "de"], "expected_answer": "a", "skill_weights": {"grammar": 1.0}},
            {"type": "writing", "instructions": "Cuenta tu rutina.", "prompt": "Escribe cuatro acciones de un día normal.", "options": None, "expected_answer": "Me levanto a las siete. Desayuno. Trabajo por la mañana. Me acuesto a las once.", "skill_weights": {"writing": 1.0, "grammar": 0.5}},
            {"type": "listening", "instructions": "Escucha y elige.", "prompt": "¿A qué hora sale de casa?", "options": ["A las ocho menos cuarto", "A las siete", "A las nueve"], "expected_answer": "A las ocho menos cuarto", "audio": True, "skill_weights": {"listening": 1.0}},
            {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": "Repite: Después desayuno café con leche", "options": None, "expected_answer": "Después desayuno café con leche", "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
        ],
    },
    {
        "slug": "en-la-consulta",
        "title": "En la consulta",
        "cefr_level": "A2",
        "topics": ["salud", "cuerpo", "consejos"],
        "source": "original",
        "status": "published",
        "grammar_tip": {
            "wrong": "Debes de descansar dos días.",
            "right": "Debes descansar dos días.",
            "explanation": "Para dar un consejo usamos deber más infinitivo, sin la preposición de.",
        },
        "segments": [
            {
                "start": 0.0, "end": 42.0,
                "transcript": [
                    {"es": "Buenos días. ¿Qué le pasa?", "en": "Good morning. What is wrong?"},
                    {"es": "Me duele la garganta y tengo un poco de fiebre.", "en": "My throat hurts and I have a slight fever."},
                    {"es": "¿Desde cuándo se encuentra así?", "en": "How long have you felt this way?"},
                ],
                "phrases": [
                    {"text": "¿Qué le pasa?", "translation": "What is wrong?", "tip": "La u de qué no se pronuncia"},
                    {"text": "me duele la garganta", "translation": "my throat hurts", "tip": "La g de garganta es fuerte"},
                    {"text": "tengo fiebre", "translation": "I have a fever", "tip": "Fiebre tiene dos sílabas"},
                ],
            },
            {
                "start": 42.0, "end": 86.0,
                "transcript": [
                    {"es": "Desde ayer por la noche. También estoy muy cansada.", "en": "Since last night. I am also very tired."},
                    {"es": "Parece un resfriado. Debe descansar y beber mucha agua.", "en": "It seems like a cold. You should rest and drink plenty of water."},
                    {"es": "Tome este medicamento después de comer.", "en": "Take this medicine after eating."},
                ],
                "phrases": [
                    {"text": "desde ayer", "translation": "since yesterday", "tip": "La d final de desde enlaza con ayer"},
                    {"text": "debe descansar", "translation": "you should rest", "tip": "La b intervocálica es suave"},
                    {"text": "después de comer", "translation": "after eating", "tip": "Marca el acento de después"},
                ],
            },
        ],
        "exercises": [
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "la garganta", "options": ["throat", "head", "back"], "expected_answer": "throat", "skill_weights": {"vocabulary": 1.0}},
            {"type": "vocabulary", "instructions": "Elige el síntoma.", "prompt": "Tengo 38 grados.", "options": ["Tengo fiebre", "Tengo hambre", "Tengo sueño"], "expected_answer": "Tengo fiebre", "skill_weights": {"vocabulary": 1.0}},
            {"type": "grammar", "instructions": "Completa con doler.", "prompt": "Me ___ la cabeza.", "options": None, "expected_answer": "duele", "skill_weights": {"grammar": 1.0}},
            {"type": "grammar", "instructions": "Completa el consejo.", "prompt": "___ descansar y beber agua.", "options": ["Debe", "Tiene", "Hace"], "expected_answer": "Debe", "skill_weights": {"grammar": 1.0}},
            {"type": "writing", "instructions": "Explica cómo estás.", "prompt": "Describe dos síntomas y pregunta qué debes hacer.", "options": None, "expected_answer": "Me duele la garganta y tengo fiebre. ¿Qué debo hacer?", "skill_weights": {"writing": 1.0, "grammar": 0.5}},
            {"type": "listening", "instructions": "Escucha y elige.", "prompt": "¿Qué recomienda la médica?", "options": ["Descansar y beber agua", "Hacer ejercicio", "Ir a trabajar"], "expected_answer": "Descansar y beber agua", "audio": True, "skill_weights": {"listening": 1.0}},
            {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": "Repite: Me duele la garganta y tengo fiebre", "options": None, "expected_answer": "Me duele la garganta y tengo fiebre", "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
        ],
    },
    {
        "slug": "buscar-piso",
        "title": "Buscar piso",
        "cefr_level": "A2",
        "topics": ["vivienda", "alquiler", "descripciones"],
        "source": "original",
        "status": "published",
        "grammar_tip": {
            "wrong": "El piso que vi ayer, tiene balcón.",
            "right": "El piso que vi ayer tiene balcón.",
            "explanation": "No separamos con coma el sujeto y su verbo.",
        },
        "segments": [
            {
                "start": 0.0, "end": 43.0,
                "transcript": [
                    {"es": "Llamo por el anuncio del piso en alquiler.", "en": "I am calling about the apartment rental listing."},
                    {"es": "Tiene dos habitaciones, un balcón y mucha luz.", "en": "It has two bedrooms, a balcony, and plenty of light."},
                    {"es": "¿Está amueblado y cuánto cuesta al mes?", "en": "Is it furnished and how much does it cost per month?"},
                ],
                "phrases": [
                    {"text": "piso en alquiler", "translation": "apartment for rent", "tip": "Alquiler termina con una r suave"},
                    {"text": "está amueblado", "translation": "it is furnished", "tip": "Une está y amueblado"},
                    {"text": "cuánto cuesta al mes", "translation": "how much it costs per month", "tip": "Cu suena como k"},
                ],
            },
            {
                "start": 43.0, "end": 88.0,
                "transcript": [
                    {"es": "Cuesta novecientos euros, gastos incluidos.", "en": "It costs nine hundred euros, utilities included."},
                    {"es": "Está cerca del metro, pero la calle es tranquila.", "en": "It is near the metro, but the street is quiet."},
                    {"es": "Me interesa. ¿Podría visitarlo mañana por la tarde?", "en": "I am interested. Could I visit it tomorrow afternoon?"},
                ],
                "phrases": [
                    {"text": "gastos incluidos", "translation": "utilities included", "tip": "La s final enlaza con incluidos"},
                    {"text": "cerca del metro", "translation": "near the metro", "tip": "En España, la c de cerca suele sonar como z"},
                    {"text": "¿Podría visitarlo?", "translation": "Could I visit it?", "tip": "Podría lleva el acento en la i"},
                ],
            },
        ],
        "exercises": [
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "amueblado", "options": ["furnished", "available", "expensive"], "expected_answer": "furnished", "skill_weights": {"vocabulary": 1.0}},
            {"type": "vocabulary", "instructions": "Elige la opción correcta.", "prompt": "gastos incluidos", "options": ["utilities included", "deposit required", "rent reduced"], "expected_answer": "utilities included", "skill_weights": {"vocabulary": 1.0}},
            {"type": "grammar", "instructions": "Completa con estar.", "prompt": "El piso ___ cerca del metro.", "options": None, "expected_answer": "está", "skill_weights": {"grammar": 1.0}},
            {"type": "grammar", "instructions": "Elige la pregunta cortés.", "prompt": "___ visitarlo mañana?", "options": ["¿Podría", "¿Podía", "¿Puedo que"], "expected_answer": "¿Podría", "skill_weights": {"grammar": 1.0}},
            {"type": "writing", "instructions": "Pregunta por una vivienda.", "prompt": "Escribe un mensaje con tres preguntas sobre un piso.", "options": None, "expected_answer": "Hola, llamo por el piso. ¿Está amueblado? ¿Cuánto cuesta? ¿Podría visitarlo mañana?", "skill_weights": {"writing": 1.0, "grammar": 0.5}},
            {"type": "listening", "instructions": "Escucha y elige.", "prompt": "¿Cuánto cuesta el piso?", "options": ["Novecientos euros", "Setecientos euros", "Mil euros"], "expected_answer": "Novecientos euros", "audio": True, "skill_weights": {"listening": 1.0}},
            {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": "Repite: ¿Podría visitarlo mañana por la tarde?", "options": None, "expected_answer": "¿Podría visitarlo mañana por la tarde?", "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
        ],
    },
    {
        "slug": "vitamina-a2-u1-conocernos",
        "title": "Vitamina A2 · U1: Vamos a conocernos",
        "cefr_level": "A2",
        "topics": ["Vitamina A2", "unidad 1", "gustos", "tiempo libre"],
        "source": "original companion",
        "status": "published",
        "grammar_tip": {"wrong": "A mí me gusta los idiomas.", "right": "A mí me gustan los idiomas.", "explanation": "Gustar concuerda con la cosa que gusta: singular gusta, plural gustan."},
        "segments": [
            {"start": 0.0, "end": 42.0, "transcript": [
                {"es": "Hola, soy Leo. En mi tiempo libre suelo quedar con mis vecinos.", "en": "Hi, I'm Leo. In my free time I usually meet my neighbours."},
                {"es": "A mí me encanta cocinar, pero no me gusta nada correr.", "en": "I love cooking, but I don't like running at all."},
                {"es": "Yo prefiero hacer excursiones y ver series en español.", "en": "I prefer going on hikes and watching series in Spanish."}],
             "phrases": [
                {"text": "en mi tiempo libre", "translation": "in my free time", "tip": "Une tiempo y libre con ritmo regular"},
                {"text": "me encanta cocinar", "translation": "I love cooking", "tip": "La c de cocinar suena como z en España"},
                {"text": "prefiero hacer excursiones", "translation": "I prefer going on hikes", "tip": "Marca el diptongo ie de prefiero"}]},
            {"start": 42.0, "end": 84.0, "transcript": [
                {"es": "¿Qué te resulta difícil cuando aprendes español?", "en": "What do you find difficult when learning Spanish?"},
                {"es": "Me cuesta entender conversaciones rápidas.", "en": "I find it hard to understand fast conversations."},
                {"es": "Puedes escuchar un poco cada día y practicar con nosotros.", "en": "You can listen a little every day and practise with us."}],
             "phrases": [
                {"text": "me cuesta entender", "translation": "I find it hard to understand", "tip": "Cuesta empieza con sonido k"},
                {"text": "conversaciones rápidas", "translation": "fast conversations", "tip": "Marca el acento de rápidas"},
                {"text": "practicar cada día", "translation": "practise every day", "tip": "La d de cada es suave"}]},
        ],
        "exercises": [
            {"type": "vocabulary", "instructions": "Elige la combinación correcta.", "prompt": "___ con amigos", "options": ["quedar", "jugar", "tomar"], "expected_answer": "quedar", "skill_weights": {"vocabulary": 1.0}},
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "me cuesta entender", "options": ["I find it hard to understand", "I want to understand", "I understand well"], "expected_answer": "I find it hard to understand", "skill_weights": {"vocabulary": 1.0}},
            {"type": "grammar", "instructions": "Completa con gustar.", "prompt": "A mí me ___ las excursiones.", "options": None, "expected_answer": "gustan", "skill_weights": {"grammar": 1.0}},
            {"type": "grammar", "instructions": "Da una recomendación.", "prompt": "Para mejorar, ___ escuchar español cada día.", "options": ["puedes", "gustas", "prefieres de"], "expected_answer": "puedes", "skill_weights": {"grammar": 1.0}},
            {"type": "writing", "instructions": "Preséntate al grupo.", "prompt": "Escribe qué te gusta, qué prefieres y qué te cuesta en español.", "options": None, "expected_answer": "Me gusta cocinar, prefiero hacer excursiones y me cuesta entender conversaciones rápidas.", "skill_weights": {"writing": 1.0, "grammar": 0.5}},
            {"type": "listening", "instructions": "Escucha y elige.", "prompt": "¿Qué le cuesta a Leo?", "options": ["Entender conversaciones rápidas", "Escribir correos", "Leer novelas"], "expected_answer": "Entender conversaciones rápidas", "audio": True, "skill_weights": {"listening": 1.0}},
            {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": "Repite: En mi tiempo libre suelo quedar con mis vecinos", "options": None, "expected_answer": "En mi tiempo libre suelo quedar con mis vecinos", "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
        ],
    },
    {
        "slug": "vitamina-a2-u2-mi-lugar",
        "title": "Vitamina A2 · U2: Mi lugar en el mundo",
        "cefr_level": "A2",
        "topics": ["Vitamina A2", "unidad 2", "rutinas", "ciudad y campo"],
        "source": "original companion",
        "status": "published",
        "grammar_tip": {"wrong": "Me levanto y después desayuno siempre.", "right": "Me levanto y después siempre desayuno.", "explanation": "Los adverbios de frecuencia suelen colocarse delante del verbo principal."},
        "segments": [
            {"start": 0.0, "end": 44.0, "transcript": [
                {"es": "Vivo fuera de mi país desde hace dos años.", "en": "I have lived outside my country for two years."},
                {"es": "Normalmente me levanto temprano, cojo el autobús y empiezo a trabajar a las nueve.", "en": "I normally get up early, take the bus and start work at nine."},
                {"es": "Lo más difícil es resolver trámites y entender algunas costumbres.", "en": "The hardest thing is handling paperwork and understanding some customs."}],
             "phrases": [
                {"text": "vivir fuera de mi país", "translation": "to live outside my country", "tip": "La v suena cercana a una b suave"},
                {"text": "cojo el autobús", "translation": "I take the bus", "tip": "La j de cojo es fuerte"},
                {"text": "resolver trámites", "translation": "handle paperwork", "tip": "Trámites lleva el acento al principio"}]},
            {"start": 44.0, "end": 88.0, "transcript": [
                {"es": "¿Prefieres vivir en el campo o en la ciudad?", "en": "Do you prefer living in the country or in the city?"},
                {"es": "La ciudad tiene más servicios, aunque también hay más ruido.", "en": "The city has more services, although there is also more noise."},
                {"es": "Yo elegiría un pueblo tranquilo cerca de una estación.", "en": "I would choose a quiet village near a station."}],
             "phrases": [
                {"text": "más servicios", "translation": "more services", "tip": "La s final se enlaza con la palabra siguiente"},
                {"text": "aunque hay más ruido", "translation": "although there is more noise", "tip": "Aunque empieza con sonido aun-ke"},
                {"text": "un pueblo tranquilo", "translation": "a quiet village", "tip": "Pronuncia juntas tr de tranquilo"}]},
        ],
        "exercises": [
            {"type": "vocabulary", "instructions": "Elige la acción de rutina.", "prompt": "Por la mañana ___ el autobús.", "options": ["cojo", "hago", "veo"], "expected_answer": "cojo", "skill_weights": {"vocabulary": 1.0}},
            {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": "resolver trámites", "options": ["handle paperwork", "find a flat", "change jobs"], "expected_answer": "handle paperwork", "skill_weights": {"vocabulary": 1.0}},
            {"type": "grammar", "instructions": "Completa el presente reflexivo.", "prompt": "Normalmente yo ___ levanto temprano.", "options": None, "expected_answer": "me", "skill_weights": {"grammar": 1.0}},
            {"type": "grammar", "instructions": "Completa el contraste.", "prompt": "La ciudad tiene más servicios, ___ hay más ruido.", "options": ["aunque", "porque de", "por eso que"], "expected_answer": "aunque", "skill_weights": {"grammar": 1.0}},
            {"type": "writing", "instructions": "Compara dos lugares.", "prompt": "Escribe ventajas e inconvenientes de vivir en la ciudad o en el campo.", "options": None, "expected_answer": "La ciudad tiene más servicios, aunque hay más ruido. El campo es tranquilo, pero hay menos transporte.", "skill_weights": {"writing": 1.0, "grammar": 0.5}},
            {"type": "listening", "instructions": "Escucha y elige.", "prompt": "¿Dónde elegiría vivir?", "options": ["En un pueblo tranquilo", "En el centro de una gran ciudad", "En otro país"], "expected_answer": "En un pueblo tranquilo", "audio": True, "skill_weights": {"listening": 1.0}},
            {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": "Repite: Normalmente me levanto temprano y cojo el autobús", "options": None, "expected_answer": "Normalmente me levanto temprano y cojo el autobús", "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
        ],
    },
    {
        "slug": "vitamina-a2-repaso-u1-u2",
        "title": "Vitamina A2 · Repaso U1–U2",
        "cefr_level": "A2",
        "topics": ["Vitamina A2", "repaso", "unidades 1 y 2"],
        "source": "original companion",
        "status": "published",
        "grammar_tip": {"wrong": "Me gusta hacer excursiones y me levanto a las siete normalmente.", "right": "Me gusta hacer excursiones y normalmente me levanto a las siete.", "explanation": "Repasa la concordancia de gustar y la posición de los adverbios de frecuencia."},
        "segments": [
            {"start": 0.0, "end": 45.0, "transcript": [
                {"es": "Me llamo Clara y vivo con mi familia en un barrio tranquilo.", "en": "My name is Clara and I live with my family in a quiet neighbourhood."},
                {"es": "Me encantan los idiomas y suelo estudiar con mis vecinos dos veces por semana.", "en": "I love languages and usually study with my neighbours twice a week."},
                {"es": "A veces me cuesta hablar, pero mis compañeros me ayudan.", "en": "Sometimes I find speaking difficult, but my classmates help me."}],
             "phrases": [
                {"text": "dos veces por semana", "translation": "twice a week", "tip": "Une veces y por suavemente"},
                {"text": "me cuesta hablar", "translation": "I find speaking difficult", "tip": "No marques demasiado la h de hablar: es muda"},
                {"text": "mis compañeros me ayudan", "translation": "my classmates help me", "tip": "Compañeros contiene el sonido ñ"}]},
            {"start": 45.0, "end": 90.0, "transcript": [
                {"es": "Normalmente estudio por la tarde después de volver a casa.", "en": "I normally study in the afternoon after returning home."},
                {"es": "Para mejorar la comprensión, escucho diálogos cortos todos los días.", "en": "To improve comprehension, I listen to short dialogues every day."},
                {"es": "Creo que vivir cerca de mis amigos hace el aprendizaje más fácil.", "en": "I think living near my friends makes learning easier."}],
             "phrases": [
                {"text": "después de volver", "translation": "after returning", "tip": "Después lleva el acento al final"},
                {"text": "para mejorar la comprensión", "translation": "to improve comprehension", "tip": "Comprensión termina con sílaba tónica"},
                {"text": "hace el aprendizaje más fácil", "translation": "makes learning easier", "tip": "La h de hace no se pronuncia"}]},
        ],
        "exercises": [
            {"type": "vocabulary", "instructions": "Repasa las combinaciones.", "prompt": "___ excursiones", "options": ["hacer", "tomar", "jugar"], "expected_answer": "hacer", "skill_weights": {"vocabulary": 1.0}},
            {"type": "vocabulary", "instructions": "Repasa la frecuencia.", "prompt": "twice a week", "options": ["dos veces por semana", "cada dos semanas", "toda la semana"], "expected_answer": "dos veces por semana", "skill_weights": {"vocabulary": 1.0}},
            {"type": "grammar", "instructions": "Completa con gustar.", "prompt": "A Clara le ___ los idiomas.", "options": None, "expected_answer": "encantan", "skill_weights": {"grammar": 1.0}},
            {"type": "grammar", "instructions": "Completa la rutina.", "prompt": "Normalmente ___ diálogos cortos todos los días.", "options": ["escucho", "escuchas", "escuchan"], "expected_answer": "escucho", "skill_weights": {"grammar": 1.0}},
            {"type": "writing", "instructions": "Haz el repaso final.", "prompt": "Preséntate, describe tu rutina y da un consejo para aprender español.", "options": None, "expected_answer": "Me llamo Clara, normalmente estudio por la tarde y recomiendo escuchar español todos los días.", "skill_weights": {"writing": 1.0, "grammar": 0.5}},
            {"type": "listening", "instructions": "Escucha y elige.", "prompt": "¿Qué hace Clara para mejorar la comprensión?", "options": ["Escucha diálogos cortos", "Lee novelas largas", "Viaja cada semana"], "expected_answer": "Escucha diálogos cortos", "audio": True, "skill_weights": {"listening": 1.0}},
            {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": "Repite: Suelo estudiar con mis vecinos dos veces por semana", "options": None, "expected_answer": "Suelo estudiar con mis vecinos dos veces por semana", "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
        ],
    },
]

LESSONS.extend(VIDEO_LESSONS)
LESSONS.extend(CURRICULUM_LESSONS)
enrich_lessons(LESSONS)
