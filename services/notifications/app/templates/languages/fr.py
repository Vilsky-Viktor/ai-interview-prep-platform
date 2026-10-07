# Email texts in French. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
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
    "reminder": {
        "subject": "Rappel : {company} attend votre entretien",
        "preheader": "« {title} » est toujours ouvert. Connectez-vous avec {email} pour commencer.",
        "heading": "Votre entretien vous attend",
        "lines": [
            (
                "{company} vous a invité à l'entretien « {title} » sur prepza il y a quelques "
                "jours, et vous ne l'avez pas encore commencé."
            ),
            (
                "Connectez-vous avec {email} pour commencer. Seule cette adresse peut passer "
                "l'entretien, et vous n'avez qu'une tentative. L'invitation expire 30 jours "
                "après son envoi."
            ),
        ],
        "button": "Ouvrir l'invitation",
    },
    "report": {
        "subject": "Rapport de candidat : {candidate}",
        "preheader": "{candidate} a passé « {title} » chez {company}. Le rapport est en pièce jointe.",
        "heading": "Rapport de candidat",
        "lines": [
            "{sender} de {company} a partagé le rapport de {candidate} pour l'entretien « {title} ».",
            (
                "Il est joint sous forme de PDF d'une page : la note globale, le score de chaque "
                "thème et ce que le navigateur du candidat a montré. Répondez à cet e-mail pour "
                "répondre à {sender}."
            ),
        ],
        "button": "Visiter prepza",
        "footer": "Cet e-mail a été envoyé à {email} parce que {sender} a partagé un rapport de "
        "candidat avec cette adresse sur prepza. Si vous ne l'attendiez pas, vous pouvez "
        "l'ignorer.",
    },
    "candidates": {
        "subject": "Rapport de tous les candidats : {title}",
        "preheader": "Tous les candidats pour « {title} » chez {company}. Le rapport est en pièce jointe.",
        "heading": "Rapport des candidats",
        "lines": [
            "{sender} de {company} a partagé le rapport de tous les candidats pour l'entretien « {title} ».",
            (
                "Il est joint sous forme de PDF : la note de chaque candidat, sa progression et ce "
                "que son navigateur a montré, les meilleurs en premier. Répondez à cet e-mail pour "
                "répondre à {sender}."
            ),
        ],
        "button": "Visiter prepza",
        "footer": "Cet e-mail a été envoyé à {email} parce que {sender} a partagé un rapport des "
        "candidats avec cette adresse sur prepza. Si vous ne l'attendiez pas, vous pouvez "
        "l'ignorer.",
    },
    "footer": "Cet e-mail a été envoyé à {email} parce que quelqu'un a invité cette adresse sur "
    "prepza. Si vous ne l'attendiez pas, vous pouvez l'ignorer.",
    "paste_link": "Ou collez ce lien dans votre navigateur",
}
