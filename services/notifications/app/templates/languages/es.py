# Email texts in Spanish. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "candidate": {
        "subject": "{company} te invita a una entrevista",
        "preheader": "Haz «{title}» en prepza. Inicia sesión con {email} para empezar.",
        "heading": "Invitación a una entrevista",
        "lines": [
            "{company} te invita a la entrevista «{title}» en prepza.",
            (
                "Inicia sesión con {email} para empezar. Solo esta dirección puede "
                "hacer la entrevista, y tienes un solo intento."
            ),
        ],
        "button": "Abrir la invitación",
    },
    "reminder": {
        "subject": "Recordatorio: {company} espera tu entrevista",
        "preheader": "«{title}» sigue abierta. Inicia sesión con {email} para empezar.",
        "heading": "Tu entrevista te espera",
        "lines": [
            (
                "{company} te invitó a la entrevista «{title}» en prepza hace unos días, y aún "
                "no la has empezado."
            ),
            (
                "Inicia sesión con {email} para empezar. Solo esta dirección puede hacer la "
                "entrevista, y tienes un solo intento. La invitación caduca 30 días después de "
                "su envío."
            ),
        ],
        "button": "Abrir la invitación",
    },
    "report": {
        "subject": "Informe de candidato: {candidate}",
        "preheader": "{candidate} hizo «{title}» en {company}. El informe va adjunto.",
        "heading": "Informe de candidato",
        "lines": [
            "{sender} de {company} compartió el informe de {candidate} de la entrevista «{title}».",
            (
                "Va adjunto como PDF de una página: la nota general, la puntuación de cada tema "
                "y lo que registró el navegador del candidato. Responde a este correo para "
                "contestar a {sender}."
            ),
        ],
        "button": "Visitar prepza",
        "footer": "Este correo se envió a {email} porque {sender} compartió un informe de "
        "candidato con esta dirección en prepza. Si no lo esperabas, puedes ignorarlo.",
    },
    "candidates": {
        "subject": "Informe de todos los candidatos: {title}",
        "preheader": "Todos los candidatos de «{title}» en {company}. El informe va adjunto.",
        "heading": "Informe de candidatos",
        "lines": [
            "{sender} de {company} compartió el informe de todos los candidatos de la entrevista «{title}».",
            (
                "Va adjunto como PDF: la nota de cada candidato, su progreso y lo que registró su "
                "navegador, los mejores primero. Responde a este correo para contestar a {sender}."
            ),
        ],
        "button": "Visitar prepza",
        "footer": "Este correo se envió a {email} porque {sender} compartió un informe de "
        "candidatos con esta dirección en prepza. Si no lo esperabas, puedes ignorarlo.",
    },
    "footer": "Este correo se envió a {email} porque alguien invitó a esta dirección en prepza. "
    "Si no lo esperabas, puedes ignorarlo.",
    "paste_link": "O pega este enlace en tu navegador",
}
