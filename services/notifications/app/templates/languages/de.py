# Email texts in German. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} lädt dich zu „{title}“ ein",
        "preheader": "Melde dich mit {email} an, um mit der Vorbereitung zu beginnen.",
        "heading": "Eine Vorbereitung für dich",
        "lines": [
            "{inviter} lädt dich ein, dich mit „{title}“ auf prepza vorzubereiten.",
            (
                "Melde dich mit {email} an, um beizutreten. Nur diese Adresse kann die "
                "Einladung annehmen."
            ),
        ],
        "button": "Einladung öffnen",
    },
    "candidate": {
        "subject": "{company} lädt Sie zu einem Vorstellungsgespräch ein",
        "preheader": "Absolvieren Sie „{title}“ auf prepza. Melden Sie sich mit "
        "{email} an, um zu beginnen.",
        "heading": "Einladung zum Vorstellungsgespräch",
        "lines": [
            "{company} lädt Sie zum Vorstellungsgespräch „{title}“ auf prepza ein.",
            (
                "Melden Sie sich mit {email} an, um zu beginnen. Nur diese Adresse "
                "kann das Gespräch absolvieren, und Sie haben einen Versuch."
            ),
        ],
        "button": "Einladung öffnen",
    },
    "footer": "Diese E-Mail wurde an {email} gesendet, weil jemand diese Adresse auf prepza "
    "eingeladen hat. Wenn Sie sie nicht erwartet haben, können Sie sie ignorieren.",
    "paste_link": "Oder fügen Sie diesen Link in Ihren Browser ein",
}
