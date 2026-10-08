# Email texts in Spanish. Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = (
    "Este correo se envió a {email} porque eres propietario o administrador de una empresa "
    "en prepza."
)

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
    "digest": {
        "subject": "Tu resumen de actividad en prepza",
        "preheader": "Lo que pasó en tus empresas en las últimas 24 horas.",
        "heading": "Tu resumen de actividad",
        "lines": [
            "Esto es lo que pasó en tus empresas en prepza en las últimas 24 horas.",
        ],
        "rows": {
            "candidate_finished": "Candidatos que terminaron: {count} · «{title}»",
            "invite_undelivered": "Invitaciones no entregadas: {count} · «{title}»",
            "ats_not_invited": "Candidatos del ATS no invitados: {count}",
            "interview_ready": "Entrevista lista: «{title}»",
        },
        "button": "Abrir prepza",
        "footer": (
            "Este correo se envió a {email} porque eres miembro de una empresa en prepza y "
            "recibes su resumen de actividad."
        ),
    },
    "low_credits": {
        "subject": "Te estás quedando sin créditos",
        "preheader": "Recarga para seguir invitando a candidatos.",
        "heading": "Se están acabando los créditos",
        "lines": [
            (
                "Estas empresas no tienen créditos suficientes para invitar a otro "
                "candidato. Recarga para seguir invitando a candidatos."
            ),
        ],
        "rows": {
            "company": "{company} · créditos disponibles: {available}",
        },
        "button": "Recargar",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "Esperando candidatos",
        "preheader": "Invita a candidatos por correo o comparte el enlace de la entrevista.",
        "heading": "Esperando candidatos",
        "lines": [
            (
                "Estas entrevistas están listas desde hace unos días, pero aún no se ha "
                "invitado a nadie. Invita a candidatos por correo o comparte el enlace de "
                "la entrevista."
            ),
        ],
        "rows": {
            "interview": "«{title}» · {company}",
        },
        "button": "Invitar a candidatos",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "Tus temas esperan tu revisión",
        "preheader": "Confirma los temas y se generarán las preguntas.",
        "heading": "Revisa tus temas",
        "lines": [
            (
                "Los temas de las entrevistas que iniciaste esperan tu revisión. Cuando los"
                " confirmes, se generarán las preguntas. Una revisión que quede abierta 14 "
                "días se cancela."
            ),
        ],
        "rows": {
            "interview": "{company} · días de espera: {days}",
        },
        "button": "Revisar los temas",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "Falló la recarga automática de {company}",
        "preheader": "No se pudo cobrar a la tarjeta. Recarga para seguir invitando a candidatos.",
        "heading": "Falló la recarga automática",
        "lines": [
            (
                "La recarga automática no pudo cobrar a la tarjeta de {company}, así que no"
                " se añadieron créditos."
            ),
            (
                "Recarga para seguir invitando a candidatos. La recarga automática volverá "
                "a intentarlo con la tarjeta más tarde."
            ),
        ],
        "button": "Recargar",
        "footer": (
            "Este correo se envió a {email} porque eres propietario o administrador de "
            "{company} en prepza. Trata sobre la facturación de tu empresa, así que se "
            "envía sin importar tu configuración de correo."
        ),
    },
    "footer": "Este correo se envió a {email} porque alguien invitó a esta dirección en prepza. "
    "Si no lo esperabas, puedes ignorarlo.",
    "paste_link": "O pega este enlace en tu navegador",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Cancelar la suscripción",
    "email_settings": "Cambiar tu configuración de correo",
    "stop_reminders": "No enviarme más recordatorios de esta entrevista",
    "stop_company": "No enviarme más correos de {company}",
}
