# Candidates

How candidates get to an interview, how they take it, and what the company sees afterwards.

- [Invites](#invites)
- [Revoking a candidate](#revoking-a-candidate)
- [Candidate names](#candidate-names)
- [Shareable link](#shareable-link)
- [Taking an interview](#taking-an-interview)
- [Timing](#timing)
- [Scorecards](#scorecards)
- [The candidate list](#the-candidate-list)
- [Reports](#reports)
- [Email limits](#email-limits)
- [Retention](#retention)

## Invites

Owners and admins invite candidates by email, in the "New candidate(s)" dialog's three tabs (the last one used is remembered in the browser):

- **one:** an email and an optional name,
- **many:** a pasted list, one candidate per line (or several separated by commas or semicolons), with or without names (`Name <email>` or `email, Name`),
- **upload:** a CSV or TXT file (at most 50 KB; another type, or a file that isn't text, is refused); the tab has buttons that download example files (`frontend/public/examples/prepza-candidates-example.csv` and `prepza-candidates-example.txt`).

Each line nobody can be invited from is named under the list with its one reason: no email found, an email that isn't valid, or a name not written as `Name <email>` (the first 10, then how many more). After inviting, the list keeps only those lines and the emails that weren't invited. The service reads the list and decides (`helpers/candidate_lists.py`, `helpers/list_files.py` in companies).

A list or file takes up to 100 emails at once, and only the emails in it count, with the names written with them (see [Candidate names](#candidate-names)). A list skips candidates who already started, so they aren't emailed again.

An invite can be resent or revoked (see [Revoking a candidate](#revoking-a-candidate)). The invite page tells candidates what to expect before they start. A visitor who isn't signed in sees the invitation (the company, the interview and its rules, but not the invited email) with a **Sign in to start** button. Signed in with another email, the page explains in a warning that only the invited email can start; once the interview is finished, it says so in an info card.

Until the candidate finishes, owners and admins see the invite link on the candidate's page, in a card with a copy button, to send it themselves if the email didn't arrive or got lost. An expired invite has none (sending it again revives it), and viewers don't see it.

A candidate's credits are set aside on invite and given back if they never answer (see [Credits and payments](billing.md)).

### Reminders and expiry

| When | What happens |
|---|---|
| Not started after 3 days | One reminder email. A daily job runs it (`/internal/schedules/invite-reminders`) |
| Not started within 30 days | The invite expires and its credits come back. Sending it again, or the candidate starting through the shareable link, sets them aside again |

Candidates can also arrive from an ATS (see [ATS integrations](ats.md)).

## Revoking a candidate

Owners and admins can revoke any candidate in the list (`DELETE /interviews/{id}/candidates/{invite_id}` in companies):

- **Not started yet:** the invite is withdrawn; its link stops working and the credits set aside come back. The candidate can be invited again later.
- **Started or finished:** the candidate is erased for good, with their answers, timings and results in rounds, for example when they ask to have their data deleted. A candidate who picked an answer to at least one question (one whose time ran out doesn't count) is charged (a finished one stays charged); other credits still held come back.

Either way the company's [audit log](companies.md#audit-log) records it, and companies publishes `candidate.removed`: the company's bell notifications about the candidate go, and so does the ATS's record of them for that interview.

## Candidate names

Each candidate may have a name (`name`, null while unknown; the app shows "No name yet"). It's untrusted text: trimmed, cut to 200 characters (`MAX_CANDIDATE_NAME_LENGTH` in prepza_common) and shown only as text.

Where it comes from, first one wins (each fills only a name not known yet):

- **The inviter:** the invite dialog's optional name field (for one email), a list's `Name <email>` or `email, Name` lines, or a CSV file whose header has a name column (`name`, `full name`, or a first and a last name, in English or the 23 languages: `constants/name_headers.py` in companies). The list is read on the backend (`helpers/candidate_lists.py`). The public API's invite takes an optional `name`.
- **The ATS:** the name the ATS sends with the candidate (Workable's and Recruitee's and Breezy HR's `name`, Greenhouse's `first_name` and `last_name`, Teamtailor's `first-name` and `last-name`), kept on the ATS candidate and passed with the invite.
- **The sign-in:** when a candidate starts, through an invite or the shareable link, the name claim of their verified sign-in (Google, LinkedIn or GitHub). A name sent in the request is never used.

Inviting the same address again (a list pasted again, an ATS event delivered twice) keeps a known name. Owners and admins correct it on the candidate's page, under the email, like a title (`PATCH /interviews/{id}/candidates/{invite_id}/name` in companies), for example when the sign-in gave a nickname; a blank name makes it unknown again. Viewers see it read-only.

**Where it shows:** under the email in the candidate list and on the candidate's page; in the candidate's and the test's PDF reports, the shared summaries, a report's email ("Name (email)"), and the bell's and Slack's notifications about the candidate; as `name` in the candidate APIs and the public API. Searching candidates matches part of the email or the name, in any case.

**Personal data:** it is kept and deleted with the invite (revoking or deleting the candidate, retention, the interview or the company going), with the ATS's record of the candidate, and with the notifications about them. When the candidate deletes their account, the name is erased with their email, and their data export lists it. Invites are matched to an account by its email only when that email is verified (`app/helpers/accounts.py` in library), so a sign-in that merely claims an address can't erase or download them.

## Shareable link

The shareable link (`/apply/{token}`) is one link per interview, for a job ad. Owners and admins turn it on.

- Anyone who opens it signs in and takes the interview.
- Each verified email can take it once.
- It is charged like an invited candidate.
- Turning it off, or marking the interview as hired, stops it at once.
- It takes at most 30 new candidates an hour, and one address starts at most 10 an hour across all links (`LINK_STARTS_PER_HOUR`, `LINK_STARTS_PER_IP_HOUR`), so a script with many accounts can't use up a company's credits; over either, a 429. A candidate already invited is never held back by them.

## Taking an interview

- Each candidate gets a random subset of each topic, with their own question order and option order.
- The interview is a single pass.
- A candidate can change their pick until they press Next question, finish the interview, or the question's time runs out. The pick is sent then, and it's final.
- Unanswered questions count as wrong.
- Candidates never see their scores or whether an answer was right.

The backend decides which section and question come next, and when the interview is done: `POST /sessions/{id}/step` and `/finish-interview` in rounds (`app/routers/interview_flow.py`).

Questions and options carry the interview's language (`lang`), so screen readers read them in it whatever the interface language.

## Timing

Every interview is timed. Each question has its own countdown.

- 60 seconds by default, adjustable per interview on its settings tab.
- The countdown turns red for the last 10 seconds, or for the last third of a shorter question.
- At zero, the pick on screen counts. If nothing is picked, the question counts as wrong.

While the questions run, the page shows only them: no header, footer or "ask agent", nothing to leave the page through by accident (a page leave is recorded, and the clock keeps running). The same goes for practice rounds and a company's preview. Once the interview is finished, the header and footer come back.

### Extra time

For a candidate who needs more time, for example because of a disability, owners and admins can give extra time on each question: +25%, +50% or +100% (`PUT /interviews/{id}/candidates/{invite_id}/extra-time` in companies). It is set per candidate, on their page, and only before they start: their questions' time is fixed then. No reason is recorded, and the company's [audit log](companies.md#audit-log) records the change. The invite page tells candidates to ask the company before they start.

The server enforces the clock:

- Closing the tab doesn't stop it.
- It accepts an answer up to 5 seconds after the deadline (`TIME_GRACE_SECONDS`), for a pick sent as the clock reaches zero.
- An interview the candidate leaves finishes by itself once its total time, plus 10%, has passed. Unanswered questions count as wrong.

## Scorecards

A scorecard shows every answer, whether it was right and how long it took. It flags:

- answers too fast to have read the question,
- times the candidate left the page,
- copy attempts.

One session's browser may report a page leave or a copy 60 times a minute (a 429 past that), and a question keeps at most 50 (`MAX_SIGNALS_PER_QUESTION`): one already flags the candidate, so a script can't flood the scorecard.

## The candidate list

- Sorted by grade by default: best first, candidates without a grade yet last.
- Can be sorted by invite date instead.
- Can be searched by email or name.
- Can be filtered by status: invited, in process, finished, passed, flagged, not delivered, expired.

Any member, viewers too, can also search a company's candidates across all its interviews by email or name, newest first, a page at a time (`GET /companies/{id}/candidates?q=&offset=&limit=` in companies). Each row is a list row with its interview's id and title; candidates of a deleted interview are gone with it. The app has no page for it.

"Not delivered" means the invite email bounced or was marked as spam (see [Notifications and emails](notifications.md#undelivered-emails)).

Each candidate's grade and integrity flag are stored on their invite when they finish, so the list is sorted, filtered and paged in the database.

## Reports

A report is a PDF, made in the browser, for one candidate or for all of an interview's candidates. A report can be:

- downloaded,
- emailed from prepza, with the PDF attached (it counts towards the member's email limits),
- shared as a short summary on WhatsApp, Telegram, Viber or LINE (Viber's button opens only where its app is installed).

## Email limits

Candidate invite and report emails are limited:

| Limit | Setting | Default |
|---|---|---|
| Per user, an hour | `EMAIL_HOURLY_LIMIT` | 100 |
| Per user, a day | `EMAIL_DAILY_LIMIT` | 200 |
| Per recipient address, a day | `EMAIL_RECIPIENT_DAILY_LIMIT` | 3 |
| Reports a company emails a day | `REPORT_EMAILS_PER_COMPANY_DAY` | 20 |

An invite counts towards these limits only once the company's credits are set aside for it: an invite refused for lack of credits (an ATS's too) uses up none of them, and one refused over a limit gives back the credits it just set aside.

A company emails a candidate's report only once that candidate has finished the interview.

## Retention

| Data | Kept | Deleted by |
|---|---|---|
| A candidate's invite (email and name), answers, timings, integrity signals and results | 365 days after the invite was last sent | The daily retention job in companies (`/internal/schedules/retention`), with the sessions in rounds and any credits still held |
| A candidate an ATS sent (email and ATS ids), with any results waiting to go back | 365 days | The ats `recover` job (every 10 minutes); see [ATS integrations](ats.md) |

Both go earlier with their interview, their company, or when the company revokes the candidate.
