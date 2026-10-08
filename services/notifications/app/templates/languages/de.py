# Email texts in German. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "candidate": {
        "subject": "{company} lädt dich zu einem Interview ein",
        "preheader": "Absolviere „{title}“ auf prepza. Melde dich mit {email} an, um zu beginnen.",
        "heading": "Einladung zum Interview",
        "lines": [
            "{company} lädt dich zum Interview „{title}“ auf prepza ein.",
            (
                "Melde dich mit {email} an, um zu beginnen. Nur diese Adresse "
                "kann das Interview absolvieren, und du hast einen Versuch."
            ),
        ],
        "button": "Einladung öffnen",
    },
    "reminder": {
        "subject": "Erinnerung: {company} wartet auf dein Interview",
        "preheader": "„{title}“ ist noch offen. Melde dich mit {email} an, um zu beginnen.",
        "heading": "Dein Interview wartet",
        "lines": [
            (
                "{company} hat dich vor einigen Tagen zum Interview „{title}“ auf "
                "prepza eingeladen, und du hast es noch nicht begonnen."
            ),
            (
                "Melde dich mit {email} an, um zu beginnen. Nur diese Adresse kann das "
                "Interview absolvieren, und du hast einen Versuch. Die Einladung läuft 30 Tage "
                "nach dem Versand ab."
            ),
        ],
        "button": "Einladung öffnen",
    },
    "report": {
        "subject": "Kandidatenbericht: {candidate}",
        "preheader": "{candidate} hat „{title}“ bei {company} absolviert. Der Bericht ist angehängt.",
        "heading": "Kandidatenbericht",
        "lines": [
            "{sender} von {company} hat den Bericht von {candidate} zum Interview „{title}“ geteilt.",
            (
                "Er ist als einseitiges PDF angehängt: das Gesamtergebnis, das Ergebnis jedes Themas "
                "und was der Browser des Kandidaten gezeigt hat. Antworte auf diese E-Mail, "
                "um {sender} zu antworten."
            ),
        ],
        "button": "prepza besuchen",
        "footer": "Diese E-Mail wurde an {email} gesendet, weil {sender} einen Kandidatenbericht "
        "mit dieser Adresse auf prepza geteilt hat. Wenn du sie nicht erwartet hast, kannst "
        "du sie ignorieren.",
    },
    "candidates": {
        "subject": "Bericht aller Kandidaten: {title}",
        "preheader": "Alle Kandidaten für „{title}“ bei {company}. Der Bericht ist angehängt.",
        "heading": "Kandidatenbericht",
        "lines": [
            "{sender} von {company} hat den Bericht aller Kandidaten zum Interview „{title}“ geteilt.",
            (
                "Er ist als PDF angehängt: Ergebnis, Fortschritt und was der Browser jedes Kandidaten "
                "gezeigt hat, die Besten zuerst. Antworte auf diese E-Mail, um {sender} zu "
                "antworten."
            ),
        ],
        "button": "prepza besuchen",
        "footer": "Diese E-Mail wurde an {email} gesendet, weil {sender} einen Kandidatenbericht "
        "mit dieser Adresse auf prepza geteilt hat. Wenn du sie nicht erwartet hast, kannst "
        "du sie ignorieren.",
    },
    "footer": "Diese E-Mail wurde an {email} gesendet, weil jemand diese Adresse auf prepza "
    "eingeladen hat. Wenn du sie nicht erwartet hast, kannst du sie ignorieren.",
    "paste_link": "Oder füge diesen Link in deinen Browser ein",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Abmelden",
    "email_settings": "E-Mail-Einstellungen ändern",
    "stop_reminders": "Keine Erinnerungen mehr zu diesem Interview",
    "stop_company": "Keine E-Mails mehr von {company}",
}
