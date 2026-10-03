# Email texts in Dutch. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} nodigt je uit voor “{title}”",
        "preheader": "Log in met {email} om te beginnen met voorbereiden.",
        "heading": "Een voorbereiding voor jou",
        "lines": [
            "{inviter} nodigt je uit om je voor te bereiden met “{title}” op prepza.",
            "Log in met {email} om mee te doen. Alleen dit adres kan de uitnodiging accepteren.",
        ],
        "button": "Uitnodiging openen",
    },
    "candidate": {
        "subject": "{company} nodigt je uit voor een sollicitatiegesprek",
        "preheader": "Doe “{title}” op prepza. Log in met {email} om te beginnen.",
        "heading": "Uitnodiging voor een gesprek",
        "lines": [
            "{company} nodigt je uit voor het gesprek “{title}” op prepza.",
            (
                "Log in met {email} om te beginnen. Alleen dit adres kan het gesprek "
                "doen, en je hebt één poging."
            ),
        ],
        "button": "Uitnodiging openen",
    },
    "footer": "Deze e-mail is naar {email} gestuurd omdat iemand dit adres op prepza heeft "
    "uitgenodigd. Verwachtte je hem niet, dan kun je hem negeren.",
    "paste_link": "Of plak deze link in je browser",
}
