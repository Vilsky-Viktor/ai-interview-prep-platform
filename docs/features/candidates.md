# Candidates

How candidates get to an interview, how they take it, and what the company sees afterwards.

- [Invites](#invites)
- [Shareable link](#shareable-link)
- [Taking an interview](#taking-an-interview)
- [Timing](#timing)
- [Scorecards](#scorecards)
- [The candidate list](#the-candidate-list)
- [Reports](#reports)
- [Email limits](#email-limits)

## Invites

Owners and admins invite candidates by email:

- one by one,
- by pasting a list,
- or by uploading a file.

A list or file takes up to 100 emails at once, and only the emails in it count. A list skips candidates who already started, so they aren't emailed again.

An invite can be resent, or revoked while the candidate hasn't used it yet. The invite page tells candidates what to expect before they start.

A candidate's credits are set aside on invite and given back if they never answer (see [Credits and payments](billing.md)).

### Reminders and expiry

| When | What happens |
|---|---|
| Not started after 3 days | One reminder email. A daily job runs it (`/internal/schedules/invite-reminders`) |
| Not started within 30 days | The invite expires and its credits come back |

Candidates can also arrive from an ATS (see [ATS integrations](ats.md)).

## Shareable link

The shareable link (`/apply/{token}`) is one link per interview, for a job ad. Owners and admins turn it on.

- Anyone who opens it signs in and takes the interview.
- Each verified email can take it once.
- It is charged like an invited candidate.
- Turning it off, or marking the interview as hired, stops it at once.

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

The server enforces the clock:

- Closing the tab doesn't stop it.
- It accepts an answer up to 5 seconds after the deadline (`TIME_GRACE_SECONDS`), for a pick sent as the clock reaches zero.
- An interview the candidate leaves finishes by itself once its total time, plus 10%, has passed. Unanswered questions count as wrong.

## Scorecards

A scorecard shows every answer, whether it was right and how long it took. It flags:

- answers too fast to have read the question,
- times the candidate left the page,
- copy attempts.

## The candidate list

- Sorted by grade by default: best first, candidates without a grade yet last.
- Can be sorted by invite date instead.
- Can be searched by email.
- Can be filtered by status: invited, in process, finished, passed, flagged, not delivered, expired.

"Not delivered" means the invite email bounced or was marked as spam (see [Notifications and emails](notifications.md#undelivered-emails)).

Each candidate's grade and integrity flag are stored on their invite when they finish, so the list is sorted, filtered and paged in the database.

## Reports

A report is a PDF, made in the browser, for one candidate or for all of an interview's candidates. A report can be:

- downloaded,
- emailed from prepza, with the PDF attached (it counts towards the member's email limits),
- shared as a short summary on WhatsApp or Telegram.

## Email limits

Candidate invite and report emails are limited:

| Limit | Setting | Default |
|---|---|---|
| Per user, an hour | `EMAIL_HOURLY_LIMIT` | 100 |
| Per user, a day | `EMAIL_DAILY_LIMIT` | 200 |
| Per recipient address, a day | `EMAIL_RECIPIENT_DAILY_LIMIT` | 3 |
| Reports a company emails a day | `REPORT_EMAILS_PER_COMPANY_DAY` | 20 |

A company emails a candidate's report only once that candidate has finished the interview.
