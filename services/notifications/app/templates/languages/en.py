# Email texts in English. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} shared “{title}” with you",
        "preheader": "Sign in with {email} to start preparing.",
        "heading": "A preparation for you",
        "lines": [
            "{inviter} invited you to prepare with “{title}” on prepza.",
            "Sign in with {email} to join. Only this address can accept the invite.",
        ],
        "button": "Open the invite",
    },
    "candidate": {
        "subject": "{company} invited you to an interview",
        "preheader": "Take “{title}” on prepza. Sign in with {email} to start.",
        "heading": "Interview invitation",
        "lines": [
            "{company} invited you to the “{title}” interview on prepza.",
            (
                "Sign in with {email} to start. Only this address can take the "
                "interview, and you get one attempt."
            ),
        ],
        "button": "Open the invite",
    },
    "footer": "This email was sent to {email} because someone invited this address on prepza. If "
    "you weren't expecting it, you can ignore it.",
    "paste_link": "Or paste this link into your browser",
}
