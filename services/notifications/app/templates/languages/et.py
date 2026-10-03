# Email texts in Estonian. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} kutsub sind komplekti „{title}”",
        "preheader": "Valmistumise alustamiseks logi sisse aadressiga {email}.",
        "heading": "Ettevalmistus sulle",
        "lines": [
            "{inviter} kutsub sind valmistuma komplektiga „{title}” prepzas.",
            (
                "Liitumiseks logi sisse aadressiga {email}. Kutset saab vastu võtta "
                "ainult see aadress."
            ),
        ],
        "button": "Ava kutse",
    },
    "candidate": {
        "subject": "{company} kutsub sind intervjuule",
        "preheader": "Tee prepzas intervjuu „{title}”. Alustamiseks logi sisse aadressiga {email}.",
        "heading": "Kutse intervjuule",
        "lines": [
            "{company} kutsub sind prepzas intervjuule „{title}”.",
            (
                "Alustamiseks logi sisse aadressiga {email}. Intervjuud saab teha "
                "ainult see aadress ja sul on üks katse."
            ),
        ],
        "button": "Ava kutse",
    },
    "footer": "See e-kiri saadeti aadressile {email}, sest keegi kutsus selle aadressi "
    "prepzasse. Kui sa seda ei oodanud, võid selle tähelepanuta jätta.",
    "paste_link": "Või kleebi see link oma brauserisse",
}
