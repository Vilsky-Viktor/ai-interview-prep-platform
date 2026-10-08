# Email texts in Estonian. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "candidate": {
        "subject": "{company} kutsub sind intervjuule",
        "preheader": "Tee prepzas intervjuu „{title}“. Alustamiseks logi sisse aadressiga {email}.",
        "heading": "Kutse intervjuule",
        "lines": [
            "{company} kutsub sind prepzas intervjuule „{title}“.",
            (
                "Alustamiseks logi sisse aadressiga {email}. Intervjuud saab teha "
                "ainult see aadress ja sul on üks katse."
            ),
        ],
        "button": "Ava kutse",
    },
    "reminder": {
        "subject": "Meeldetuletus: {company} ootab sinu intervjuud",
        "preheader": "„{title}“ on endiselt avatud. Alustamiseks logi sisse aadressiga {email}.",
        "heading": "Sinu intervjuu ootab",
        "lines": [
            (
                "{company} kutsus sind mõni päev tagasi prepzas intervjuule „{title}“, "
                "kuid sa pole seda veel alustanud."
            ),
            (
                "Alustamiseks logi sisse aadressiga {email}. Intervjuud saab teha ainult see "
                "aadress ja sul on üks katse. Kutse aegub 30 päeva pärast saatmist."
            ),
        ],
        "button": "Ava kutse",
    },
    "report": {
        "subject": "Kandidaadi aruanne: {candidate}",
        "preheader": "{candidate} tegi ettevõttes {company} intervjuu „{title}“. Aruanne on manuses.",
        "heading": "Kandidaadi aruanne",
        "lines": [
            "{sender} ettevõttest {company} jagas kandidaadi {candidate} aruannet intervjuu „{title}“ kohta.",
            (
                "See on manuses üheleheküljelise PDF-ina: üldhinne, iga teema tulemus ja see, "
                "mida kandidaadi brauser näitas. Kasutajale {sender} vastamiseks vasta sellele "
                "e-kirjale."
            ),
        ],
        "button": "Külasta prepzat",
        "footer": "See e-kiri saadeti aadressile {email}, sest {sender} jagas prepzas selle "
        "aadressiga kandidaadi aruannet. Kui sa seda ei oodanud, võid selle tähelepanuta jätta.",
    },
    "candidates": {
        "subject": "Kõigi kandidaatide aruanne: {title}",
        "preheader": "Kõik intervjuu „{title}“ kandidaadid ettevõttes {company}. Aruanne on manuses.",
        "heading": "Kandidaatide aruanne",
        "lines": [
            "{sender} ettevõttest {company} jagas intervjuu „{title}“ kõigi kandidaatide aruannet.",
            (
                "See on manuses PDF-ina: iga kandidaadi hinne, edenemine ja see, mida tema "
                "brauser näitas, parimad eespool. Kasutajale {sender} vastamiseks vasta sellele "
                "e-kirjale."
            ),
        ],
        "button": "Külasta prepzat",
        "footer": "See e-kiri saadeti aadressile {email}, sest {sender} jagas prepzas selle "
        "aadressiga kandidaatide aruannet. Kui sa seda ei oodanud, võid selle tähelepanuta jätta.",
    },
    "footer": "See e-kiri saadeti aadressile {email}, sest keegi kutsus selle aadressi "
    "prepzasse. Kui sa seda ei oodanud, võid selle tähelepanuta jätta.",
    "paste_link": "Või kleebi see link oma brauserisse",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Loobu tellimusest",
    "email_settings": "Muuda oma e-kirjade seadeid",
    "stop_reminders": "Ära saada mulle selle intervjuu meeldetuletusi",
    "stop_company": "Ära saada mulle e-kirju ettevõttelt {company}",
}
