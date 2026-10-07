# Email texts in Polish. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "candidate": {
        "subject": "{company} zaprasza Cię na rozmowę kwalifikacyjną",
        "preheader": "Weź udział w „{title}” w prepza. Zaloguj się adresem {email}, aby zacząć.",
        "heading": "Zaproszenie na rozmowę",
        "lines": [
            "{company} zaprasza Cię na rozmowę „{title}” w prepza.",
            (
                "Zaloguj się adresem {email}, aby zacząć. Tylko ten adres może wziąć "
                "udział w rozmowie i masz jedno podejście."
            ),
        ],
        "button": "Otwórz zaproszenie",
    },
    "reminder": {
        "subject": "Przypomnienie: {company} czeka na Twoją rozmowę",
        "preheader": "Rozmowa „{title}” jest nadal otwarta. Zaloguj się adresem {email}, aby zacząć.",
        "heading": "Twoja rozmowa czeka",
        "lines": [
            (
                "Zaproszenie od {company} na rozmowę „{title}” w prepza czeka od kilku dni, "
                "a rozmowa nie została jeszcze rozpoczęta."
            ),
            (
                "Zaloguj się adresem {email}, aby zacząć. Tylko ten adres może wziąć udział w "
                "rozmowie i masz jedno podejście. Zaproszenie wygasa 30 dni po wysłaniu."
            ),
        ],
        "button": "Otwórz zaproszenie",
    },
    "report": {
        "subject": "Raport kandydata: {candidate}",
        "preheader": "Kandydat {candidate} ukończył rozmowę „{title}” w firmie {company}. Raport jest w załączniku.",
        "heading": "Raport kandydata",
        "lines": [
            "{sender} z firmy {company} udostępnił(a) raport kandydata {candidate} z rozmowy „{title}”.",
            (
                "Jest w załączniku jako jednostronicowy PDF: wynik ogólny, wynik z każdego tematu "
                "i to, co pokazała przeglądarka kandydata. Odpowiedz na tę wiadomość, aby "
                "odpisać {sender}."
            ),
        ],
        "button": "Odwiedź prepza",
        "footer": "Ta wiadomość została wysłana na {email}, ponieważ {sender} udostępnił(a) temu "
        "adresowi raport kandydata w prepza. Jeśli się jej nie spodziewasz, możesz ją zignorować.",
    },
    "candidates": {
        "subject": "Raport wszystkich kandydatów: {title}",
        "preheader": "Wszyscy kandydaci z rozmowy „{title}” w firmie {company}. Raport jest w załączniku.",
        "heading": "Raport kandydatów",
        "lines": [
            "{sender} z firmy {company} udostępnił(a) raport wszystkich kandydatów z rozmowy „{title}”.",
            (
                "Jest w załączniku jako PDF: wynik i postęp każdego kandydata oraz to, co pokazała "
                "jego przeglądarka, od najlepszych. Odpowiedz na tę wiadomość, aby odpisać {sender}."
            ),
        ],
        "button": "Odwiedź prepza",
        "footer": "Ta wiadomość została wysłana na {email}, ponieważ {sender} udostępnił(a) temu "
        "adresowi raport kandydatów w prepza. Jeśli się jej nie spodziewasz, możesz ją zignorować.",
    },
    "footer": "Ta wiadomość została wysłana na {email}, ponieważ ktoś zaprosił ten adres w "
    "prepza. Jeśli się jej nie spodziewasz, możesz ją zignorować.",
    "paste_link": "Lub wklej ten link do przeglądarki",
}
