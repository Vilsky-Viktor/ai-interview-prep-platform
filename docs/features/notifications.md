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
- an automatic top-up charged or failed.

Companies' verification decisions and ATS candidates that couldn't be invited (`ats_not_invited`) reach owners and admins in the bell too (see [Companies](companies.md#verification) and [ATS integrations](ats.md#candidates-from-workable)).

## Slack

A company can send its notifications to one Slack channel too, from its integrations tab (Messaging, above the ATSs).

- An owner or admin clicks "Add to Slack", allows prepza in Slack and picks the channel. Back on the company's Slack page, they choose which notifications go there. By default: finished candidates, ATS candidates that weren't invited, undelivered invites and failed automatic top-ups; ready interviews and charged top-ups can be added.
- prepza gets only an incoming web hook for that channel (the `incoming-webhook` scope): it can post there and can't read anything.
- Each new notification is posted once, in English, with a link back to prepza. A redelivered event doesn't post again.
- If Slack says the web hook is gone (the app was removed or the channel deleted), the page shows "Reconnect". Other Slack errors are logged and that message is skipped; the bell always gets it.
- Disconnecting, or deleting the company, removes prepza's app from the workspace and the channel from prepza.
- Members who can't edit see the channel and its notifications without changing them.
- The channel works while whoever connected it is still an owner or admin; once they're removed or made a viewer, it's marked for reconnecting by a current editor.

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

### Grouping

Bursts are grouped. Another finished candidate, undelivered invite, or flagged or fixed question about the same interview within 24 hours adds to the last notification ("3 candidates finished …") instead of making a new one.

## Emails

The service sends, as HTML with a plain-text version:

- candidate invites,
- reminders,
- emailed reports, with the PDF attached,
- contact page messages, to `CONTACT_EMAIL` (hello@prepza.ai by default).

`SITE_URL` is the site address that links in emails point to.

### Sending real emails

Without `RESEND_API_KEY`, emails go to `SMTP_HOST` and `SMTP_PORT`: Mailpit locally (http://localhost:8125). To send real emails through [Resend](https://resend.com):

1. Verify your domain at resend.com/domains.
2. In `.env`, set `RESEND_API_KEY` (a sending-only key is enough) and `MAIL_FROM` with an address on that domain, for example `prepza. <no-reply@yourdomain.com>`.
3. Restart the service: it reads `.env` only when it starts.

With `RESEND_API_KEY` set, a message sent from the local contact page reaches the real `CONTACT_EMAIL` inbox.

### Failed sends

- A failed send answers Pub/Sub's push with an error, so Pub/Sub retries it.
- After the subscription's maximum attempts, Pub/Sub moves it to the dead-letter topic.
- The error from Resend is in the logs.
- Retries never send an email twice.

### Undelivered emails

To show invites whose email bounced or was marked as spam ("Email not delivered" in the candidate list):

1. Add a webhook at resend.com/webhooks pointing at `https://<your domain>/api/notifications/webhooks/resend`, with the events `email.bounced`, `email.complained` and `email.suppressed`.
2. Put its signing secret (`whsec_...`) in `.env` as `RESEND_WEBHOOK_SECRET`.
3. Restart notifications.

Without the secret, every webhook is refused. Locally, Resend reaches the webhook only through a tunnel, as with Paddle (see [Credits and payments](billing.md#setting-up-paddle)).
