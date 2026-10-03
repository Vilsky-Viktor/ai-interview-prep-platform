# The text of each email, in each language an interview or kit can be in. Every value is filled
# in with str.format; the HTML version escapes them. Russian avoids past-tense verbs, which would
# need the inviter's gender.

SHARE_INVITE = {
    "en": {
        "subject": "{inviter} shared “{title}” with you",
        "preheader": "Sign in with {email} to start preparing.",
        "heading": "A preparation for you",
        "lines": [
            "{inviter} invited you to prepare with “{title}” on prepza.",
            "Sign in with {email} to join. Only this address can accept the invite.",
        ],
        "button": "Open the invite",
    },
    "ru": {
        "subject": "{inviter} приглашает вас в «{title}»",
        "preheader": "Войдите с адресом {email}, чтобы начать подготовку.",
        "heading": "Подготовка для вас",
        "lines": [
            "{inviter} приглашает вас готовиться с «{title}» на prepza.",
            (
                "Войдите с адресом {email}, чтобы присоединиться. Принять приглашение можно только "
                "с этого адреса."
            ),
        ],
        "button": "Открыть приглашение",
    },
}

CANDIDATE_INVITE = {
    "en": {
        "subject": "{company} invited you to an interview",
        "preheader": "Take “{title}” on prepza. Sign in with {email} to start.",
        "heading": "Interview invitation",
        "lines": [
            "{company} invited you to the “{title}” interview on prepza.",
            (
                "Sign in with {email} to start. Only this address can take the interview, "
                "and you get one attempt."
            ),
        ],
        "button": "Open the invite",
    },
    "ru": {
        "subject": "{company} приглашает вас на собеседование",
        "preheader": "Пройдите «{title}» на prepza. Войдите с адресом {email}, чтобы начать.",
        "heading": "Приглашение на собеседование",
        "lines": [
            "{company} приглашает вас на собеседование «{title}» на prepza.",
            (
                "Войдите с адресом {email}, чтобы начать. Пройти собеседование можно только с этого "
                "адреса и только один раз."
            ),
        ],
        "button": "Открыть приглашение",
    },
}

FOOTER = {
    "en": (
        "This email was sent to {email} because someone invited this address on prepza. "
        "If you weren't expecting it, you can ignore it."
    ),
    "ru": (
        "Это письмо отправлено на {email}, потому что этот адрес пригласили на prepza. "
        "Если вы его не ждали, просто проигнорируйте его."
    ),
}

# Under the button, for clients that don't show it.
PASTE_LINK = {
    "en": "Or paste this link into your browser",
    "ru": "Или вставьте эту ссылку в браузер",
}
