# Deployment

Production runs on Google Cloud in `europe-west1`, set up by Terraform in [`infra/`](../infra/README.md). The infra README also has the one-time bootstrap steps, the GitHub setup for deploys and the restore drill.

- [Production images](#production-images)
- [Migrations](#migrations)
- [Error reporting](#error-reporting)
- [CI/CD](#cicd)
- [Releasing](#releasing)
- [Rolling back](#rolling-back)
- [Dependencies](#dependencies)

## Production images

Every app Dockerfile (on Alpine) has a `prod` target, with the code built in and no reload. The API images are built from the repo root, because they include `packages/common`:

```bash
docker build --target prod -f services/library/Dockerfile -t prepza-library .   # also generation, rounds, companies, billing, notifications, ats, api, assistant
docker build --target prod -t prepza-frontend \
  --build-arg NEXT_PUBLIC_FIREBASE_API_KEY=... --build-arg NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=... \
  --build-arg NEXT_PUBLIC_FIREBASE_PROJECT_ID=... frontend
```

Never set `FIREBASE_AUTH_EMULATOR_HOST` in production.

Terraform passes only one generation setting to Google Cloud, `DAILY_GENERATION_LIMIT` (its `daily_generation_limit` variable, default 200); production runs on the defaults of the others (see [Generation settings](generation.md#generation-settings) and [infra/README.md](../infra/README.md#notes)). The assistant runs on its defaults too (`ASSISTANT_MODEL`, `ASSISTANT_REASONING_EFFORT`, `ASSISTANT_RETENTION_DAYS`); its usage limits are constants in its code (see [The in-app assistant](features/assistant.md#limits)). It gets `SITE_URL` and `FIREBASE_WEB_API_KEY` (the `firebase_web_api_key` variable) for AI apps over MCP, whose endpoint and OAuth paths the load balancer sends to it at the site's root; its account needs to read Firebase accounts and sign as itself (`infra/terraform/iam.tf`, see [AI apps over MCP](features/mcp.md)).

## Migrations

- Run each API's migrations once before it starts: `uv run --no-sync alembic upgrade head`.
- Each of the 9 API services has them (library, generation, rounds, companies, billing, notifications, ats, api, assistant); the generation worker and the bell stream share generation's and notifications' databases. In Google Cloud, each runs as a `<service>-migrate` job, after the `db-roles` job that gives each service its own database user.
- Migrations only go forward, so keep them additive for rollbacks to stay safe.

## Error reporting

Errors go to Sentry when its DSN is set; empty, nothing is sent. Emails are scrubbed from every event, and URLs are cut to their host, so web hook addresses (which can carry secrets) never reach it.

| Setting | What it sets |
|---|---|
| `BACKEND_SENTRY_DSN` | The DSN for the backend services |
| `FRONTEND_SENTRY_DSN` | The DSN for the frontend, a build argument |
| `SENTRY_ENVIRONMENT` | The environment's name (`development` locally) |
| `SENTRY_TRACES_SAMPLE_RATE` | The share of requests traced (default 0.1) |
| `SENTRY_RELEASE` | The release events are tagged with: the commit, built into every image by CI (services read it at runtime; the frontend's Sentry plugin names it at build time) |
| `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT` | Passed to the frontend build, to see the original code in frontend stack traces |

Events carry user ids only, with emails scrubbed.

## CI/CD

| When | What runs |
|---|---|
| A push to a pull request | CI ([`ci.yml`](../.github/workflows/ci.yml)); a newer push cancels the run for the previous one |
| A merge to `main` | CI again on the merged code, then the production images are pushed, tagged with the commit: the changed ones are built, the others are the last passing commit's images with this commit's tag added. Nothing is deployed |
| A `v*` tag on such a commit | [`deploy.yml`](../.github/workflows/deploy.yml): checks the tag is on `main` and CI passed on it, tags that commit's images with the version (no rebuild), runs the migrations, deploys every service, smoke-tests the site and creates a GitHub release |
| Actions → Deploy → Run workflow with an earlier tag | Redeploys that version: a rollback. Migrations run only when **Run migrations** (`migrate`) is ticked |

What CI tests is in [Testing](testing.md#ci).

## Releasing

To release, tag the last commit of a push to `main` once CI has passed on it:

```bash
git tag v1.4.0 && git push origin v1.4.0
```

The one-time GitHub setup (tag protection, an optional approval for deploys) is in [infra/README.md](../infra/README.md#deploys).

## Rolling back

Run Actions → Deploy → Run workflow with an earlier tag. It redeploys that version. Migrations run only when **Run migrations** (`migrate`) is ticked.

## Dependencies

- Workflow actions are pinned by commit.
- Dockerfile base images are pinned by digest.
- Dependabot ([`.github/dependabot.yml`](../.github/dependabot.yml)) opens weekly pull requests to update them.
