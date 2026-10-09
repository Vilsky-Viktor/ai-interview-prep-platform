# Public API

A company can connect its own platform to prepza through the public API: list its interviews, invite candidates, read their results, and hear when a candidate finishes through a web hook. The reference is on the site at `/api-docs` (linked in the footer), read from the API's own OpenAPI description, so it always matches it.

- [Keys](#keys)
- [The API](#the-api)
- [Web hooks](#web-hooks)
- [The API page](#the-api-page)
- [How it's built](#how-its-built)
- [Settings](#settings)

## Keys

- An owner or admin makes a key on the company's **Integrations** tab → **API** → **API keys** → **New key**: a name, and when it expires (in 1, 3, 6 or 12 months, or never; "never" shows a warning that a leaked key stays usable until deleted).
- The key (`pz_...`) is shown once. prepza keeps only its SHA-256 hash and its first characters, to tell keys apart.
- A key belongs to one company and acts as the member who made it: invites go out under that member's email limits. It stops working when it expires, when it's deleted, or when that member is no longer an owner or admin there (`401`; the api service rechecks that at most once a minute per instance).
- A company can have up to 10 keys, and all its keys together can make 60 requests a minute (`429` over it). Keys and web hooks are added one at a time per company (a Postgres advisory lock), so two added at once can't pass the limit. If Redis is down, requests go through without the limit rather than failing (logged).
- Deleting the company deletes its keys and web hooks; deleting an account deletes the keys and web hooks that member made.

## The API

Everything is under `https://<domain>/api/v1`, with `Authorization: Bearer pz_...`:

| Route | What it does |
|---|---|
| `GET /interviews` | The company's interviews, newest first |
| `GET /interviews/{id}` | One interview |
| `GET /interviews/{id}/candidates` | Its candidates with progress, grade, pass, integrity signals and a link to their results, newest first |
| `GET /interviews/{id}/candidates/{candidate_id}` | One candidate |
| `POST /interviews/{id}/candidates` | Invites a candidate by email, with an optional name (or sends the invite again), as the key's maker; credits are set aside as in the app |

- Lists take `offset` and `limit` (up to 100).
- Companies' refusals pass through as they are: `402` without credits, `409` while the interview's questions are being made, `429` over the email limits, `503` while invites are paused, `404` for another company's interview.

## Web hooks

- An owner or admin adds up to 5 HTTPS addresses on the API page's **web hooks** tab. Like a key, a web hook works while whoever added it is still an owner or admin of the company; after that it gets nothing. An address must lead to the public internet: prepza refuses private, loopback and link-local addresses when it's added and again before each send, then connects to the very address it checked (with the host's name for TLS and the `Host` header), so a lookup that answers differently the second time can't lead the send elsewhere. It never follows redirects, and never logs a web hook's address, which can carry a secret.
- Each web hook gets a signing secret (`whsec_...`), shown once and stored encrypted with `API_ENCRYPTION_KEY`.
- When a candidate finishes (companies' `candidate.finished`), each web hook gets `POST {"id", "type": "candidate.finished", "data": {"interview", "candidate"}}`, the same objects the API returns, with `Prepza-Signature: t=<unix seconds>,v1=<hex HMAC-SHA256 of "<t>.<body>">`.
- When a finished candidate's grade changes because an answer key was corrected (companies' `candidate.rescored`, published only when the stored grade actually changed), each web hook gets the same body with `"type": "candidate.rescored"`, its own `id`, and the candidate as they are now; it's delivered and retried like `candidate.finished`. The candidate is read from companies at send time, so even two corrections arriving out of order both carry the current grade.
- Delivery: all of a company's web hooks are sent to at once, each with 10 seconds to answer `2xx`. A web hook that took the event is remembered (`webhook_deliveries`, for 30 days), so a redelivered event reaches only the ones that failed. An event can arrive more than once; its `id` stays the same, and receivers are told to ignore repeats by it. Two sends of one event at the same time (a redelivered event while the retry job sends it) aren't prevented: both may arrive.
- Retries: an event a web hook didn't take is kept for it (`webhook_retries`), and the Pub/Sub event is done, so one company's failing endpoint doesn't hold up events for everyone. The `webhook-retries` job (every 5 minutes) sends it again after 5 minutes, then twice as long each time, at most 6 hours apart; each run sends up to 25 at once, and two runs never send the same one. It's dropped when it gets there, when whoever added the web hook is no longer an owner or admin, or after 3 days of failing: then the web hook shows as failing (`failing` in the API page's list) until it takes an event again.
- A web hook whose secret can't be read, or whose address no longer leads to the public internet, is skipped. An address whose lookup fails counts as a failed send and is retried. A candidate or interview deleted since is told to nobody; if the companies service can't answer for now, the event fails and Pub/Sub retries it, and nothing has been sent yet.

## The API page

`/companies/<id>/integrations/api`, from the **API** row on the integrations tab (which shows how many keys and web hooks the company has):

- Two tabs, **API keys** and **web hooks**, each a list with its own button in the title row (**new key**, **add web hook**) for owners and admins, next to **api docs**.
- A key shows its first characters, when it was made, when it expires (or that it expired), and when it was last used (noted at most once a minute). Viewers see the lists without the buttons.

## How it's built

- The `api` service (`services/api`) owns the keys, web hooks, deliveries and retries in its own database. It has no business rules of its own: interviews, candidates and invites come from companies' internal routes (`/internal/companies/{id}/interviews/...` and `/internal/interviews/{id}/invites`).
- It's reached at `/api/v1/` (the gateway locally, the load balancer's `v1` path in Google Cloud). The management routes (`/api/v1/manage`, for the API page, signed in with Firebase) and the internal ones are left out of the public OpenAPI.
- It consumes `candidate.finished` and `candidate.rescored` (web hooks) and `company.deleted` (deletes the company's keys and web hooks).

## Settings

| Setting | What it does |
|---|---|
| `API_ENCRYPTION_KEY` | The Fernet key that encrypts web hooks' secrets. Empty: keys work, but web hooks can't be added ("Web hooks aren't set up yet") and none is sent. Keep it: a new key makes every web hook unreadable, so they have to be added again |
