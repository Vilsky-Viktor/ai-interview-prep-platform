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
docker build --target prod -f services/library/Dockerfile -t prepza-library .   # also generation, rounds, companies, billing, notifications, ats
docker build --target prod -t prepza-frontend \
  --build-arg NEXT_PUBLIC_FIREBASE_API_KEY=... --build-arg NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=... \
  --build-arg NEXT_PUBLIC_FIREBASE_PROJECT_ID=... frontend
```

Never set `FIREBASE_AUTH_EMULATOR_HOST` in production.

Terraform passes none of the generation settings to Google Cloud, so production runs on their defaults (see [Generation settings](generation.md#generation-settings)).

## Migrations

- Run each API's migrations once before it starts: `uv run --no-sync alembic upgrade head`.
- Every API but the frontend has them, notifications included.
- Migrations only go forward, so keep them additive for rollbacks to stay safe.

## Error reporting

Errors go to Sentry when its DSN is set; empty, nothing is sent.

| Setting | What it sets |
|---|---|
| `SENTRY_DSN` | The DSN for the backend services |
| `NEXT_PUBLIC_SENTRY_DSN` | The DSN for the frontend, a build argument |
| `SENTRY_ENVIRONMENT` | The environment's name (`development` locally) |
| `SENTRY_TRACES_SAMPLE_RATE` | The share of requests traced (default 0.1) |
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
