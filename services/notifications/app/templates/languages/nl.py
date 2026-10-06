# Email texts in Dutch. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
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
    "reminder": {
        "subject": "Herinnering: {company} wacht op je sollicitatiegesprek",
        "preheader": "“{title}” staat nog open. Log in met {email} om te beginnen.",
        "heading": "Je gesprek wacht op je",
        "lines": [
            (
                "{company} heeft je een paar dagen geleden uitgenodigd voor het gesprek “{title}” "
                "op prepza, en je bent nog niet begonnen."
            ),
            (
                "Log in met {email} om te beginnen. Alleen dit adres kan het gesprek doen, en je "
                "hebt één poging. De uitnodiging verloopt 30 dagen na verzending."
            ),
        ],
        "button": "Uitnodiging openen",
    },
    "report": {
        "subject": "Kandidaatrapport: {candidate}",
        "preheader": "{candidate} deed “{title}” bij {company}. Het rapport zit in de bijlage.",
        "heading": "Kandidaatrapport",
        "lines": [
            "{sender} van {company} heeft het rapport van {candidate} voor het sollicitatiegesprek “{title}” gedeeld.",
            (
                "Het zit als PDF van één pagina in de bijlage: het totaalcijfer, de score per "
                "onderwerp en wat de browser van de kandidaat liet zien. Beantwoord deze e-mail om "
                "{sender} te antwoorden."
            ),
        ],
        "button": "Naar prepza",
        "footer": "Deze e-mail is naar {email} gestuurd omdat {sender} op prepza een "
        "kandidaatrapport met dit adres heeft gedeeld. Verwachtte je hem niet, dan kun je hem "
        "negeren.",
    },
    "candidates": {
        "subject": "Rapport van alle kandidaten: {title}",
        "preheader": "Alle kandidaten voor “{title}” bij {company}. Het rapport zit in de bijlage.",
        "heading": "Kandidatenrapport",
        "lines": [
            "{sender} van {company} heeft het rapport van alle kandidaten voor het sollicitatiegesprek “{title}” gedeeld.",
            (
                "Het zit als PDF in de bijlage: het cijfer, de voortgang en wat de browser van elke "
                "kandidaat liet zien, beste eerst. Beantwoord deze e-mail om {sender} te antwoorden."
            ),
        ],
        "button": "Naar prepza",
        "footer": "Deze e-mail is naar {email} gestuurd omdat {sender} op prepza een "
        "kandidatenrapport met dit adres heeft gedeeld. Verwachtte je hem niet, dan kun je hem "
        "negeren.",
    },
    "footer": "Deze e-mail is naar {email} gestuurd omdat iemand dit adres op prepza heeft "
    "uitgenodigd. Verwachtte je hem niet, dan kun je hem negeren.",
    "paste_link": "Of plak deze link in je browser",
}
