# Email texts in Filipino. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "Iniimbitahan ka ni {inviter} sa “{title}”",
        "preheader": "Mag-sign in gamit ang {email} para magsimulang maghanda.",
        "heading": "Isang paghahanda para sa iyo",
        "lines": [
            "Iniimbitahan ka ni {inviter} na maghanda gamit ang “{title}” sa prepza.",
            (
                "Mag-sign in gamit ang {email} para sumali. Ang address na ito lang ang "
                "puwedeng tumanggap ng imbitasyon."
            ),
        ],
        "button": "Buksan ang imbitasyon",
    },
    "candidate": {
        "subject": "Iniimbitahan ka ng {company} sa isang interview",
        "preheader": "Sagutan ang “{title}” sa prepza. Mag-sign in gamit ang {email} "
        "para magsimula.",
        "heading": "Imbitasyon sa interview",
        "lines": [
            "Iniimbitahan ka ng {company} sa interview na “{title}” sa prepza.",
            (
                "Mag-sign in gamit ang {email} para magsimula. Ang address na ito "
                "lang ang puwedeng sumagot sa interview, at may isang pagkakataon ka "
                "lang."
            ),
        ],
        "button": "Buksan ang imbitasyon",
    },
    "footer": "Ipinadala ang email na ito sa {email} dahil may nag-imbita sa address na ito sa "
    "prepza. Kung hindi mo ito inaasahan, puwede mo itong balewalain.",
    "paste_link": "O i-paste ang link na ito sa iyong browser",
}
