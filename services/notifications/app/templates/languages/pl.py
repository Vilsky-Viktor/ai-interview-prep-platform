# Email texts in Polish. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} zaprasza Cię do „{title}”",
        "preheader": "Zaloguj się adresem {email}, aby zacząć przygotowania.",
        "heading": "Przygotowanie dla Ciebie",
        "lines": [
            "{inviter} zaprasza Cię do przygotowań z „{title}” w prepza.",
            "Zaloguj się adresem {email}, aby dołączyć. Tylko ten adres może przyjąć zaproszenie.",
        ],
        "button": "Otwórz zaproszenie",
    },
    "candidate": {
        "subject": "{company} zaprasza Cię na rozmowę kwalifikacyjną",
        "preheader": "Weź udział w „{title}” w prepza. Zaloguj się adresem {email}, aby zacząć.",
        "heading": "Zaproszenie na rozmowę",
        "lines": [
            "{company} zaprasza Cię na rozmowę „{title}” w prepza.",
            (
                "Zaloguj się adresem {email}, aby zacząć. Tylko ten adres może wziąć "
                "udział w rozmowie i masz jedną próbę."
            ),
        ],
        "button": "Otwórz zaproszenie",
    },
    "footer": "Ta wiadomość została wysłana na {email}, ponieważ ktoś zaprosił ten adres w "
    "prepza. Jeśli się jej nie spodziewasz, możesz ją zignorować.",
    "paste_link": "Lub wklej ten link do przeglądarki",
}
