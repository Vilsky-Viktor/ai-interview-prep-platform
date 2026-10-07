# Development

How to run prepza locally, the settings it reads, and the everyday commands.

- [Running locally](#running-locally)
- [Local addresses](#local-addresses)
- [Settings](#settings)
- [Databases and migrations](#databases-and-migrations)
- [The local stack](#the-local-stack)
- [Everyday commands](#everyday-commands)
- [Project conventions](#project-conventions)

## Running locally

Requirements: Docker with Compose, and an OpenAI API key.

```bash
cp .env.example .env
# Set OPENAI_API_KEY in .env.
docker compose up --build
```

## Local addresses

| URL | What |
|---|---|
| http://localhost:8090 | The app |
| http://localhost:4100 | Firebase Auth emulator UI (sign-in creates fake accounts here) |
| http://localhost:8125 | Mailpit: every email sent locally, when `RESEND_API_KEY` is empty |

Without `RESEND_API_KEY`, emails go to Mailpit instead of real inboxes. To send real ones, see [Notifications and emails](features/notifications.md#sending-real-emails).

## Settings

Settings live in `.env`, copied from [`.env.example`](../.env.example). Apart from `OPENAI_API_KEY`, the values work locally as they are:

| Setting | What it is |
|---|---|
| `POSTGRES_PASSWORD` | The local Postgres password |
| `SERVICE_SECRET` | Signs calls between services; at least 32 characters |
| `FIREBASE_PROJECT_ID` | A `demo-` project, which lets the services (`FIREBASE_AUTH_EMULATOR_HOST`) and the browser (`NEXT_PUBLIC_FIREBASE_AUTH_EMULATOR_URL`) use the Auth emulator |

Settings are described with the feature they shape:

| Topic | Page |
|---|---|
| Generation, models, rate limits, LangSmith | [Generation and question quality](generation.md#generation-settings) |
| Paddle | [Credits and payments](features/billing.md#setting-up-paddle) |
| Resend, Mailpit, `SITE_URL`, `CONTACT_EMAIL` | [Notifications and emails](features/notifications.md#emails) |
| Email limits | [Candidates](features/candidates.md#email-limits) |
| Help chat and contact form limits | [Public site](features/site.md#faq-and-help-chat) |
| `ATS_ENCRYPTION_KEY` | [ATS integrations](features/ats.md#connecting-an-ats) |
| `SUPERADMIN_EMAILS` | [Admin zone](features/admin-zone.md) |
| `ANALYTICS_SALT` | [Architecture](architecture.md#funnel-events) |
| Sentry, search engine verification | [Deployment](deployment.md#error-reporting) and [Public site](features/site.md#search-engines) |

## Databases and migrations

- Each API's database migrations run once, in a short-lived `*-migrate` container, before the API starts.
- A Postgres volume made before a database was added needs that database created once, for example:

  ```bash
  docker compose exec postgres createdb -U prepza ats
  ```

- Docker marks an API healthy only when `/ready` confirms its database answers. Redis isn't checked, so a Redis outage doesn't stop a service from starting.

## The local stack

[`docker-compose.yml`](../docker-compose.yml) is for local development only. It:

- builds each image's `dev` target,
- mounts the source, so servers reload on change,
- enables the Firebase emulator,
- runs Google's Pub/Sub emulator and a small `scheduler` container (see [Architecture](architecture.md#background-work)).

The frontend keeps its `node_modules` in a volume. After a frontend dependency changes:

1. run `docker compose build frontend`,
2. remove the `prepza_frontend-modules` volume,
3. start again.

Paddle and Resend reach local webhooks only through a tunnel, for example `cloudflared tunnel --url http://localhost:8090`.

## Everyday commands

```bash
# After changing an API: regenerate the frontend's API types (needs the stack running)
cd frontend && pnpm api-types

# Give template topics without an embedding one
docker compose exec generation uv run --no-sync python -m app.jobs.embed_templates

# Rebuild the documents for companies after changing their sources
./scripts/documents/build.sh   # needs uv (for pandoc) and Docker (Chromium prints the PDFs)
```

Tests, lint and the translations check are in [Testing](testing.md).

## Project conventions

See [CLAUDE.md](../CLAUDE.md). In short:

- separate modules for schemas, models, prompts, helpers and constants,
- `app/main.py` only wires the app,
- at most 300 lines per file,
- the simplest solution that works,
- no business logic on the frontend: rules, thresholds and decisions live in the services.
