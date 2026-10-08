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
- Each notification is posted once, in English, with a link back to prepza. What people wrote (titles, emails) shows as typed: a title like `<!channel>` doesn't ping anyone. A redelivered event doesn't post again, nor does one that adds to a grouped notification in the bell (see [Grouping](#grouping)): only the group's first is posted.
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
   Add `http://localhost:8090/api/notifications/slack/callback` to `redirect_urls` for local use.
2. Under **Manage Distribution**, activate public distribution, so other companies' workspaces can add it.
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
- reminders,
- emailed reports, with the PDF attached,
- contact page messages, to `CONTACT_EMAIL` (hello@prepza.ai by default).

`SITE_URL` is the site address that links in emails point to.

### Email preferences and consent

Each user chooses, in Settings > Emails, which emails they get beyond service emails (invites, reports, billing problems, legal changes), which always go out. `library` stores the choices (`/library/me/email-preferences`; other services read them at `/internal/users/{id}/email-preferences`):

- the activity digest, one setting per kind: a candidate finished, an invite wasn't delivered, an ATS candidate wasn't invited, an interview is ready; on by default, with one checkbox in Settings that turns all four on or off,
- reminders (low credits, an interview with no candidates, topics waiting for review); on by default,
- product updates and news: a soft opt-in for prepza's own users. The sign-in dialog offers an unticked "Don't send me product updates and news"; a first sign-in without it ticked turns updates on, with it ticked leaves them off. A later sign-in never turns them back on, and users who haven't signed in since (no stored preferences) have them off,
- offers and promotions: off until the user ticks them, in Settings or on the sign-in dialog. Signing in only turns them on: an unticked box there changes nothing.

Every change is logged and never edited (`email_consents`): the setting, on or off, where (`sign_in`, `settings`, `unsubscribe`), on what basis (`choice`, or `soft_opt_in` for updates turned on at a first sign-in that showed the opt-out), the wording's version (`CONSENT_TEXT_VERSION` in `services/library/app/constants/emails.py`, changed whenever the checkboxes' wording changes) and the time. The account export includes both; deleting the account removes them.

### Unsubscribing

Emails carry signed unsubscribe links (`EMAIL_LINK_SECRET`, an HMAC-SHA256; `services/notifications/app/helpers/unsubscribe.py`). A link names what it stops and whom, never expires, and can't be made for anyone else:

- optional emails to a prepza user (the activity digest or one of its kinds, reminders, updates, offers) name the user and the email; they show "Unsubscribe" and "Change your email settings" (Settings) under the footer, and carry the one-click headers (`List-Unsubscribe`, `List-Unsubscribe-Post: List-Unsubscribe=One-Click`) that mail clients show as their own unsubscribe button. `optional_email` in `services/notifications/app/helpers/emails.py` builds such an email from a template and the type,
- a candidate's invite links to "Don't email me for <company>"; a reminder to that and to "Don't send me reminders for this interview", and its one-click headers stop that interview's reminders. These links name the candidate's address as its SHA-256 (links end up in request logs), the company, and for reminders the invite.

A link opens `/unsubscribe?token=…` (no sign-in, not indexed): it says what stops ("You won't get the activity digest anymore", "You won't get reminders for this interview anymore", "You won't get emails from Acme anymore") and changes nothing until "Confirm", since mail scanners open links. Then it says "You're unsubscribed", with "Email settings" for a signed-in user. The page reads the link at `GET /api/notifications/unsubscribe/{token}` and confirms with a `POST` there; mail clients' one-click `POST` (body `List-Unsubscribe=One-Click`) goes to the same address and needs nothing more. Repeating either changes nothing.

- A user's link turns the setting (or the digest's four kinds) off in `library`, logged with the source `unsubscribe`.
- A candidate's link is kept in notifications (`candidate_opt_outs`, by the address's hash). An invite to an address that stopped the company's emails isn't sent, and the company sees it as undelivered, as with a bounce. A reminder isn't sent when the address stopped the company's emails or that interview's reminders; the company isn't told. An opt-out stays when the company erases the candidate, and goes with the company.

Changing `EMAIL_LINK_SECRET` breaks the links in emails already sent; opt-outs already made stay.

### Sending real emails

Without `RESEND_API_KEY`, emails go to `SMTP_HOST` and `SMTP_PORT`: Mailpit locally (http://localhost:8125). To send real emails through [Resend](https://resend.com):

1. Verify your domain at resend.com/domains.
2. In `.env`, set `RESEND_API_KEY` (a sending-only key is enough) and `MAIL_FROM` with an address on that domain, for example `prepza. <no-reply@yourdomain.com>`.
3. Restart the service: it reads `.env` only when it starts.

With `RESEND_API_KEY` set, a message sent from the local contact page reaches the real `CONTACT_EMAIL` inbox.

### Failed sends

- A failed send answers Pub/Sub's push with an error, so Pub/Sub retries it.
- Over Resend's per-second limit (a burst of invites), it answers 429 instead: Pub/Sub retries with backoff, and it doesn't count as a server error in the alerts.
- After the subscription's maximum attempts, Pub/Sub moves it to the dead-letter topic.
- The error from Resend is in the logs.
- Retries never send an email twice.

### Undelivered emails

To show invites whose email bounced or was marked as spam ("Email not delivered" in the candidate list):

1. Add a webhook at resend.com/webhooks pointing at `https://<your domain>/api/notifications/webhooks/resend`, with the events `email.bounced`, `email.complained` and `email.suppressed`.
2. Put its signing secret (`whsec_...`) in `.env` as `RESEND_WEBHOOK_SECRET`.
3. Restart notifications.

Without the secret, every webhook is refused. Locally, Resend reaches the webhook only through a tunnel, as with Paddle (see [Credits and payments](billing.md#setting-up-paddle)).
