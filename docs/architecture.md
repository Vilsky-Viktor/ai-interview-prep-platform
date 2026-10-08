# Architecture

prepza is a set of Python API services behind an nginx gateway, with a Next.js frontend. They talk through signed internal calls and through events on one Pub/Sub topic.

- [Overview](#overview)
- [Services](#services)
- [How services work together](#how-services-work-together)
- [Background work](#background-work)
- [Events](#events)
- [Funnel events](#funnel-events)

## Overview

```mermaid
flowchart LR
    browser[Browser] --> gateway[nginx gateway]
    gateway --> frontend[Next.js frontend]
    gateway --> library
    gateway --> generation
    gateway --> rounds
    gateway --> companies
    gateway --> billing
    gateway --> ats
    gateway --> api
    platforms[Companies' platforms] -- API keys --> gateway
    paddle[Paddle] -- payment webhooks --> billing
    atss[Workable / Greenhouse / Teamtailor / Recruitee / Breezy HR] -- candidate webhooks --> ats

    generation -- jobs via Cloud Tasks --> worker[generation worker]
    scheduler[Cloud Scheduler] -- sweeps, retention --> worker
    worker -- saves sets, reuses questions --> library
    library -- re-generate, verify --> generation
    rounds -- questions --> library
    companies --> generation
    companies --> library
    companies --> rounds
    companies -- candidate credits --> billing
    ats -- members, interviews, invites --> companies
    api -- members, interviews, candidates, invites --> companies
    api -- signed web hooks --> platforms

    rounds -- answer.recorded / session.scored / interview.finished / results.rescored --> pubsub[(Pub/Sub topic: events)]
    worker -- generation.completed / cancelled --> pubsub
    companies -- candidate.invited / reminded, report.shared, company.deleted --> pubsub
    companies -- candidate.finished, interview.ready / deleted --> pubsub
    rounds -- contact.sent --> pubsub
    billing -- credits.added --> pubsub
    library & companies & billing & ats -- notification.requested --> pubsub
    pubsub -- push --> library
    pubsub -- push --> companies
    pubsub -- push --> ats
    pubsub -- push --> api
    pubsub -- push --> notifications -- email --> smtp[Resend / mailpit]
    pubsub -- funnel.* events --> bigquery[(BigQuery: funnel_events)]
```

## Services

| Service | Responsibility |
|---|---|
| `library` | Question sets (topics and questions) of interviews and templates: the template catalog, the question bank's stages, revealed questions for practice; candidates' votes and reports, question quality flags and reuse; also account deletion and export across services |
| `generation` | The generation pipeline (LangGraph), run by its worker (`app/worker_main.py`) as Cloud Tasks jobs; topic review, re-generating single questions, the question verifier, and scheduled sweeps |
| `rounds` | Candidates' interview sessions and their answers, free practice rounds; the FAQ, the help chat, the legal texts and the contact form (`/help/...`) |
| `companies` | Companies (unique names, logos, verification), members (owner, admins, viewers), interviews, candidate invites (one by one, in bulk, through a shareable link, with reminders), reports |
| `billing` | Companies' credit wallets (holds and charges), welcome credits, referrals, Paddle top-ups, automatic top-ups, refunds and chargebacks (webhooks); companies sets a candidate's credits aside and charges them through it |
| `notifications` | Receives domain events pushed by Pub/Sub and sends emails through Resend (mailpit without a key): candidate invites and reminders, emailed PDF reports, and contact messages to prepza's inbox. Also the bell: stores the notifications other services ask for (`notification.requested`), removes a deleted company's (`company.deleted`), and streams them live to open tabs over server-sent events, through Redis pub/sub so every instance hears them. Posts a company's chosen notifications to its Slack channel too, through the channel's incoming web hook |
| `ats` | ATS integrations (Workable, Greenhouse, Teamtailor, Recruitee, Breezy HR): companies' encrypted ATS keys, linked jobs and the candidates the ATSs send (their webhooks); invites them through companies and writes their results back to the ATS |
| `api` | The public API at `/api/v1/`: companies' API keys (as hashes, with their expiry), their web hooks (secrets encrypted) and deliveries; reads interviews and candidates and invites through companies, and sends a signed web hook when a candidate finishes |
| `frontend` | Next.js app; server-rendered pages call the API through the gateway |

What each service does for users is described in the feature pages, linked from the [README](../README.md#documentation). Generation is described in [Generation and question quality](generation.md).

## How services work together

- **Databases:** each service owns its own Postgres database.
- **Internal calls:** services call each other's `/internal/` endpoints with short-lived signed tokens. The gateway never exposes those routes.
- **Shared code:** code the API services share (sign-in, service tokens, logging, database and HTTP setup) lives in [`packages/common`](../packages/common/README.md), installed into each service from the repo. The API images are therefore built from the repo root.
- **Paging:** every list endpoint takes `offset` and `limit`, at most 100 per page.
- **Sign-in:** users sign in with Firebase Authentication. The local setup uses the Firebase emulator, so no Firebase project is needed.

## Background work

| Kind | In Google Cloud | Examples |
|---|---|---|
| Long jobs | Cloud Tasks that call the generation worker's `/internal/jobs/...` | A generation, a question check |
| Periodic work | Cloud Scheduler calling `/internal/schedules/...` | Stuck-generation sweeps, key-check batches, invite reminders and expiry, stalled ATS invites, retention |

- Google signs those calls, and Pub/Sub pushes, as one invoker service account, which each service checks.
- Locally there is no queue: the API calls the worker directly.
- Locally, a small `scheduler` container runs [`scripts/local/crontab`](../scripts/local/crontab).

## Events

Domain events go through an outbox, so a change never loses its event:

1. An event is saved in an `outbox` table, in the same transaction as the change it announces.
2. It is published right after. A request publishes only the events it saved, in one batch, with a 5-second timeout.
3. If that failed, a per-minute scheduled flush publishes it.

Refusals and duplicates:

- An event Pub/Sub refuses is counted in its row's `attempts`, and parked after 5 refusals, so it can't hold up the rest.
- Each event carries a stable `event_id` attribute (its outbox row id), so a consumer that gets it twice acts once. Notifications' emails and bell, library's statistics and companies' notifications track this through their `processed_events`.

Delivery:

- All events go to one Pub/Sub topic, `events`.
- It pushes each event to the `/internal/events` endpoint of library, companies, notifications, ats and api.
- In Google Cloud, each subscription carries only the types its consumer handles ([`infra/terraform/pubsub.tf`](../infra/terraform/pubsub.tf)).
- Locally, each consumer ignores events that aren't its own.
- Locally, Google's Pub/Sub emulator runs in docker-compose, and [`scripts/local/pubsub-setup.sh`](../scripts/local/pubsub-setup.sh) creates the topic and subscriptions.

The event types each service publishes are in the [overview diagram](#overview).

## Funnel events

The services also publish small `funnel.*` events (signed up, company created, candidate invited, results viewed, topped up and so on) to the same topic.

- A filtered BigQuery subscription stores them for the dashboards (`funnel_events`).
- The push subscriptions skip them.
- They carry counts and a salted hash of the user id (`ANALYTICS_SALT`), never emails or text.
- Locally, nothing stores them.
