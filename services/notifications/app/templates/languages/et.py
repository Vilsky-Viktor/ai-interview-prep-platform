# Email texts in Estonian. Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = (
    "See e-kiri saadeti aadressile {email}, sest oled prepzas ettevõtte omanik või administraator."
)

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
    "digest": {
        "subject": "Sinu tegevuste kokkuvõte prepzas",
        "preheader": "Mis sinu ettevõtetes viimase 24 tunni jooksul juhtus.",
        "heading": "Sinu tegevuste kokkuvõte",
        "lines": [
            "Siin on, mis sinu ettevõtetes prepzas viimase 24 tunni jooksul juhtus.",
        ],
        "rows": {
            "candidate_finished": "Lõpetanud kandidaadid: {count} · „{title}“",
            "invite_undelivered": "Kohale jõudmata kutsed: {count} · „{title}“",
            "ats_not_invited": "Kutsumata ATS-i kandidaadid: {count}",
            "interview_ready": "Valmis intervjuu: „{title}“",
        },
        "button": "Ava prepza",
        "footer": (
            "See e-kiri saadeti aadressile {email}, sest kuulud prepzas ettevõttesse ja "
            "saad selle tegevuste kokkuvõtet."
        ),
    },
    "low_credits": {
        "subject": "Sinu krediidid hakkavad otsa saama",
        "preheader": "Laadi juurde, et kandidaate edasi kutsuda.",
        "heading": "Krediidid hakkavad otsa saama",
        "lines": [
            (
                "Nendel ettevõtetel pole piisavalt krediiti, et veel üht kandidaati "
                "kutsuda. Laadi juurde, et kandidaate edasi kutsuda."
            ),
        ],
        "rows": {
            "company": "{company} · saadaval krediiti: {available}",
        },
        "button": "Laadi juurde",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "Ootab kandidaate",
        "preheader": "Kutsu kandidaadid e-postiga või jaga intervjuu linki.",
        "heading": "Ootab kandidaate",
        "lines": [
            (
                "Need intervjuud on juba mõni päev valmis, kuid kedagi pole veel kutsutud. "
                "Kutsu kandidaadid e-postiga või jaga intervjuu linki."
            ),
        ],
        "rows": {
            "interview": "„{title}“ · {company}",
        },
        "button": "Kutsu kandidaadid",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "Sinu teemad ootavad ülevaatamist",
        "preheader": "Kinnita teemad ja küsimused luuakse.",
        "heading": "Vaata oma teemad üle",
        "lines": [
            (
                "Sinu alustatud intervjuude teemad ootavad ülevaatamist. Kui need kinnitad,"
                " luuakse küsimused. Ülevaatus, mis jääb 14 päevaks avatuks, tühistatakse."
            ),
        ],
        "rows": {
            "interview": "{company} · ootepäevi: {days}",
        },
        "button": "Vaata teemad üle",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "Automaatne juurdelaadimine ebaõnnestus: {company}",
        "preheader": "Kaardilt ei saanud makset võtta. Laadi juurde, et kandidaate edasi kutsuda.",
        "heading": "Automaatne juurdelaadimine ebaõnnestus",
        "lines": [
            (
                "Automaatne juurdelaadimine ei saanud ettevõtte {company} kaardilt makset "
                "võtta, seega krediiti ei lisatud."
            ),
            (
                "Laadi juurde, et kandidaate edasi kutsuda. Automaatne juurdelaadimine "
                "proovib kaarti hiljem uuesti."
            ),
        ],
        "button": "Laadi juurde",
        "footer": (
            "See e-kiri saadeti aadressile {email}, sest oled prepzas ettevõtte {company} "
            "omanik või administraator. See puudutab sinu ettevõtte arveldust, seega "
            "saadetakse see sõltumata sinu e-kirjade seadetest."
        ),
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
