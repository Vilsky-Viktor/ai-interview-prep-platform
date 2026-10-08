# Email texts in French. Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = (
    "Cet e-mail a été envoyé à {email} parce que vous êtes propriétaire ou admin d'une "
    "entreprise sur prepza."
)

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
    "digest": {
        "subject": "Votre récapitulatif d'activité sur prepza",
        "preheader": "Ce qui s'est passé dans vos entreprises ces dernières 24 heures.",
        "heading": "Votre récapitulatif d'activité",
        "lines": [
            "Voici ce qui s'est passé dans vos entreprises sur prepza ces dernières 24 heures.",
        ],
        "rows": {
            "candidate_finished": "Candidats ayant terminé : {count} · « {title} »",
            "invite_undelivered": "Invitations non remises : {count} · « {title} »",
            "ats_not_invited": "Candidats de l'ATS non invités : {count}",
            "interview_ready": "Entretien prêt : « {title} »",
        },
        "button": "Ouvrir prepza",
        "footer": (
            "Cet e-mail a été envoyé à {email} parce que vous êtes membre d'une entreprise "
            "sur prepza et recevez son récapitulatif d'activité."
        ),
    },
    "low_credits": {
        "subject": "Vos crédits sont bientôt épuisés",
        "preheader": "Rechargez pour continuer à inviter des candidats.",
        "heading": "Crédits bientôt épuisés",
        "lines": [
            (
                "Ces entreprises n'ont plus assez de crédits pour inviter un autre "
                "candidat. Rechargez pour continuer à inviter des candidats."
            ),
        ],
        "rows": {
            "company": "{company} · crédits disponibles : {available}",
        },
        "button": "Recharger",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "En attente de candidats",
        "preheader": "Invitez des candidats par e-mail ou partagez le lien de l'entretien.",
        "heading": "En attente de candidats",
        "lines": [
            (
                "Ces entretiens sont prêts depuis quelques jours, mais personne n'a encore "
                "été invité. Invitez des candidats par e-mail ou partagez le lien de "
                "l'entretien."
            ),
        ],
        "rows": {
            "interview": "« {title} » · {company}",
        },
        "button": "Inviter des candidats",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "Vos thèmes attendent votre relecture",
        "preheader": "Validez les thèmes, et les questions seront générées.",
        "heading": "Relisez vos thèmes",
        "lines": [
            (
                "Les thèmes des entretiens que vous avez lancés attendent votre relecture. "
                "Dès que vous les validez, les questions sont générées. Une relecture "
                "restée ouverte 14 jours est annulée."
            ),
        ],
        "rows": {
            "interview": "{company} · jours d'attente : {days}",
        },
        "button": "Relire les thèmes",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "Échec de la recharge automatique pour {company}",
        "preheader": (
            "La carte n'a pas pu être débitée. Rechargez pour continuer à inviter des candidats."
        ),
        "heading": "Échec de la recharge automatique",
        "lines": [
            (
                "La recharge automatique n'a pas pu débiter la carte pour {company}, aucun "
                "crédit n'a donc été ajouté."
            ),
            (
                "Rechargez pour continuer à inviter des candidats. La recharge automatique "
                "réessaiera la carte plus tard."
            ),
        ],
        "button": "Recharger",
        "footer": (
            "Cet e-mail a été envoyé à {email} parce que vous êtes propriétaire ou admin de"
            " {company} sur prepza. Il concerne la facturation de votre entreprise ; il est"
            " donc envoyé quels que soient vos réglages d'e-mails."
        ),
    },
    "footer": "Cet e-mail a été envoyé à {email} parce que quelqu'un a invité cette adresse sur "
    "prepza. Si vous ne l'attendiez pas, vous pouvez l'ignorer.",
    "paste_link": "Ou collez ce lien dans votre navigateur",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Se désabonner",
    "email_settings": "Modifier vos préférences d'e-mail",
    "stop_reminders": "Ne plus m'envoyer de rappels pour cet entretien",
    "stop_company": "Ne plus m'envoyer d'e-mails de la part de {company}",
}
