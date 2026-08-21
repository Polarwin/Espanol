"""Short lessons cut from Spanish video sources.

``source_video`` paths are relative to the content dir (resolved at seed
time in load.py); the referenced files live in git-ignored ``content/sources/``.
"""

from typing import Any


def _lesson(slug: str, title: str, level: str, topics: list[str], source: str, start: float, end: float, transcript: list[list[tuple[str, str]]], phrases: list[list[tuple[str, str, str | None]]], grammar: tuple[str, str, str], exercises: list[dict]) -> dict[str, Any]:
    duration = end - start
    segment_length = duration / len(transcript)
    return {
        "slug": slug, "title": title, "cefr_level": level, "topics": topics,
        "source": "video-library", "status": "published",
        "source_video": {"path": source, "start": start, "end": end},
        "grammar_tip": {"wrong": grammar[0], "right": grammar[1], "explanation": grammar[2]},
        "segments": [
            {"start": i * segment_length, "end": (i + 1) * segment_length,
             "transcript": [{"es": es, "en": en} for es, en in lines],
             "phrases": [{"text": text, "translation": translation, "tip": tip} for text, translation, tip in phrases[i]]}
            for i, lines in enumerate(transcript)
        ],
        "exercises": exercises,
    }


def _ex(vocab: tuple[str, str], grammar_prompt: str, grammar_answer: str, writing: str, listen_q: str, listen_options: list[str], listen_answer: str, repeat: str) -> list[dict]:
    return [
        {"type": "vocabulary", "instructions": "Elige el significado.", "prompt": vocab[0], "options": [vocab[1], "otra cosa", "nunca"], "expected_answer": vocab[1], "skill_weights": {"vocabulary": 1.0}},
        {"type": "grammar", "instructions": "Completa la frase.", "prompt": grammar_prompt, "options": None, "expected_answer": grammar_answer, "skill_weights": {"grammar": 1.0}},
        {"type": "writing", "instructions": "Responde con tus palabras.", "prompt": writing, "options": None, "expected_answer": repeat, "skill_weights": {"writing": 1.0, "fluency": 0.3}},
        {"type": "listening", "instructions": "Escucha y elige.", "prompt": listen_q, "options": listen_options, "expected_answer": listen_answer, "audio": True, "skill_weights": {"listening": 1.0}},
        {"type": "pronunciation", "instructions": "Escucha y repite.", "prompt": f"Repite: {repeat}", "options": None, "expected_answer": repeat, "audio": True, "skill_weights": {"pronunciation": 1.0, "fluency": 0.5}},
    ]


VIDEO_LESSONS = [
    _lesson("video-a1-aprender-juntos", "Aprender juntos", "A1", ["estudios", "amistad"], "sources/basic-conversations.webm", 10, 109,
      [[("¿Tú también hablas español?", "Do you also speak Spanish?"), ("Solo un poco. Todavía estoy aprendiendo.", "Only a little. I am still learning.")], [("¿Cómo se dice good morning?", "How do you say good morning?"), ("Se dice buenos días.", "You say buenos días.")], [("Practico con mis amigos y veo vídeos en español.", "I practise with friends and watch videos in Spanish."), ("Sigue practicando todos los días.", "Keep practising every day.")]],
      [[("todavía estoy aprendiendo", "I am still learning", None)], [("¿Cómo se dice...?", "How do you say...?", None)], [("seguir practicando", "keep practising", None)]],
      ("Yo habla español.", "Yo hablo español.", "Con yo, el presente termina normalmente en -o."),
      _ex(("con fluidez", "fluently"), "Yo ___ español con mis amigos.", "hablo", "¿Cómo practicas español?", "¿Qué aprende la persona?", ["Español", "Francés", "Alemán"], "Español", "Todavía estoy aprendiendo.")),
    _lesson("video-a2-ruta-senderismo", "Una ruta de senderismo", "A2", ["planes", "naturaleza"], "sources/weekend-plans.webm", 20, 162,
      [[("Quedamos a las ocho en la parada de autobús.", "We meet at eight at the bus stop."), ("A esa hora el bosque está tranquilo y fresquito.", "At that time the forest is quiet and cool.")], [("La ruta dura unas dos horas, a ritmo tranquilo.", "The route lasts about two hours at an easy pace."), ("Lleva agua y calzado cómodo.", "Bring water and comfortable footwear.")], [("De momento somos cinco. Tú serías el sexto.", "For now there are five of us. You would be the sixth."), ("El viernes te lo confirmo.", "I will confirm on Friday.")]],
      [[("quedar a las ocho", "meet at eight", None)], [("a ritmo tranquilo", "at an easy pace", None)], [("confirmarlo", "confirm it", None)]],
      ("¿Cuánto dura la ruta? Dos horas dura.", "¿Cuánto dura la ruta? Dura dos horas.", "En una respuesta neutra colocamos el verbo antes de la duración."),
      _ex(("calzado cómodo", "comfortable footwear"), "La ruta ___ dos horas.", "dura", "¿Aceptarías esta excursión? Explica por qué.", "¿Qué deben llevar?", ["Agua y calzado cómodo", "Una maleta", "Un ordenador"], "Agua y calzado cómodo", "El viernes te lo confirmo.")),
    _lesson("video-b1-mensajes-intencion", "Mensajes con intención", "B1", ["comunicación", "trabajo"], "sources/answer-the-phone-b1.mkv", 155, 280,
      [[("Necesito que me envíes la última factura.", "I need you to send me the latest invoice."), ("¿Me la puedes enviar, por favor?", "Can you send it to me, please?")], [("Tenemos el gusto de invitaros a la ceremonia civil.", "We are pleased to invite you to the civil ceremony."), ("Se ruega confirmación.", "Confirmation is requested.")], [("Le comunicamos la entrada en vigor de las nuevas medidas.", "We inform you that the new measures take effect."), ("Esperamos que esta información sea de su interés.", "We hope this information is of interest to you.")]],
      [[("enviar la factura", "send the invoice", None)], [("se ruega confirmación", "please confirm", None)], [("entrada en vigor", "coming into effect", None)]],
      ("Necesito que me envías la factura.", "Necesito que me envíes la factura.", "Después de «necesito que» usamos presente de subjuntivo."),
      _ex(("entrada en vigor", "coming into effect"), "Necesito que me ___ la factura.", "envíes", "Escribe un mensaje formal para pedir un documento.", "¿Qué pide el primer mensaje?", ["Una factura", "Una invitación", "Una reserva"], "Una factura", "Necesito que me envíes la última factura.")),
]
