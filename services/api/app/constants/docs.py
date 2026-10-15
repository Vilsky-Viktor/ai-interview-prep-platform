# The public API's description: its reference's API, web hooks and SDK tabs, each under its
# "# " title (the developer docs page splits it there; objects are the fourth tab).
API_TITLE = "prepza API"
API_VERSION = "1"
API_DESCRIPTION = """# API

The prepza API connects prepza to your own platform. Use it to create interviews from job
descriptions, invite candidates, remind, update or remove them, read their results, find a
candidate by email and read your credits, and receive a [web hook](/api-docs?tab=webhooks) as
soon as a candidate finishes.

## Getting an API key

1. Sign in to prepza as an owner or admin of your company.
2. Open **Hiring**, select your company and go to the **Integrations** tab.
3. In the **API** section, open the API page and select **New key**.
4. Name the key after the platform that will use it, choose when it expires (in 1, 3, 6 or 12
   months, or never), then select **New key**.
5. Copy the key and store it securely. It is shown only once: prepza keeps only a hash of it.

A company can have up to 10 keys. An expired key returns `401`; make a new one before it
expires. Deleting a key on the same page revokes it immediately.

## Authentication

Send the key with every request in the `Authorization` header: `Authorization: Bearer pz_...`.
A key belongs to one company and acts on behalf of the member who created it, so invitations are
sent under that member's email limits. If the member leaves the company or is no longer an owner
or admin, the key stops working and requests return `401`.

## Rate limits and pagination

Your company's keys together can make up to 60 requests per minute; further requests return
`429` until the minute ends. List endpoints return the newest items first and accept `offset` and `limit` (up to 100
items per request).

## Retrying safely

Creating an interview and inviting a candidate accept an `Idempotency-Key` header: any unique
string, such as a UUID. If a request times out, send it again with the same key: within 24 hours
you get the first request's result, and the candidate isn't emailed twice. A retry while the
first request is still running returns `409`.

## Errors

Failed requests return a standard HTTP status code and a JSON body whose `detail` field describes
the problem. Each endpoint below lists the errors it can return.

## Results support a person's decision

A candidate's `grade`, `passed` and `signals` help a person decide; they are not a decision.
Don't reject candidates automatically on them: before rejecting anyone, a person should open the
candidate's full results (`results_url`) and review them.

## Invite links

Until a candidate finishes, they come with their invite link (`invite_url`), the same link the
invite email carries. Send it to them yourself if the email didn't reach them; only the invited
email can use it, unless they were invited with `sign_in` false. It's null once they've finished
or the invite has expired.

## Sending candidates from your own platform

When your platform already knows who the candidate is, invite them with `sign_in` false: prepza
sends no emails, and the `invite_url` opens the interview without signing in to prepza. Anyone
with that link can take the interview, so give it only to the candidate. Add a `return_url` on
your company's verified website domain to bring them back once they've finished, or [embed the
interview](/api-docs?tab=sdk) in your own page instead.

## Verified companies

Bringing candidates back to your site and [embedding the interview](/api-docs?tab=sdk) work only
on your company's verified website domain and its subdomains. To verify your company, select
**Verify** next to its name in prepza and enter its website. Once an owner or admin signs in with
a work email on that domain, prepza reviews the company and adds the verified badge; until then, a
`return_url` returns `422` and an [embedded interview](/api-docs?tab=sdk) isn't shown.

# Web hooks

Owners and admins can add up to 5 web hook endpoints on the same API page. Each endpoint gets
every event below as a `POST` request: a candidate started, finished (with their results), wasn't
reached by the invitation email, expired or was removed, and an interview is ready. Ignore the
types you don't need. A candidate's results never change after they finish: a fixed question
applies only to candidates who start after the fix. Endpoints must use HTTPS and be reachable
from the public internet.

On the API page, **send test event** sends a signed `test` event to an endpoint at once, and the
**delivery log** shows its latest 20 sends: each event's type, when, and whether it was
delivered, the status the endpoint answered, or what went wrong.

Every request carries a `Prepza-Signature` header in the form `t=<timestamp>,v1=<signature>`. The
signature is the hex-encoded HMAC-SHA256 of `<timestamp>.<raw request body>`, computed with the
web hook's signing secret, which is shown once when the web hook is added. Verify the signature,
and reject requests whose timestamp is more than a few minutes old, before processing an event.

Respond with any `2xx` status within 10 seconds to confirm delivery. Other responses and timeouts
are retried with growing pauses, from 5 minutes up to 6 hours apart, for 3 days; after that the
web hook is paused: it gets no events, and the API page shows it as paused, until a test event
sent from there goes through. An event can occasionally arrive more than once; use its `id` to
ignore duplicates.

Each request body is a JSON object with the event's `id`, its `type`, `occurred_at` (when the
change happened, in ISO 8601) and its `data`. A retried event can arrive after a later one, so
order a candidate's events by `occurred_at`, not by when they arrive.

# SDK

Your page can show the interview itself, for a candidate invited with `sign_in` false. Your
server invites them and passes the `invite_url` to your page, which embeds it with prepza's
script; never put your API key in a page. The page must be on your company's verified website
domain (or a subdomain of it) and served over HTTPS: anywhere else the interview isn't shown.

```html
<div id="interview"></div>
<script src="https://prepza.ai/embed/v1.js"></script>
<script>
  const interview = Prepza.embed({
    element: "#interview",
    url: "https://prepza.ai/invite/3fTq9xLk2VbN7wZr8YcP1mHd5sJ4gAe6uQo0RiKtEy",
    theme: "dark",
    onReady: () => {},
    onStart: () => {},
    onFinish: ({ candidateId }) => {},
  })
</script>
```

`theme` is optional: `"light"` or `"dark"` always shows the interview in that theme, in your
company's colors for it (set on the company's **brand** tab); `"default"`, or none, the
candidate's own theme, or the one the invite asked for. The frame fits its height to the
interview. `onFinish` gets the candidate's `id`, so your page can take them on; their results come
with the `candidate.finished` web hook as usual. `interview.destroy()` removes the frame. While
the interview runs, the candidate should stay on it: leaving it, including for the rest of your
page, is recorded as a page leave."""
