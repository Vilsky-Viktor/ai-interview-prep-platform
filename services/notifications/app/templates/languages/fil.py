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
        "subject": "Report ng aplikante: {candidate}",
        "preheader": "Sinagutan ni {candidate} ang “{title}” sa {company}. Naka-attach ang report.",
        "heading": "Report ng aplikante",
        "lines": [
            "Ibinahagi ni {sender} mula sa {company} ang report ni {candidate} para sa interview na “{title}”.",
            (
                "Naka-attach ito bilang isang pahinang PDF: ang kabuuang grade, ang score sa "
                "bawat topic at ang ipinakita ng browser ng aplikante. Mag-reply sa email na ito "
                "para sumagot kay {sender}."
            ),
        ],
        "button": "Bisitahin ang prepza",
        "footer": "Ipinadala ang email na ito sa {email} dahil nag-share si {sender} ng report ng "
        "aplikante sa address na ito sa prepza. Kung hindi mo ito inaasahan, puwede mo itong "
        "balewalain.",
    },
    "candidates": {
        "subject": "Report ng lahat ng aplikante: {title}",
        "preheader": "Lahat ng aplikante para sa “{title}” sa {company}. Naka-attach ang report.",
        "heading": "Report ng mga aplikante",
        "lines": [
            "Ibinahagi ni {sender} mula sa {company} ang report ng lahat ng aplikante para sa interview na “{title}”.",
            (
                "Naka-attach ito bilang PDF: ang grade, progreso at ipinakita ng browser ng bawat "
                "aplikante, simula sa pinakamahusay. Mag-reply sa email na ito para sumagot kay "
                "{sender}."
            ),
        ],
        "button": "Bisitahin ang prepza",
        "footer": "Ipinadala ang email na ito sa {email} dahil nag-share si {sender} ng report ng "
        "mga aplikante sa address na ito sa prepza. Kung hindi mo ito inaasahan, puwede mo itong "
        "balewalain.",
    },
    "footer": "Ipinadala ang email na ito sa {email} dahil may nag-imbita sa address na ito sa "
    "prepza. Kung hindi mo ito inaasahan, puwede mo itong balewalain.",
    "paste_link": "O i-paste ang link na ito sa iyong browser",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Mag-unsubscribe",
    "email_settings": "Baguhin ang iyong mga setting sa email",
    "stop_reminders": "Huwag na akong padalhan ng paalala para sa interview na ito",
    "stop_company": "Huwag na akong padalhan ng email para sa {company}",
}
