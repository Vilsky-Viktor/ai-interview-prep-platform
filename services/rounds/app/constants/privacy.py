from app.constants.legal import COMPANY

# The privacy policy, in English only: it's a legal text, and a translation would need its own
# legal review. The FAQ page's chat answers from it too.
PRIVACY_INTRO = f"This policy explains what personal data prepza collects, why, how long we keep it, and the rights you have. prepza is run by {COMPANY['name']} (registry code {COMPANY['registry_code']}), {COMPANY['address']}."

PRIVACY_SECTIONS = [
    {
        "heading": "Who is responsible",
        "paragraphs": [
            f"For your own account and your company's account, {COMPANY['name']} is the controller of your data. Write to {COMPANY['email']} with any question or request.",
            "When a company invites you to an interview on prepza, that company decides why and how your results are used and is the controller of them; we process them on its behalf. You can contact the company directly, or us, and we will pass your request on.",
        ],
    },
    {
        "heading": "What we collect",
        "items": [
            "Account: your name, email address, profile photo and account id, from the Google, LinkedIn or GitHub account you sign in with, and which of them are linked to your account.",
            "What you give us: job descriptions you paste and the interviews made from them, the emails of the candidates you invite and of the people you send a report to, and your ratings and reports of questions. Questions you ask the help chat on the FAQ page are used only to answer them and aren't stored.",
            "Companies: the company's name, logo and website, and the email domain it was verified with.",
            "Practice: if you take free practice interviews, your answers, grades and how long each answer took. Only you see them.",
            "Contact messages: the name, email address and message you send through the contact page.",
            "Interviews, if a company invites you: the email you were invited with, your answers, how long each answer took, when you left the interview page, copied text or answered too fast to have read the question, any extra time the company gave you (no reason is recorded), and your ratings and reports of questions. You are told about this before you start.",
            "Technical: error reports without your IP address or email, and short-lived server logs needed to run and secure the service.",
            "Tools a company connects: the keys or tokens its owner or admin creates in its applicant tracking system (Workable, Greenhouse, Teamtailor, Recruitee or Breezy HR) or Slack, stored encrypted; a one-way hash of each prepza API key and the addresses of its web hooks; and, from its applicant tracking system, the email and id of each candidate it sends to prepza.",
            "Referrals: whose referral link you or your company came through, and whether it has been rewarded.",
            "Usage statistics: steps such as signing up, a company being created, a candidate invited or a top-up, with counts like a score or an amount. Your account id is replaced by a code that can't be traced back to you, and no names, emails or texts are included.",
        ],
    },
    {
        "heading": "Why we use it",
        "items": [
            "To provide prepza: generating interviews, running them for invited candidates, showing companies the results and sending the emails you ask for (contract).",
            "To keep prepza secure and working: preventing abuse, rate limits, error reports, and statistics that improve question quality (our legitimate interest).",
            "Usage statistics show which parts of prepza help people and which prices and limits work, so we can improve them (our legitimate interest).",
            "Showing a company as verified, by checking its website against the email domains of its owners and admins (our legitimate interest).",
            "Interview results, timings and integrity signals help the hiring company assess your answers fairly (the company's legitimate interest). People at the company make the hiring decision; prepza makes no decision about you on its own. You can ask the company for a person to review your result, and for an accommodation such as extra time before you start.",
        ],
    },
    {
        "heading": "Who we share it with",
        "paragraphs": [
            "We share data with the service providers that run prepza for us, under agreements that protect it:",
        ],
        "items": [
            "Google (Firebase Authentication): sign-in. LinkedIn and GitHub only confirm who you are when you sign in with them; we don't receive anything else from them.",
            "OpenAI: writing questions and help chat answers from the text you provide, and checking reported questions (only the reasons given, never the comments). Under OpenAI's API terms, this data is not used to train their models.",
            "Resend: sending invite, reminder and report emails and contact messages.",
            "Sentry: error reports, with emails removed.",
            "Google Cloud, our hosting provider, which stores the data.",
            "Upstash: short-lived counters for rate limits and live updates.",
            "Paddle: payments and taxes, as the reseller.",
        ],
    },
    {
        "heading": "Tools a company connects",
        "paragraphs": [
            "A company can connect its own tools to prepza, and then we send them data on its instruction, as part of the service it asked for: its applicant tracking system (Workable, Greenhouse, Teamtailor, Recruitee or Breezy HR) receives your grade, whether it reached the passing grade, the integrity signals and a link to your results; a Slack channel it chose receives its notifications, such as that you finished and your grade; and its own systems, through prepza's API or web hooks, receive your email, progress, grade and integrity signals. The company chooses and controls these tools, which may be outside the EU, and is responsible for how they use your data.",
        ],
    },
    {
        "heading": "Transfers outside the EU",
        "paragraphs": [
            "Some of these providers are in the United States. Transfers are covered by the EU-US Data Privacy Framework or the European Commission's standard contractual clauses.",
        ],
    },
    {
        "heading": "How long we keep it",
        "items": [
            "Your account and everything in it: until you delete your account.",
            "Interview results, timings and integrity signals: 12 months after the invitation was last sent, then deleted automatically.",
            "Candidates an applicant tracking system sends: their email and id there, 12 months after they arrive.",
            "Notifications in the app, such as that a candidate finished: 90 days.",
            "The record of a company's decisions, such as removing a candidate: 24 months.",
            "Practice rounds: until you delete your account.",
            "A report emailed from prepza: the PDF is kept only to send the email, and deleted at most 7 days later.",
            "Pasted job descriptions in our generation records: 90 days after the generation finishes. The interview made from them stays in the company's account until it's deleted.",
            "Contact messages: as long as we need them to answer you, at most 2 years.",
            "Error reports: up to 90 days.",
            "Database backups: 14 days, then overwritten; anything deleted is gone from them by then.",
            "Usage statistics: 25 months, then deleted automatically.",
            "Purchase records: as long as accounting law requires (7 years in Estonia), without your account id once you delete your account.",
            "A one-way hash of your email after you delete your account, only so that signing up again doesn't repeat the welcome credits. It can't be turned back into your email.",
        ],
    },
    {
        "heading": "Your rights",
        "paragraphs": [
            'You can see, download and delete your data yourself: "Download my data" and "Delete account" are in Settings, in your account menu. You can also ask us to correct your data, to restrict or object to its use, or to move it to another service, at the address above.',
            "You can complain to the Estonian Data Protection Inspectorate (Andmekaitse Inspektsioon, www.aki.ee) or to the authority where you live.",
        ],
    },
    {
        "heading": "Cookies and storage",
        "paragraphs": [
            "prepza uses only what it needs to work: one cookie and the browser storage that keep you signed in, and a setting that remembers your light or dark theme. There are no advertising or analytics cookies, so there is nothing to consent to.",
        ],
    },
    {
        "heading": "Children",
        "paragraphs": [
            "prepza is not meant for anyone under 16.",
        ],
    },
    {
        "heading": "Changes",
        "paragraphs": [
            "We will update this page when our practices change and tell you about significant changes by email or in the app.",
        ],
    },
    {
        "heading": "Contact us",
        "paragraphs": [
            f"Questions about this policy or your data: write to {COMPANY['email']}, or use the contact page linked at the bottom of every page.",
        ],
    },
]
