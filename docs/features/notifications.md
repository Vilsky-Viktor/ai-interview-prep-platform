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
