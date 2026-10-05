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
                "udział w rozmowie i masz jedną próbę."
            ),
        ],
        "button": "Otwórz zaproszenie",
    },
    "reminder": {
        "subject": "Przypomnienie: {company} czeka na Twoją rozmowę",
        "preheader": "„{title}” jest nadal otwarta. Zaloguj się adresem {email}, aby zacząć.",
        "heading": "Twoja rozmowa czeka",
        "lines": [
            (
                "{company} zaprosiła Cię kilka dni temu na rozmowę „{title}” w prepza, a Ty "
                "jeszcze jej nie zacząłeś."
            ),
            (
                "Zaloguj się adresem {email}, aby zacząć. Tylko ten adres może wziąć udział w "
                "rozmowie i masz jedną próbę. Zaproszenie wygasa 30 dni po wysłaniu."
            ),
        ],
        "button": "Otwórz zaproszenie",
    },
    "report": {
        "subject": "{sender} udostępnił raport kandydata: {candidate}",
        "preheader": "{candidate} rozwiązał „{title}” w {company}. Raport jest w załączniku.",
        "heading": "Raport kandydata",
        "lines": [
            "{sender} z {company} udostępnił raport kandydata {candidate} z rozmowy „{title}”.",
            (
                "Jest w załączniku jako jednostronicowy PDF: ocena ogólna, wynik z każdego tematu "
                "i to, co pokazała przeglądarka kandydata. Odpowiedz na tę wiadomość, aby "
                "odpisać {sender}."
            ),
        ],
        "button": "Odwiedź prepza",
        "footer": "Ta wiadomość została wysłana na {email}, ponieważ {sender} udostępnił temu "
        "adresowi raport kandydata w prepza. Jeśli się jej nie spodziewasz, możesz ją zignorować.",
    },
    "candidates": {
        "subject": "{sender} udostępnił raport wszystkich kandydatów: {title}",
        "preheader": "Wszyscy kandydaci do „{title}” w {company}. Raport jest w załączniku.",
        "heading": "Raport kandydatów",
        "lines": [
            "{sender} z {company} udostępnił raport wszystkich kandydatów z rozmowy „{title}”.",
            (
                "Jest w załączniku jako PDF: ocena i postęp każdego kandydata oraz to, co pokazała "
                "jego przeglądarka, od najlepszych. Odpowiedz na tę wiadomość, aby odpisać {sender}."
            ),
        ],
        "button": "Odwiedź prepza",
        "footer": "Ta wiadomość została wysłana na {email}, ponieważ {sender} udostępnił temu "
        "adresowi raport kandydatów w prepza. Jeśli się jej nie spodziewasz, możesz ją zignorować.",
    },
    "footer": "Ta wiadomość została wysłana na {email}, ponieważ ktoś zaprosił ten adres w "
    "prepza. Jeśli się jej nie spodziewasz, możesz ją zignorować.",
    "paste_link": "Lub wklej ten link do przeglądarki",
}
