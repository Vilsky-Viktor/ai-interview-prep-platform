# Email texts in Portuguese. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} convida você para “{title}”",
        "preheader": "Entre com {email} para começar a se preparar.",
        "heading": "Uma preparação para você",
        "lines": [
            "{inviter} convida você a se preparar com “{title}” no prepza.",
            "Entre com {email} para participar. Só este endereço pode aceitar o convite.",
        ],
        "button": "Abrir o convite",
    },
    "candidate": {
        "subject": "{company} convida você para uma entrevista",
        "preheader": "Faça “{title}” no prepza. Entre com {email} para começar.",
        "heading": "Convite para entrevista",
        "lines": [
            "{company} convida você para a entrevista “{title}” no prepza.",
            (
                "Entre com {email} para começar. Só este endereço pode fazer a "
                "entrevista, e você tem uma única tentativa."
            ),
        ],
        "button": "Abrir o convite",
    },
    "footer": "Este e-mail foi enviado para {email} porque alguém convidou este endereço no "
    "prepza. Se você não esperava por ele, pode ignorá-lo.",
    "paste_link": "Ou cole este link no seu navegador",
}
