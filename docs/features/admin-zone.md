# Admin zone

The admin zone is for superadmins: prepza's own team, not a company's admins.

- Superadmins are the accounts in `SUPERADMIN_EMAILS` (verified Google emails).
- Only they see the Admin zone in the account menu.
- Everyone else gets "not found" from its pages and routes.

It has nine tabs, in this order: [Templates](#templates), [News](#news), [Flagged](#flagged-and-replaced), [Replaced](#flagged-and-replaced), [Pass rates](#pass-rates), [Verification](#verification), [Stats](#stats), [Emails](#emails) and [Controls](#controls). On a phone the row scrolls sideways.

## Templates

Ready-made interviews by role (see [Templates and practice](templates-and-practice.md)).

- Generated from a role description, through the same topic review as a company's interview.
- Titles never name a company.
- Can be renamed, checked question by question, re-generated or deleted.

## News

The posts on the public [news page](site.md#news), newest first, like the templates list.

- **New post** opens a dialog: a title (up to 120 characters), a date (today unless changed) and the text (up to 500 characters, with a live count of the characters left). Library checks the limits (`MAX_NEWS_TITLE_LENGTH`, `MAX_NEWS_TEXT_LENGTH` in `prepza_common.constants`); the form only shows them.
- Posts are written in English only. Each row's pencil opens the same dialog to edit it; its bin deletes it after asking.
- Each row says "translated" once the post is in every other language, "translating…" until then.

**Translation:** after a save, library asks generation (`POST /internal/news/{id}/translate`), which queues a worker job (Cloud Tasks). The job reads the post and the languages it lacks from library, translates it into each with the generation model (meaning, not words: each language's hiring terms; "prepza" and product and ATS names kept), and saves those that worked (`PUT /internal/news/{id}/translations`).

- A language that fails, or whose translation is past the limits, keeps showing the English post. The job then fails, so Cloud Tasks runs it again for the missing languages; library's daily schedule sends every post that still lacks one again.
- A changed title or text deletes the post's translations and starts a new translation; a new date alone keeps them. Translations of an older text that arrive after an edit are dropped, and saving the same translation again replaces it.
- While the emergency pause is on, generation refuses the request and the daily schedule sends the post later.
- Without an OpenAI key (locally), nothing is translated, and every language shows the English post.

Routes (library): `GET/POST /superadmin/news`, `PUT/DELETE /superadmin/news/{id}`.

## Flagged and replaced

- **Flagged:** the flagged questions, each to fix now or dismiss. A superadmin's "Fix now" isn't counted towards the verifier's daily limit.
- **Replaced:** the questions the verifier replaced.
- Each replaced question has a "replaced with" button showing the question that took its place: the next kept version, or the question as it is now.

See [Question quality](../generation.md#question-quality) for how questions get flagged.

## Verification

Companies waiting for review of their name and website (see [Companies](companies.md#verification)).

## Pass rates

Lists company interviews with finished candidates, with:

- finished candidates,
- pass rate at the current passing grade,
- average grade,
- share of timed-out answers.

It sorts by lowest pass rate or most finished first. It marks the interviews outside the post-market monitoring triggers: below 10% or above 95%, with 20+ finished.

## Stats

Nine numbers as cards:

1. companies created,
2. companies verified (in the month they were approved),
3. interviews created,
4. candidates invited (in the month they were invited),
5. candidates finished (also in the month they were invited),
6. talents' practice rounds,
7. top-ups,
8. what they paid (tax included, refunds not taken off; a transaction counts once),
9. the credits spent on candidates.

### Period

- A UTC month or year, or all time with the "all time" checkbox.
- The period is one choice in a menu of two columns: a month with its year (the last 12, none before 2026) or a year.
- The menu is off while all time is on.
- The browser keeps the choice for the next visit (`localStorage`), not the address.

### How it counts

Companies, rounds and billing each count their own records, through the shared `prepza_common.stats`:

```
GET /superadmin/stats?period=2026-10   # a month
GET /superadmin/stats?period=2026      # a year
GET /superadmin/stats                  # all time
```

So the numbers are what is stored now: deleted companies and candidates past retention aren't counted.

## Controls

Two switches: the emergency pause and maintenance mode.

### Emergency pause

While it's on, every service answers these with a 503:

- new candidate interviews (invite and job-ad link starts),
- candidate invites (new, sent again or from a list),
- practice rounds,
- previews,
- generations and re-generations,
- verifier jobs,
- the help chat and the assistant (its messages and voice).

Also while it's on:

- The invite and new-interview pages say so; the new-interview box is turned off.
- The scheduled answer-key checks and invite reminders wait until it's off.
- Candidates already in an interview can finish.

The switch is one Redis key (`pause:on`, no expiry) that every service reads. With Redis down, it counts as off. Who turned it and when goes to companies' logs.

### Maintenance mode

Maintenance mode closes the whole site:

- Every page shows a maintenance screen. `proxy.ts` asks companies' public `GET /maintenance`, cached 10 seconds.
- Every service's API answers every request with a 503 (`prepza_common.maintenance`, a middleware in each `main.py`).
- Superadmins still use the site, with a warning above each page.

These stay open, so no event, job or payment is lost:

- `/health` and `/ready`,
- the switch itself,
- `/internal/` (calls between services, Pub/Sub and Scheduler pushes),
- `/webhooks/` (Paddle, Resend, the ATSs).

Billing has no Redis and isn't switched; its only public route is the price catalog.

Turning it on first asks to confirm, showing the number of candidates in an interview right now (a question shown in the last 15 minutes), who may lose time.

It's one Redis key (`maintenance:on`). With Redis down, it counts as off. Each service reads it at most every 5 seconds, so a change reaches every instance within 5 seconds. Who turned it goes to the logs.

## Emails

Stops the emails prepza sends to an address, for someone who asked by email rather than with a link (see [Unsubscribing](notifications.md#unsubscribing)).

- **Find:** an email address, whatever its case. It's sent in the request body, never in a page or API address, which logs record.
- **prepza account:** whether an account signs in with that address (library asks Firebase). If so, its email settings, as Settings → Emails shows them, each changed at once, and "Turn off all optional emails". Service emails can't be turned off.
- **Emails from companies:** the companies that invited the address (companies' invites) or whose emails it stopped, by name, each "Emails are sent", "All emails stopped" or "Reminders stopped for N invites":
  - "Stop emails" stops every email from that company to the address, only for a company that invited it.
  - "Resume emails" lets them through again, reminders included (the person changed their mind).

Both are safe to repeat. A company that's gone isn't listed.

```
POST /library/superadmin/emails/lookup                     {email}
PUT  /library/superadmin/emails/{user_id}/preferences      {changes}
POST /notifications/superadmin/candidate-opt-outs/lookup   {email}
PUT  /notifications/superadmin/candidate-opt-outs          {email, company_id, stopped}
```

What's logged:

- A settings change goes to the consent log (`email_consents`) with the source `admin` and the superadmin's id (`changed_by`), and to library's logs.
- Stopping or resuming a company's emails goes to notifications' logs with the superadmin's id, the company and the address's hash, never the address.
