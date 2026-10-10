from app.constants.legal import COMPANY

# The privacy policy, in English only: it's a legal text, and a translation would need its own
# legal review. The help chat (the signed-out assistant) answers from it too.
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
            "What you give us: job descriptions you paste and the interviews made from them, the emails of the candidates you invite (and their names, if you give them or correct them) and of the people you send a report to, and your ratings and reports of questions.",
            "The assistant: when you're signed in, what you write or say to it (a voice message is turned into text and never stored) and its answers, so you can come back to a chat. It doesn't keep what it read to answer you, such as candidates' results: when you open a chat again, it fetches them again with your current access. If you aren't signed in, your questions are used only to answer them and aren't stored. A message that contains a key, token or password is removed at once: it isn't stored or sent on.",
            "Companies: the company's name, logo and website, and the email domain it was verified with.",
            "Practice: if you take free practice interviews, your answers, grades and how long each answer took. Only you see them.",
            "Contact messages: the name, email address and message you send through the contact page.",
            "Interviews, if a company invites you: the email you were invited with, your answers, how long each answer took, when you left the interview page, copied text or answered too fast to have read the question, any extra time the company gave you (no reason is recorded), and your ratings and reports of questions. You are told about this before you start.",
            "Technical: error reports without your IP address or email, and short-lived server logs needed to run and secure the service.",
            "AI apps you connect: the app's name and the site it returns to, and when you connected it and last used it. Its access is kept only as a one-way hash.",
            "Tools a company connects: the keys or tokens its owner or admin creates in its applicant tracking system (Workable, Greenhouse, Teamtailor, Recruitee or Breezy HR) or Slack, stored encrypted; a one-way hash of each prepza API key and the addresses of its web hooks; and, from its applicant tracking system, the email, name and id of each candidate it sends to prepza.",
            "Email settings: which optional emails you get, and a log of every change to them: which email, on or off, when, where (signing in, Settings, or an unsubscribe link or spam report) and which version of the checkboxes' wording you saw.",
            "Emails to company members: a record of the activity digests and reminders we sent you, and what each reminder was about, so none is sent twice.",
            "Candidates who stop a company's emails: a one-way hash of their email address, with the company and, if they stopped only an interview's reminders, that invite. It can't be turned back into the email.",
            "Referrals: whose referral link you or your company came through, and whether it has been rewarded.",
            "Usage statistics: steps such as signing up, a company being created, a candidate invited or a top-up, with counts like a score or an amount. Your account id is replaced by a code that can't be traced back to you, and no names, emails or texts are included.",
        ],
    },
    {
        "heading": "Why we use it",
        "items": [
            "To provide prepza: generating interviews, running them for invited candidates, showing companies the results and sending the emails you ask for (contract).",
            "Service emails, such as invites, reports, billing problems and changes to our terms, which are always sent (contract).",
            "The activity digest and reminders about your companies, such as low credits or an interview with no candidates (our legitimate interest in helping you use prepza). They are on until you turn them off.",
            "Product updates and news: for our own users who didn't tick \"Don't send me product updates and news\" the first time signing in offered it (article 13(2) of the ePrivacy Directive and § 103¹ of the Estonian Electronic Communications Act). You can stop them at any time, free of charge.",
            "Offers and promotions: only if you agree, by ticking the box when you sign in or in Settings (consent). You can withdraw it at any time.",
            "Remembering that a candidate stopped a company's emails, so prepza doesn't email them for that company again (respecting their objection).",
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
            "OpenAI: writing questions from the text you provide; the assistant's answers, from your questions and the data it reads with your access to answer them; turning voice messages into text; and checking reported questions (only the reasons given, never the comments). Under OpenAI's API terms, this data is not used to train their models.",
            "Resend: sending emails: invites and reminders to candidates, reports, emails to company members such as the activity digest, and contact messages.",
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
        "heading": "AI apps you connect",
        "paragraphs": [
            "You can connect an AI app of your own, such as Claude (by Anthropic) or ChatGPT (by OpenAI), to your prepza account. Only when you do, and only for what you ask it, it reads and changes your companies' data with your access, including candidates' results, and that data reaches the app's provider under the app's own terms and privacy policy, not ours. You choose these apps and can disconnect one at any time on a company's Integrations tab; deleting your account disconnects them all.",
        ],
    },
    {
        "heading": "Emails and unsubscribing",
        "paragraphs": [
            "Service emails, such as invites, reports, billing problems and changes to our terms, are always sent. You choose the others in Settings, under Emails: the activity digest, reminders, product updates and news, and offers and promotions. Every optional email has an unsubscribe link that works without signing in, and marking the activity digest or reminders as spam turns them off too.",
            "Invites and reminders a company sends to candidates through prepza have links to stop that company's emails, or that interview's reminders. prepza then doesn't email that address for the company again, and the company sees the invite as not delivered.",
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
            "Candidates an applicant tracking system sends: their email, name and id there, 12 months after they arrive.",
            "Notifications in the app, such as that a candidate finished: 90 days.",
            "AI apps you connect: until you disconnect them or delete your account; a connection unused for 90 days ends by itself.",
            "Your chats with the assistant: 90 days after their last message. You can delete a chat at any time, and they're deleted with your account or the company they're about.",
            "The record of a company's decisions, such as removing a candidate: 24 months.",
            "Practice rounds: until you delete your account.",
            "A report emailed from prepza: the PDF is kept only to send the email, and deleted at most 7 days later.",
            "Pasted job descriptions in our generation records: 90 days after the generation finishes. The interview made from them stays in the company's account until it's deleted.",
            "Your email settings and the log of their changes: until you delete your account.",
            "The record of digests and reminders sent to you: 30 days, or until you delete your account if that's sooner.",
            "A candidate's request to stop a company's emails, as a hash of their email: until the company is deleted, even if the company erases the candidate.",
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
