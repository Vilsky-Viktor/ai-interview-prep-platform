# Email texts in French. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} vous invite à « {title} »",
        "preheader": "Connectez-vous avec {email} pour commencer à vous préparer.",
        "heading": "Une préparation pour vous",
        "lines": [
            "{inviter} vous invite à vous préparer avec « {title} » sur prepza.",
            (
                "Connectez-vous avec {email} pour rejoindre. Seule cette adresse peut "
                "accepter l'invitation."
            ),
        ],
        "button": "Ouvrir l'invitation",
    },
    "candidate": {
        "subject": "{company} vous invite à un entretien",
        "preheader": "Passez « {title} » sur prepza. Connectez-vous avec {email} pour commencer.",
        "heading": "Invitation à un entretien",
        "lines": [
            "{company} vous invite à l'entretien « {title} » sur prepza.",
            (
                "Connectez-vous avec {email} pour commencer. Seule cette adresse "
                "peut passer l'entretien, et vous n'avez qu'une tentative."
            ),
        ],
        "button": "Ouvrir l'invitation",
    },
    "footer": "Cet e-mail a été envoyé à {email} parce que quelqu'un a invité cette adresse sur "
    "prepza. Si vous ne l'attendiez pas, vous pouvez l'ignorer.",
    "paste_link": "Ou collez ce lien dans votre navigateur",
}
