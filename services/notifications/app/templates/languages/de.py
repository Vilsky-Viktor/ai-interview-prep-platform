# Email texts in German. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "candidate": {
        "subject": "{company} lädt Sie zu einem Interview ein",
        "preheader": "Absolvieren Sie „{title}“ auf prepza. Melden Sie sich mit "
        "{email} an, um zu beginnen.",
        "heading": "Einladung zum Interview",
        "lines": [
            "{company} lädt Sie zum Interview „{title}“ auf prepza ein.",
            (
                "Melden Sie sich mit {email} an, um zu beginnen. Nur diese Adresse "
                "kann das Interview absolvieren, und Sie haben einen Versuch."
            ),
        ],
        "button": "Einladung öffnen",
    },
    "reminder": {
        "subject": "Erinnerung: {company} wartet auf Ihr Interview",
        "preheader": "„{title}“ ist noch offen. Melden Sie sich mit {email} an, um zu beginnen.",
        "heading": "Ihr Interview wartet",
        "lines": [
            (
                "{company} hat Sie vor einigen Tagen zum Interview „{title}“ auf "
                "prepza eingeladen, und Sie haben es noch nicht begonnen."
            ),
            (
                "Melden Sie sich mit {email} an, um zu beginnen. Nur diese Adresse kann das "
                "Interview absolvieren, und Sie haben einen Versuch. Die Einladung läuft 30 Tage "
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
                "und was der Browser des Kandidaten gezeigt hat. Antworten Sie auf diese E-Mail, "
                "um {sender} zu antworten."
            ),
        ],
        "button": "prepza besuchen",
        "footer": "Diese E-Mail wurde an {email} gesendet, weil {sender} einen Kandidatenbericht "
        "mit dieser Adresse auf prepza geteilt hat. Wenn Sie sie nicht erwartet haben, können "
        "Sie sie ignorieren.",
    },
    "candidates": {
        "subject": "Bericht aller Kandidaten: {title}",
        "preheader": "Alle Kandidaten für „{title}“ bei {company}. Der Bericht ist angehängt.",
        "heading": "Kandidatenbericht",
        "lines": [
            "{sender} von {company} hat den Bericht aller Kandidaten zum Interview „{title}“ geteilt.",
            (
                "Er ist als PDF angehängt: Ergebnis, Fortschritt und was der Browser jedes Kandidaten "
                "gezeigt hat, die Besten zuerst. Antworten Sie auf diese E-Mail, um {sender} zu "
                "antworten."
            ),
        ],
        "button": "prepza besuchen",
        "footer": "Diese E-Mail wurde an {email} gesendet, weil {sender} einen Kandidatenbericht "
        "mit dieser Adresse auf prepza geteilt hat. Wenn Sie sie nicht erwartet haben, können "
        "Sie sie ignorieren.",
    },
    "footer": "Diese E-Mail wurde an {email} gesendet, weil jemand diese Adresse auf prepza "
    "eingeladen hat. Wenn Sie sie nicht erwartet haben, können Sie sie ignorieren.",
    "paste_link": "Oder fügen Sie diesen Link in Ihren Browser ein",
}
