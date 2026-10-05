# Email texts in English. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
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
    "reminder": {
        "subject": "Reminder: {company} is waiting for your interview",
        "preheader": "“{title}” is still open. Sign in with {email} to start.",
        "heading": "Your interview is waiting",
        "lines": [
            (
                "{company} invited you to the “{title}” interview on prepza a few days ago, and "
                "you haven't started it yet."
            ),
            (
                "Sign in with {email} to start. Only this address can take the interview, and "
                "you get one attempt. The invite expires 30 days after it was sent."
            ),
        ],
        "button": "Open the invite",
    },
    "report": {
        "subject": "{sender} shared a candidate report: {candidate}",
        "preheader": "{candidate} took “{title}” at {company}. The report is attached.",
        "heading": "Candidate report",
        "lines": [
            "{sender} from {company} shared the report of {candidate} for the “{title}” interview.",
            (
                "It's attached as a one-page PDF: the overall grade, each topic's score and "
                "what the candidate's browser showed. Reply to this email to answer {sender}."
            ),
        ],
        "button": "Visit prepza",
        "footer": "This email was sent to {email} because {sender} shared a candidate report "
        "with this address on prepza. If you weren't expecting it, you can ignore it.",
    },
    "candidates": {
        "subject": "{sender} shared a report of all candidates: {title}",
        "preheader": "Every candidate for “{title}” at {company}. The report is attached.",
        "heading": "Candidates report",
        "lines": [
            "{sender} from {company} shared the report of all candidates for the “{title}” interview.",
            (
                "It's attached as a PDF: each candidate's grade, progress and what their browser "
                "showed, best first. Reply to this email to answer {sender}."
            ),
        ],
        "button": "Visit prepza",
        "footer": "This email was sent to {email} because {sender} shared a candidates report "
        "with this address on prepza. If you weren't expecting it, you can ignore it.",
    },
    "footer": "This email was sent to {email} because someone invited this address on prepza. If "
    "you weren't expecting it, you can ignore it.",
    "paste_link": "Or paste this link into your browser",
}
