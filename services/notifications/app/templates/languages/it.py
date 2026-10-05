# Email texts in Italian. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
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
    "reminder": {
        "subject": "Promemoria: {company} aspetta il tuo colloquio",
        "preheader": "«{title}» è ancora aperto. Accedi con {email} per iniziare.",
        "heading": "Il tuo colloquio ti aspetta",
        "lines": [
            (
                "{company} ti ha invitato al colloquio «{title}» su prepza qualche giorno fa, e "
                "non l'hai ancora iniziato."
            ),
            (
                "Accedi con {email} per iniziare. Solo questo indirizzo può svolgere il "
                "colloquio, e hai un solo tentativo. L'invito scade 30 giorni dopo l'invio."
            ),
        ],
        "button": "Apri l'invito",
    },
    "report": {
        "subject": "{sender} ha condiviso il report di un candidato: {candidate}",
        "preheader": "{candidate} ha svolto «{title}» presso {company}. Il report è in allegato.",
        "heading": "Report del candidato",
        "lines": [
            "{sender} di {company} ha condiviso il report di {candidate} per il colloquio «{title}».",
            (
                "È allegato come PDF di una pagina: il voto complessivo, il punteggio di ogni "
                "argomento e cosa ha mostrato il browser del candidato. Rispondi a questa email "
                "per rispondere a {sender}."
            ),
        ],
        "button": "Visita prepza",
        "footer": "Questa email è stata inviata a {email} perché {sender} ha condiviso il report "
        "di un candidato con questo indirizzo su prepza. Se non te l'aspettavi, puoi ignorarla.",
    },
    "candidates": {
        "subject": "{sender} ha condiviso il report di tutti i candidati: {title}",
        "preheader": "Tutti i candidati per «{title}» presso {company}. Il report è in allegato.",
        "heading": "Report dei candidati",
        "lines": [
            "{sender} di {company} ha condiviso il report di tutti i candidati per il colloquio «{title}».",
            (
                "È allegato come PDF: il voto di ogni candidato, i suoi progressi e cosa ha mostrato "
                "il suo browser, dai migliori in giù. Rispondi a questa email per rispondere a "
                "{sender}."
            ),
        ],
        "button": "Visita prepza",
        "footer": "Questa email è stata inviata a {email} perché {sender} ha condiviso il report "
        "dei candidati con questo indirizzo su prepza. Se non te l'aspettavi, puoi ignorarla.",
    },
    "footer": "Questa email è stata inviata a {email} perché qualcuno ha invitato questo "
    "indirizzo su prepza. Se non te l'aspettavi, puoi ignorarla.",
    "paste_link": "Oppure incolla questo link nel tuo browser",
}
