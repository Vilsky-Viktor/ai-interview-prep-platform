from app.constants.legal import COMPANY

# The data processing agreement (GDPR Article 28) between prepza and each company, in English
# only: it's a legal text, and a translation would need its own legal review. The terms make it
# part of every company's agreement. The FAQ page's chat answers from it too.
DPA_INTRO = f"This agreement applies when a company uses prepza to assess candidates. The company is the controller of its candidates' data and {COMPANY['name']} (registry code {COMPANY['registry_code']}), {COMPANY['address']}, processes it on the company's behalf. It forms part of the terms and is accepted with them; nothing needs to be signed."

DPA_SECTIONS = [
    {
        "heading": "What is processed",
        "items": [
            "Purpose: running the company's interviews: inviting candidates, timing and scoring their answers, showing the company the results and the integrity signals, sending the emails the company asks for, sending results to the tools the company connects (its applicant tracking system, Slack, and its own systems through prepza's API and web hooks), and keeping the results for the company.",
            "People: the candidates the company invites, who apply through its link or whom its applicant tracking system sends, and the members of the company.",
            "Data: candidates' email addresses, names and account ids from their sign-in, their answers, how long each took, page leaves, copy attempts and answers too fast to have read the question during the interview, any extra time the company gives them (without a reason), and the results; the email and applicant tracking system id of candidates that system sends; and the emails of people the company sends a report to.",
            "Duration: while the company uses prepza. Candidates' results are deleted 12 months after their invitation was last sent, candidates an applicant tracking system sends 12 months after they arrive, and everything when the company is deleted.",
        ],
    },
    {
        "heading": "Our duties",
        "items": [
            "We process the data only to provide prepza as the company uses it, following its instructions given through the product and these terms, unless the law requires otherwise; we tell the company if an instruction seems to break data protection law.",
            "Everyone who can access the data is bound to confidentiality.",
            "We keep the data secure: encrypted in transit and at rest, access limited to what each service needs, sign-in through Firebase (Google, LinkedIn or GitHub), signed calls between services, backups with point-in-time recovery, error reports without email addresses, and logs kept briefly.",
            "We help the company answer candidates' requests (access, correction, deletion, objection, review by a person) and with its impact assessments and consultations, as far as the information is ours.",
            "We tell the company without undue delay, and within 48 hours where we can, after becoming aware of a breach of its data, with what we know.",
            "At the end, the data is deleted as described above; the company can download its results before deleting its company.",
            "Tools the company connects (an applicant tracking system, a Slack workspace, or its own systems through prepza's API and web hooks) are its own recipients, not our sub-processors: we send them data only on the company's instruction, given when its owner or admin connects them, and stop when they are disconnected. Where they are outside the EU, that transfer is the company's responsibility.",
            "We give the company the information needed to show that this agreement is kept, and answer reasonable audit questions in writing.",
        ],
    },
    {
        "heading": "Sub-processors",
        "paragraphs": [
            "The company authorises these sub-processors, each bound by data protection terms at least as protective as these:",
        ],
        "items": [
            "Google Cloud (hosting, database, events) and Google Firebase (sign-in).",
            "OpenAI (writing and improving questions, including checking reported questions by the reasons given, never their comments; under its API terms nothing is used for training).",
            "Resend (emails).",
            "Sentry (error reports, without email addresses).",
            "Upstash (short-lived counters for limits and live updates).",
        ],
    },
    {
        "heading": "Changes and transfers",
        "paragraphs": [
            "We announce a new sub-processor at least 14 days before it starts, by email or in the app; a company that objects for reasonable data protection reasons can stop using prepza and delete its company.",
            "Transfers outside the EU are covered by the EU-US Data Privacy Framework or the European Commission's standard contractual clauses.",
        ],
    },
    {
        "heading": "The company's duties",
        "items": [
            "The company has a lawful basis to assess its candidates, tells them how their results are used, and answers their requests.",
            "A candidate who deletes their own prepza account erases their answers and results with it, for every company; the company sees them as a deleted candidate.",
            "prepza makes no decision about a candidate. The company reviews results before deciding, doesn't reject a candidate on the score alone, gives candidates who need it an accommodation such as extra time, and lets a candidate ask for a person to review their result. This applies equally to results sent to its applicant tracking system or other tools: the company doesn't set them up to reject candidates automatically.",
            "The company allows prepza to use candidates' answers, combined and without identifying anyone, to measure and improve the quality of questions across prepza.",
            "Where the law requires it, the company carries out an impact assessment, and gives candidates the notices its jurisdiction requires.",
        ],
    },
    {
        "heading": "Contact",
        "paragraphs": [
            f"Questions about this agreement, and notices under it: {COMPANY['email']}.",
        ],
    },
]
