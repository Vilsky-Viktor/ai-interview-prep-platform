# Email texts in English. Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = (
    "This email was sent to {email} because you're an owner or admin of a company on prepza."
)

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
        "subject": "Candidate report: {candidate}",
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
        "subject": "Report of all candidates: {title}",
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
    "digest": {
        "subject": "Your activity digest on prepza",
        "preheader": "What happened in your companies in the last 24 hours.",
        "heading": "Your activity digest",
        "lines": [
            "Here's what happened in your companies on prepza in the last 24 hours.",
        ],
        "rows": {
            "candidate_finished": "Candidates who finished: {count} · “{title}”",
            "invite_undelivered": "Undelivered invites: {count} · “{title}”",
            "ats_not_invited": "ATS candidates not invited: {count}",
            "interview_ready": "Interview ready: “{title}”",
        },
        "button": "Open prepza",
        "footer": (
            "This email was sent to {email} because you're a member of a company on prepza "
            "and get its activity digest."
        ),
    },
    "low_credits": {
        "subject": "Your credits are running low",
        "preheader": "Top up to keep inviting candidates.",
        "heading": "Credits are running low",
        "lines": [
            (
                "These companies don't have enough credits to invite another candidate. Top"
                " up to keep inviting candidates."
            ),
        ],
        "rows": {
            "company": "{company} · credits available: {available}",
        },
        "button": "Top up",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "Waiting for candidates",
        "preheader": "Invite candidates by email, or share the interview's link.",
        "heading": "Waiting for candidates",
        "lines": [
            (
                "These interviews have been ready for a few days, but nobody has been "
                "invited yet. Invite candidates by email, or share the interview's link."
            ),
        ],
        "rows": {
            "interview": "“{title}” · {company}",
        },
        "button": "Invite candidates",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "Your topics are waiting for review",
        "preheader": "Confirm the topics, and the questions get generated.",
        "heading": "Review your topics",
        "lines": [
            (
                "The topics of the interviews you started are waiting for your review. Once"
                " you confirm them, the questions are generated. A review left open for 14 "
                "days is cancelled."
            ),
        ],
        "rows": {
            "interview": "{company} · days waiting: {days}",
        },
        "button": "Review your topics",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "Automatic top-up failed for {company}",
        "preheader": "The card couldn't be charged. Top up to keep inviting candidates.",
        "heading": "Automatic top-up failed",
        "lines": [
            "Automatic top-up couldn't charge the card for {company}, so no credits were added.",
            "Top up to keep inviting candidates. Automatic top-up will try the card again later.",
        ],
        "button": "Top up",
        "footer": (
            "This email was sent to {email} because you're an owner or admin of {company} "
            "on prepza. It's about your company's billing, so it's sent whatever your email"
            " settings."
        ),
    },
    "footer": "This email was sent to {email} because someone invited this address on prepza. If "
    "you weren't expecting it, you can ignore it.",
    "paste_link": "Or paste this link into your browser",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Unsubscribe",
    "email_settings": "Change your email settings",
    "stop_reminders": "Don't send me reminders for this interview",
    "stop_company": "Don't email me for {company}",
}
