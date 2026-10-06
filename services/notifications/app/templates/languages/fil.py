# Email texts in Filipino. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
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
    "reminder": {
        "subject": "Paalala: hinihintay ng {company} ang iyong interview",
        "preheader": "Bukas pa ang “{title}”. Mag-sign in gamit ang {email} para magsimula.",
        "heading": "Naghihintay ang iyong interview",
        "lines": [
            (
                "Inimbitahan ka ng {company} sa interview na “{title}” sa prepza ilang araw na "
                "ang nakalipas, at hindi mo pa ito nasisimulan."
            ),
            (
                "Mag-sign in gamit ang {email} para magsimula. Ang address na ito lang ang "
                "puwedeng sumagot sa interview, at may isang pagkakataon ka lang. Mag-e-expire "
                "ang imbitasyon 30 araw matapos itong ipadala."
            ),
        ],
        "button": "Buksan ang imbitasyon",
    },
    "report": {
        "subject": "Report ng kandidato: {candidate}",
        "preheader": "Sinagutan ni {candidate} ang “{title}” sa {company}. Naka-attach ang report.",
        "heading": "Report ng kandidato",
        "lines": [
            "Ibinahagi ni {sender} mula sa {company} ang report ni {candidate} para sa interview na “{title}”.",
            (
                "Naka-attach ito bilang isang pahinang PDF: ang kabuuang grado, ang score sa "
                "bawat topic at ang ipinakita ng browser ng kandidato. Mag-reply sa email na ito "
                "para sumagot kay {sender}."
            ),
        ],
        "button": "Bisitahin ang prepza",
        "footer": "Ipinadala ang email na ito sa {email} dahil nag-share si {sender} ng report ng "
        "kandidato sa address na ito sa prepza. Kung hindi mo ito inaasahan, puwede mo itong "
        "balewalain.",
    },
    "candidates": {
        "subject": "Report ng lahat ng kandidato: {title}",
        "preheader": "Lahat ng kandidato para sa “{title}” sa {company}. Naka-attach ang report.",
        "heading": "Report ng mga kandidato",
        "lines": [
            "Ibinahagi ni {sender} mula sa {company} ang report ng lahat ng kandidato para sa interview na “{title}”.",
            (
                "Naka-attach ito bilang PDF: ang grado, progreso at ipinakita ng browser ng bawat "
                "kandidato, simula sa pinakamahusay. Mag-reply sa email na ito para sumagot kay "
                "{sender}."
            ),
        ],
        "button": "Bisitahin ang prepza",
        "footer": "Ipinadala ang email na ito sa {email} dahil nag-share si {sender} ng report ng "
        "mga kandidato sa address na ito sa prepza. Kung hindi mo ito inaasahan, puwede mo itong "
        "balewalain.",
    },
    "footer": "Ipinadala ang email na ito sa {email} dahil may nag-imbita sa address na ito sa "
    "prepza. Kung hindi mo ito inaasahan, puwede mo itong balewalain.",
    "paste_link": "O i-paste ang link na ito sa iyong browser",
}
