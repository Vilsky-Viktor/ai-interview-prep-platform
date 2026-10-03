# Email texts in Spanish. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} te invita a «{title}»",
        "preheader": "Inicia sesión con {email} para empezar a prepararte.",
        "heading": "Una preparación para ti",
        "lines": [
            "{inviter} te invita a prepararte con «{title}» en prepza.",
            (
                "Inicia sesión con {email} para unirte. Solo esta dirección puede "
                "aceptar la invitación."
            ),
        ],
        "button": "Abrir la invitación",
    },
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
    "footer": "Este correo se envió a {email} porque alguien invitó a esta dirección en prepza. "
    "Si no lo esperabas, puedes ignorarlo.",
    "paste_link": "O pega este enlace en tu navegador",
}
