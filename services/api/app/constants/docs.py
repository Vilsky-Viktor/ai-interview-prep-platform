# The public API's description, at the top of its reference.
API_TITLE = "prepza API"
API_VERSION = "1"
API_DESCRIPTION = """The prepza API connects prepza to your own platform. Use it to retrieve your
company's interviews, invite candidates and read their results, and receive a web hook as soon as
a candidate finishes.

## Results support a person's decision

A candidate's `grade`, `passed` and `signals` help a person decide; they are not a decision.
Don't reject candidates automatically on them: before rejecting anyone, a person should open the
candidate's full results (`results_url`) and review them.

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

## Errors

Failed requests return a standard HTTP status code and a JSON body whose `detail` field describes
the problem. Each endpoint below lists the errors it can return.

## Web hooks

Owners and admins can add up to 5 web hook endpoints on the same API page. When a candidate
finishes an interview, prepza sends a `POST` request to each endpoint. Endpoints must use HTTPS
and be reachable from the public internet.

Every request carries a `Prepza-Signature` header in the form `t=<timestamp>,v1=<signature>`. The
signature is the hex-encoded HMAC-SHA256 of `<timestamp>.<raw request body>`, computed with the
web hook's signing secret, which is shown once when the web hook is added. Verify the signature,
and reject requests whose timestamp is more than a few minutes old, before processing an event.

Respond with any `2xx` status within 10 seconds to confirm delivery. Other responses and timeouts
are retried with growing pauses, from 5 minutes up to 6 hours apart, for 3 days; after that the
web hook is marked as failing on the API page until it takes an event again. An event can
occasionally arrive more than once; use its `id` to ignore duplicates."""
