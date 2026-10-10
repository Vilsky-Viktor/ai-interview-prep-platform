# Notifications and emails

The `notifications` service sends prepza's emails and keeps the bell's notifications. Both are driven by events (see [Architecture](../architecture.md#events)).

## The bell

A bell next to the account menu shows notifications live: it updates within a second, without reloading.

- A badge counts the unread ones.
- It shows the latest 10.
- Each person or company keeps at most 100, none older than 90 days.
- A deleted company's notifications go with it.

### What gets a notification

Only what matters, for every member of a company:

- a candidate finished (with their grade),
- an invite not delivered,
- an interview ready or cancelled,
- a flagged and fixed interview question,
- a referral reward,
- an automatic top-up charged or failed,
- an ATS candidate who couldn't be invited (`ats_not_invited`, see [ATS integrations](ats.md#candidates-from-workable)).

Companies' verification decisions reach only the owner and admins, one notification each, as viewers can't act on them (see [Companies](companies.md#verification)).

## Slack

A company can send its notifications to one Slack channel too, from its integrations tab (Messaging, above the ATSs).

- An owner or admin clicks "Add to Slack", allows prepza in Slack and picks the channel. Back on the company's Slack page, they choose which notifications go there. Each "Add to Slack" link works once, for 15 minutes, and only while whoever clicked it is still an owner or admin. By default: finished candidates, ATS candidates that weren't invited, undelivered invites and failed automatic top-ups; ready interviews and charged top-ups can be added.
- prepza gets only an incoming web hook for that channel (the `incoming-webhook` scope): it can post there and can't read anything.
- Each notification is posted once, in English, with a link back to prepza. What people wrote (titles, emails) shows as typed: a title like `<!channel>` doesn't ping anyone. Every notification is posted, also one the bell groups with others (see [Grouping](#grouping)); a redelivered event doesn't post again.
- The bell gets the notification first, whatever happens in Slack. If Slack is busy or down (rate limited, a server error, a timeout), the event is retried with Pub/Sub's backoff and the retry posts the message; the bell doesn't get it twice.
- If Slack says the web hook is gone (the app was removed or the channel deleted), the page shows "Reconnect". A message Slack refuses for good is logged and skipped.
- Disconnecting, or deleting the company, removes the channel from prepza, and prepza's app from the workspace unless another company still posts there. Reconnecting to the same workspace keeps the app; reconnecting to another workspace removes it from the earlier one (again, unless another company uses it).
- Members who can't edit see the channel and its notifications without changing them.
- The channel works while whoever connected it is still an owner or admin; once they're removed or made a viewer, it's marked for reconnecting by a current editor. If they delete their prepza account, the channel stays without their id (`deleted-user`), marked for reconnecting; their data export lists the channels they connected.

### Setting up Slack

1. At api.slack.com/apps, create an app "From a manifest" with:
   ```yaml
   display_information:
     name: prepza
     description: Hiring notifications from prepza
   features:
     bot_user:
       display_name: prepza
       always_online: false
   oauth_config:
     redirect_urls:
       - https://<your domain>/api/notifications/slack/callback
     scopes:
       bot:
         - incoming-webhook
   settings:
     org_deploy_enabled: false
     socket_mode_enabled: false
     token_rotation_enabled: false
   ```
   Slack asks for the bot user: bot scopes, `incoming-webhook` among them, need one. A publicly distributed app takes only `https` redirect URLs, so local development uses a second app, "prepza (dev)", made from the same manifest with only `http://localhost:8090/api/notifications/slack/callback`, not distributed: it works in your own workspace, and its keys go in the local `.env`.
2. Under **Manage Distribution**, tick that the app has no hard-coded tokens or web hooks (prepza gets each company's through OAuth) and activate public distribution, so other companies' workspaces can add it.
3. Put its **Client ID** and **Client Secret** (Basic Information) in `.env` as `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET`.
4. Set `SLACK_ENCRYPTION_KEY`, the Fernet key that encrypts the web hooks:
   ```bash
   python3 -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
   ```
   Keep it: a new key makes every company reconnect.
5. Restart notifications.

Until all three are set, "Add to Slack" answers "Slack isn't set up yet" and nothing is posted.

### Erased candidates

When a company erases a candidate (`candidate.removed` from companies), its notifications about them (their email and grade) go. When a candidate deletes their prepza account, every company's notifications about them go too.

### Grouping

Bursts are grouped. Another finished candidate, undelivered invite, flagged or fixed question, or ATS candidate who couldn't be invited, about the same page and title (for example the same interview) within 24 hours, adds to the last notification ("3 candidates finished …") instead of making a new one.

## Emails

The service sends, as HTML with a plain-text version:

- candidate invites,
- candidates' reminders,
- emailed reports, with the PDF attached,
- contact page messages, to `CONTACT_EMAIL` (hello@prepza.ai by default),
- to company members: the activity digest, reminders, and failed automatic top-ups (see [Emails to company members](#emails-to-company-members)).

`SITE_URL` is the site address that links in emails point to; emails link only there (no shorteners or tracking redirects).

- **Two senders:** service emails come from `MAIL_FROM`, and the emails a user may turn off (the digest and reminders) from `MAIL_FROM_UPDATES`, on a subdomain of its own, so spam complaints about them can't hurt the service emails' reputation. The DNS records both need are in [infra/README.md](../../infra/README.md#email-deliverability).
- **Replies** go to the member who shared a report, to the visitor for contact messages, and otherwise to `CONTACT_EMAIL`, prepza's inbox, rather than to an unread no-reply address.
- **Headers:** every email has `Auto-Submitted: auto-generated` (no out-of-office replies); only those the recipient may stop carry the one-click unsubscribe headers (see [Unsubscribing](#unsubscribing)).

### Emails to company members

All three follow the invites' layout, with a plain-text version, in the member's interface language (their sign-in's language, from library). What they list links into the app.

- **Activity digest** (optional, `digest`): one email a day per person, covering every company they're a member of (any role). It lists what reached the companies' bells in the 24 hours before the hour its runs are in, only of the kinds the person gets, grouped by company: candidates who finished and undelivered invites, each with its count and interview; ATS candidates not invited, with their count; interviews ready. Nothing happened, or every kind is off: no email. It shows counts and titles only, no candidate's address or grade. Its "Unsubscribe" stops the whole digest; "Change your email settings" chooses kinds.
- **Reminders** (optional, the one `reminders` setting), to owners and admins, each kind at most once in 7 days to a person:
  - credits running low: companies whose available credits can't pay for another candidate and that no automatic top-up refills (billing decides), again each week while that lasts,
  - waiting for candidates: an interview nobody was invited to, 3 days after it got its questions (not one marked hired); each interview once, and none ready more than 10 days ago,
  - topics waiting for review: to whoever started the interview, while they're still an owner or admin, once its topics have waited a day; each interview once. Generation cancels a review after 14 days, which the email says.
- **Automatic top-up failed** (a service email, always sent): at once to the company's owners and admins, with the bell's notification. No unsubscribe link; its footer says it's about the company's billing, so it's sent whatever their email settings. A retried event doesn't send it twice (Resend's key is the event and the person).

The digest and reminders are sent by `notifications` on a schedule: `POST /internal/schedules/digest` every 10 minutes from 7:00 to 7:50 UTC and `/internal/schedules/reminders` from 8:00 to 8:50 (`infra/terraform/jobs.tf`, `scripts/local/crontab`). A run reads what it needs with one batched call to each service (members from companies, low credits from billing, waiting interviews from companies and their review statuses from generation, addresses, languages and settings from library), then sends for at most 40 seconds, one email every 0.6 seconds to stay under Resend's per-second limit; the next run goes on with the rest.

- **Never twice:** each email is claimed in a sent log (`sent_emails`: the person, the kind, the day or what a reminder named) under a per-person lock and a unique constraint, so a re-run or two runs at once send it once. A send that fails gives its claim back for the next run; Resend's idempotency key (the person, the kind and the email's content) keeps a send that failed but went through from going out again.
- **Resend busy** (429): the run gives back its claim and stops; the next run sends the rest. Any other failure fails the run (and the scheduler's alert) after giving the claim back.
- The log keeps 30 days; deleting an account removes the person's rows.

### Email preferences and consent

Each user chooses, in Settings > Emails, which emails they get beyond service emails (invites, reports, billing problems, legal changes), which always go out. `library` stores the choices (`/library/me/email-preferences`; other services read them at `/internal/users/{id}/email-preferences`):

- the activity digest, one setting per kind: a candidate finished, an invite wasn't delivered, an ATS candidate wasn't invited, an interview is ready; on by default, with one checkbox in Settings that turns all four on or off,
- reminders (low credits, an interview with no candidates, topics waiting for review); on by default,
- product updates and news: a soft opt-in for prepza's own users. The sign-in dialog offers an unticked "Don't send me product updates and news"; a first sign-in without it ticked turns updates on, with it ticked leaves them off. A later sign-in never turns them back on, and users who haven't signed in since (no stored preferences) have them off,
- offers and promotions: off until the user ticks them, in Settings or on the sign-in dialog. Signing in only turns them on: an unticked box there changes nothing.

The sign-in dialog shows both checkboxes only on a browser where no one has signed in yet (a `prepza:signed-in-before` flag in local storage, set at every sign-in): an existing account's choices are in its Settings.

Every change is logged and never edited (`email_consents`): the setting, on or off, where (`sign_in`, `settings`, `unsubscribe`, or `admin` with the superadmin's id in `changed_by`), on what basis (`choice`, or `soft_opt_in` for updates turned on at a first sign-in that showed the opt-out), the wording's version (`CONSENT_TEXT_VERSION` in `services/library/app/constants/emails.py`, changed whenever the checkboxes' wording changes) and the time. The account export includes both; deleting the account removes them.

### Unsubscribing

Emails carry signed unsubscribe links (`EMAIL_LINK_SECRET`, an HMAC-SHA256; `services/notifications/app/helpers/unsubscribe.py`). A link names what it stops and whom, never expires, and can't be made for anyone else:

- optional emails to a prepza user (the activity digest or one of its kinds, reminders, updates, offers) name the user and the email; they show "Unsubscribe" and "Change your email settings" (Settings) under the footer, and carry the one-click headers (`List-Unsubscribe`, `List-Unsubscribe-Post: List-Unsubscribe=One-Click`) that mail clients show as their own unsubscribe button. `optional_email` in `services/notifications/app/helpers/emails.py` builds such an email from a template and the type,
- a candidate's invite links to "Don't email me for <company>"; a reminder to that and to "Don't send me reminders for this interview", and its one-click headers stop that interview's reminders. These links name the candidate's address as its SHA-256 (links end up in request logs), the company, and for reminders the invite.

A link opens `/unsubscribe?token=…` (no sign-in, not indexed): it says what stops ("You won't get the activity digest anymore", "You won't get reminders for this interview anymore", "You won't get emails from Acme anymore") and changes nothing until "Confirm", since mail scanners open links. Then it says "You're unsubscribed", with "Email settings" for a signed-in user. The page reads the link at `GET /api/notifications/unsubscribe/{token}` and confirms with a `POST` there; mail clients' one-click `POST` (body `List-Unsubscribe=One-Click`) goes to the same address and needs nothing more. Repeating either changes nothing.

- A user's link turns the setting (or the digest's four kinds) off in `library`, logged with the source `unsubscribe`. Marking the digest or reminders as spam does the same: those emails are tagged with the user and what they are, and Resend's `email.complained` webhook (see [Undelivered emails](#undelivered-emails)) turns that email off as its link would.
- A candidate's link is kept in notifications (`candidate_opt_outs`, by the address's hash). An invite to an address that stopped the company's emails isn't sent, and the company sees it as undelivered, as with a bounce. A reminder isn't sent when the address stopped the company's emails or that interview's reminders; the company isn't told. An opt-out stays when the company erases the candidate, and goes with the company.

Someone who asks by email instead: a superadmin turns their settings off, or stops or resumes a company's emails to their address, on the admin zone's [Emails](admin-zone.md#emails) tab. Companies' invites tell which companies invited the address (`POST /internal/invites/companies`, the address in the body).

Changing `EMAIL_LINK_SECRET` breaks the links in emails already sent; opt-outs already made stay.

### Sending real emails

Without `RESEND_API_KEY`, emails go to `SMTP_HOST` and `SMTP_PORT`: Mailpit locally (http://localhost:8125). To send real emails through [Resend](https://resend.com):

1. Verify your domain at resend.com/domains.
2. In `.env`, set `RESEND_API_KEY` (a sending-only key is enough), `MAIL_FROM` with an address on that domain, for example `prepza. <no-reply@yourdomain.com>`, and `MAIL_FROM_UPDATES` with one on a subdomain verified too, for example `prepza. <updates@mail.yourdomain.com>`. Keep click and open tracking off for both domains in Resend.
3. Restart the service: it reads `.env` only when it starts.

With `RESEND_API_KEY` set, a message sent from the local contact page reaches the real `CONTACT_EMAIL` inbox.

### Failed sends

- A failed send answers Pub/Sub's push with an error, so Pub/Sub retries it.
- Over Resend's per-second limit (a burst of invites), it answers 429 instead: Pub/Sub retries with backoff, and it doesn't count as a server error in the alerts.
- After the subscription's maximum attempts, Pub/Sub moves it to the dead-letter topic.
- The error from Resend is in the logs.
- Retries never send an email twice.

### Undelivered emails

To show invites whose email bounced or was marked as spam ("Email not delivered" in the candidate list), and to turn off the digest or reminders for a user who marked them as spam:

1. Add a webhook at resend.com/webhooks pointing at `https://<your domain>/api/notifications/webhooks/resend`, with the events `email.bounced`, `email.complained` and `email.suppressed`.
2. Put its signing secret (`whsec_...`) in `.env` as `RESEND_WEBHOOK_SECRET`.
3. Restart notifications.

Without the secret, every webhook is refused. Locally, Resend reaches the webhook only through a tunnel, as with Paddle (see [Credits and payments](billing.md#setting-up-paddle)).
