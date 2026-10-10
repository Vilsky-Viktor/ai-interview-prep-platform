# Email texts in Filipino. Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = (
    "Ipinadala ang email na ito sa {email} dahil ikaw ay may-ari o admin ng isang kumpanya "
    "sa prepza."
)

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
    "member": {
        "subject": "Iniimbitahan ka ni {inviter} na sumali sa team ng {company} sa prepza",
        "preheader": (
            "Sumali sa team ng {company} bilang {role}. Mag-sign in gamit ang {email} para "
            "tanggapin."
        ),
        "heading": "Imbitasyon sa team",
        "lines": [
            "Iniimbitahan ka ni {inviter} na sumali sa team ng {company} sa prepza bilang {role}.",
            (
                "Mag-sign in gamit ang {email} para tanggapin ito. Ang address na ito lang ang "
                "puwedeng tumanggap sa imbitasyon."
            ),
        ],
        "button": "Buksan ang imbitasyon",
        # The role's name as the lines use it.
        "roles": {"admin": "admin", "viewer": "viewer"},
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
    "digest": {
        "subject": "Ang iyong buod ng aktibidad sa prepza",
        "preheader": "Ang nangyari sa mga kumpanya mo sa nakalipas na 24 oras.",
        "heading": "Ang iyong buod ng aktibidad",
        "lines": [
            "Narito ang nangyari sa mga kumpanya mo sa prepza sa nakalipas na 24 oras.",
        ],
        "rows": {
            "candidate_finished": "Mga aplikanteng nakatapos: {count} · “{title}”",
            "invite_undelivered": "Mga imbitasyong hindi naihatid: {count} · “{title}”",
            "ats_not_invited": "Mga aplikante mula sa ATS na hindi na-imbitahan: {count}",
            "interview_ready": "Handa na ang interview: “{title}”",
        },
        "button": "Buksan ang prepza",
        "footer": (
            "Ipinadala ang email na ito sa {email} dahil miyembro ka ng isang kumpanya sa "
            "prepza at natatanggap mo ang buod ng aktibidad nito."
        ),
    },
    "low_credits": {
        "subject": "Paubos na ang iyong mga credit",
        "preheader": "Mag-top up para patuloy na makapag-imbita ng aplikante.",
        "heading": "Paubos na ang mga credit",
        "lines": [
            (
                "Kulang na ang credits ng mga kumpanyang ito para mag-imbita ng isa pang "
                "aplikante. Mag-top up para patuloy na makapag-imbita ng aplikante."
            ),
        ],
        "rows": {
            "company": "{company} · available na credits: {available}",
        },
        "button": "Mag-top up",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "Naghihintay ng mga aplikante",
        "preheader": "Mag-imbita ng mga aplikante sa email o ibahagi ang link ng interview.",
        "heading": "Naghihintay ng mga aplikante",
        "lines": [
            (
                "Ilang araw nang handa ang mga interview na ito, pero wala pang "
                "naiimbitahan. Mag-imbita ng mga aplikante sa email o ibahagi ang link ng "
                "interview."
            ),
        ],
        "rows": {
            "interview": "“{title}” · {company}",
        },
        "button": "Mag-imbita ng mga aplikante",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "Naghihintay ng review ang iyong mga topic",
        "preheader": "Kumpirmahin ang mga topic, at gagawin na ang mga tanong.",
        "heading": "I-review ang iyong mga topic",
        "lines": [
            (
                "Naghihintay ng iyong review ang mga topic ng mga interview na sinimulan "
                "mo. Kapag kinumpirma mo ang mga ito, gagawin na ang mga tanong. "
                "Kinakansela ang review na nakabukas nang 14 na araw."
            ),
        ],
        "rows": {
            "interview": "{company} · araw na naghihintay: {days}",
        },
        "button": "I-review ang mga topic",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "Pumalya ang awtomatikong top-up para sa {company}",
        "preheader": (
            "Hindi ma-charge ang card. Mag-top up para patuloy na makapag-imbita ng aplikante."
        ),
        "heading": "Pumalya ang awtomatikong top-up",
        "lines": [
            (
                "Hindi ma-charge ng awtomatikong top-up ang card para sa {company}, kaya "
                "walang naidagdag na credits."
            ),
            (
                "Mag-top up para patuloy na makapag-imbita ng aplikante. Susubukan ulit ng "
                "awtomatikong top-up ang card mamaya."
            ),
        ],
        "button": "Mag-top up",
        "footer": (
            "Ipinadala ang email na ito sa {email} dahil ikaw ay may-ari o admin ng "
            "{company} sa prepza. Tungkol ito sa billing ng kumpanya mo, kaya ipinapadala "
            "ito anuman ang iyong email settings."
        ),
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
