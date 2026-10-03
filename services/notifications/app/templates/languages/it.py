# Email texts in Italian. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} ti invita a «{title}»",
        "preheader": "Accedi con {email} per iniziare a prepararti.",
        "heading": "Una preparazione per te",
        "lines": [
            "{inviter} ti invita a prepararti con «{title}» su prepza.",
            "Accedi con {email} per partecipare. Solo questo indirizzo può accettare l'invito.",
        ],
        "button": "Apri l'invito",
    },
    "candidate": {
        "subject": "{company} ti invita a un colloquio",
        "preheader": "Svolgi «{title}» su prepza. Accedi con {email} per iniziare.",
        "heading": "Invito a un colloquio",
        "lines": [
            "{company} ti invita al colloquio «{title}» su prepza.",
            (
                "Accedi con {email} per iniziare. Solo questo indirizzo può svolgere "
                "il colloquio, e hai un solo tentativo."
            ),
        ],
        "button": "Apri l'invito",
    },
    "footer": "Questa email è stata inviata a {email} perché qualcuno ha invitato questo "
    "indirizzo su prepza. Se non te l'aspettavi, puoi ignorarla.",
    "paste_link": "Oppure incolla questo link nel tuo browser",
}
