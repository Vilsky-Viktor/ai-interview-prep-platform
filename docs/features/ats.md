# ATS integrations

A company can connect its applicant tracking system (ATS): Workable, Greenhouse, Teamtailor or Recruitee. Candidates the company moves into a chosen stage in the ATS get the prepza invite, and their results go back to the ATS.

- [Connecting an ATS](#connecting-an-ats)
- [Linking a job](#linking-a-job)
- [The ATS pages](#the-ats-pages)
- [Candidates from Workable](#candidates-from-workable)
- [Candidates from Greenhouse](#candidates-from-greenhouse)
- [Candidates from Teamtailor](#candidates-from-teamtailor)
- [Candidates from Recruitee](#candidates-from-recruitee)
- [Results back to the ATS](#results-back-to-the-ats)
- [How it's built](#how-its-built)

## Connecting an ATS

On a company's **ATS** tab, an owner or admin connects an ATS with its key:

| ATS | What to paste | Permissions |
|---|---|---|
| Workable | Its address and an API access token | The scopes `r_jobs`, `r_candidates` and `w_candidates` |
| Greenhouse | A Harvest V3 (OAuth) API credential's client ID and secret | The Jobs, Job Posts, Job Interview Stages and Notes endpoints |
| Teamtailor | An API key (Settings → Integrations → API keys) | Admin permission, Read/Write |
| Recruitee | Its address and a personal API token (Settings → Apps and plugins → Personal API tokens) | The token acts as the person who made it: an admin who sees every job |

- prepza checks the key with one read before saving it. A Teamtailor key is tried in each of Teamtailor's regions (EU, North America, Asia-Pacific) until one accepts it; the connection keeps that region.
- The key is saved encrypted with `ATS_ENCRYPTION_KEY`, the ats service's Fernet key. An empty key turns integrations off.
- prepza never shows the key again.
- Disconnecting deletes the key and the linked jobs at once.
- A key the ATS stops accepting marks the connection for reconnecting.

## Linking a job

**Link a job** links one of the ATS's jobs, and one of its stages, to an interview. The interview is either:

- an existing one,
- or a new interview made from the job's text in the ATS. The company checks and edits the text first, then reviews its topics as usual.

## The ATS pages

- The ATS tab lists the ATSs, with a "connected" tag once connected.
- Each ATS opens its own page: `/companies/<id>/integrations/<workable, greenhouse, teamtailor or recruitee>`. Before it's connected, the page says so in place of the linked jobs.
- The page lists its linked jobs. For each job:
  - how many of its candidates were invited (an icon and the number),
  - how many are waiting or weren't invited, above **Invite again**, which tries that job's again,
  - **Unlink**, after a confirmation.
- Each ATS has one **Instructions** button, on its row and its page. Its dialog holds everything to know: the candidate flow, starting with a stage just for prepza, and, for a connected Greenhouse, Teamtailor or Recruitee, the web hook to set up (owners and admins only). The dialog opens by itself right after connecting either of them.
- Every member sees these pages; viewers change nothing.

## Candidates from Workable

**Subscription.** Linking a job subscribes to Workable's `candidate_moved` events for its stage, at an address of its own: `/api/ats/webhooks/workable/<link id>`, built from `SITE_URL`. Unlinking or disconnecting cancels it.

**Signature.** An event counts only when its `X-Workable-Signature` is the HMAC-SHA256 of the body with the account's token.

**Inviting once.**

- The candidate is saved once per Workable candidate and interview (a unique key).
- It is then claimed in one update before the invite, so a repeated or simultaneous event invites once.
- An invite cut off midway can be claimed again after 10 minutes, by **Invite again**, a new event or the ats service's daily `recover` job.

**The invite** is the usual one. Companies sends it as if whoever connected Workable sent it: their limits, the company's credits, the pause.

- A candidate for an interview still being made waits, and is invited once it's ready (`interview.ready`).
- A candidate refused (credits, limits, the pause) is kept as not invited, and owners and admins get an `ats_not_invited` notification.

**Retention.** The saved candidates, with their emails, are deleted:

- after 365 days, by the same daily job,
- with their interview (`interview.deleted`),
- with their company (`company.deleted`),
- with the candidate's account. Account deletion and export include them.

## Candidates from Greenhouse

Greenhouse's API can't set up web hooks, so the company does it once in Greenhouse:

1. Go to Configure → Dev Center → Web Hooks.
2. Add the event "Candidate or Prospect Stage Change".
3. Paste the address and secret key the Instructions dialog shows.

- The address is the connection's own: `/api/ats/webhooks/greenhouse/<connection id>`.
- The secret key is made at the first connect, and kept on reconnecting.
- An event counts only when its `Signature` header is `sha256 ` followed by the HMAC-SHA256 of the body with that key.
- A candidate whose application moved into a linked job's stage (matched by id or name) is saved and invited exactly as from Workable, as `<candidate id>:<application id>`.

## Candidates from Teamtailor

Teamtailor's web hooks are an add-on, set up by hand in Teamtailor too:

1. Turn on Webhooks in Teamtailor's Add-on feature center.
2. Go to Settings → Integrations → Webhooks and add one for the event `job_application.update`, with the address the Instructions dialog shows.
3. Teamtailor makes the web hook's signature key: paste it into the Instructions dialog and save it.

- The address is the connection's own: `/api/ats/webhooks/teamtailor/<connection id>`.
- The signature key is kept on reconnecting. Until it's saved, every event is refused.
- An event counts only when its `TT-Signature` header is base64 of `t=<timestamp>,v2=<hex>`, the HMAC-SHA256 of `<timestamp>.<body>` with that key.
- The event only says an application changed (`job_application.update` or `.create`), so ats reads the application from Teamtailor: its job, stage and candidate as they are now.
- A candidate whose application is in a linked job's stage is saved and invited exactly as from Workable, by their Teamtailor candidate id.

## Candidates from Recruitee

The company sets up Recruitee's web hook by hand too:

1. Go to Settings → Apps and plugins → Webhooks and add one for the event `candidate_moved`, with the address the Instructions dialog shows.
2. Recruitee shows the web hook's secret: paste it into the Instructions dialog and save it.

- The address is the connection's own: `/api/ats/webhooks/recruitee/<connection id>`.
- The secret is kept on reconnecting.
- Recruitee tests the web hook when it's created, before its secret can be saved: until the secret is saved, events are answered and ignored.
- An event counts only when its `X-Recruitee-Signature` is the HMAC-SHA256 hex digest of the body with that secret.
- A `candidate_moved` event of subtype `stage_changed` carries the candidate's emails, the job (offer) and the new stage: a candidate moved into a linked job's stage is saved and invited exactly as from Workable, by their Recruitee candidate id.

## Results back to the ATS

When such a candidate finishes, companies publishes `candidate.finished` (grade, passed, flagged), and ats writes a comment about them in the ATS, in English:

- their grade,
- whether they passed,
- any integrity flags,
- a link to their scorecard.

| ATS | Where it's written |
|---|---|
| Workable | As the Workable member of whoever connected it (or an admin) |
| Greenhouse | A note on the candidate's application |
| Teamtailor | A note on the candidate, as the Teamtailor user of whoever connected it (or an admin) |
| Recruitee | A note on the candidate, as the person whose token it is |

- It's sent once (`reported_at`).
- A failing ATS makes the event come again.
- A key the ATS refuses marks the connection for reconnecting.

## How it's built

- All of it is the `ats` service (`services/ats`, its own database).
- It asks companies who is a member or editor, the interviews' titles, and to send invites.
- Each ATS's API is one client module (`app/integrations/workable.py`, `greenhouse.py`, `teamtailor.py`, `recruitee.py`) with the same functions. Each names the credentials it takes (`KEYS`), so a connection can keep others, like a web hook's secret key.
- `app/integrations/ats_clients.py` picks the module by provider. A new ATS adds its module there.
- The web hook handlers are in `app/services/ats_webhooks.py`, one per ATS.
- The webhook routes stay open in maintenance mode (see [Admin zone](admin-zone.md#maintenance-mode)).

See also [Architecture](../architecture.md) for the events ats consumes.
