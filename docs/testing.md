# Testing

prepza has unit, integration, browser, end-to-end and load tests, plus offline evals of model quality. CI runs most of them on every pull request (see [CI](#ci)).

- [Test suites](#test-suites)
- [Unit tests and lint](#unit-tests-and-lint)
- [Integration tests](#integration-tests)
- [Smoke test](#smoke-test)
- [Browser tests of the signed-out pages](#browser-tests-of-the-signed-out-pages)
- [Browser tests of the signed-in pages](#browser-tests-of-the-signed-in-pages)
- [Translations](#translations)
- [End-to-end test](#end-to-end-test)
- [Load tests](#load-tests)
- [Model and prompt evals](#model-and-prompt-evals)
- [CI](#ci)

## Test suites

| Suite | Command | Needs |
|---|---|---|
| Python unit tests | `cd services/rounds && uv sync && uv run pytest` | Nothing running |
| Python lint and format | `uvx ruff@0.16.10 check ...` (below) | Nothing running |
| Frontend lint, types and unit tests | `cd frontend && pnpm install && pnpm lint && pnpm typecheck && pnpm test` | Nothing running |
| Smoke test | `./e2e_tests/smoke.sh` | The running stack |
| Integration tests | `./scripts/integration.sh` | The running stack |
| Signed-out pages | `./e2e_tests/pages.sh` | The running stack |
| Signed-in pages | `./e2e_tests/signed-in.sh` | The running stack |
| Translations | `docker compose exec frontend pnpm check:messages` | The running stack |
| End-to-end | `python3 e2e_tests/flow.py` | `OPENAI_API_KEY` |
| Load tests | `./e2e_tests/load.sh candidates` | The local stack only |

## Unit tests and lint

Each Python service (and `packages/common`) keeps:

- `tests/unit`: fakes, no services needed,
- `tests/integration`: real Postgres and Redis,
- the shared setup in `tests/conftest.py`.

```bash
# Unit tests of each Python service, and of the shared package (packages/common)
cd services/rounds && uv sync && uv run pytest

# Python lint and format, as CI runs them (ruff's version is pinned in CI)
uvx ruff@0.16.10 check services packages evals && uvx ruff@0.16.10 format --check services packages evals

# Frontend: lint, types, and unit tests of the pure helpers (frontend/tests, vitest)
cd frontend && pnpm install && pnpm lint && pnpm typecheck && pnpm test
```

## Integration tests

Each service's `tests/integration` runs against the running stack's real Postgres and Redis, in a `<service>_test` database created and dropped for the run.

```bash
./scripts/integration.sh            # or: ./scripts/integration.sh rounds library
```

## Smoke test

A smoke test against a running stack:

```bash
./e2e_tests/smoke.sh
```

## Browser tests of the signed-out pages

Playwright tests of the signed-out pages, on desktop and phone sizes, in Playwright's Docker image. The pages: home, companies, pricing, terms, privacy, docs, FAQ, about, contact, practice.

They check:

- no console errors,
- no sideways scroll,
- the same page width everywhere,
- the footer at the end,
- lowercase titles (articles keep their capitals).

`seo.spec.ts` checks language addresses and hreflang, titles, structured data, the sitemap, robots.txt, noindex on private pages, redirects and the footer.

```bash
./e2e_tests/pages.sh
```

Extra arguments go to Playwright, for example `--workers=2` when the dev server is slow to compile.

## Browser tests of the signed-in pages

Playwright tests of the signed-in pages, in the same Docker image, against the running stack.

**Signing in.** Users sign in through "Continue with Google" and the Firebase Auth emulator's own sign-in page (local only). The superadmin is the first address in `SUPERADMIN_EMAILS`.

**Test data.** Every test makes throwaway users, companies and interviews. Interviews are made from local templates: no OpenAI. The owner spec adds and deletes its own throwaway templates in the library database.

**What they cover:**

- a company owner,
- a candidate taking an interview,
- the team and a viewer,
- verification,
- the admin zone's pass rates, stats, pause and maintenance mode (turned off again afterwards),
- the candidates' PDF report.

**Cleanup.** After every run, `teardown.ts` deletes every throwaway account, and so their companies and data, leftovers of stopped runs included. It fails if any is left.

Screenshots land in `e2e_tests/signed-in/test-results/screenshots`.

```bash
./e2e_tests/signed-in.sh            # or: ./e2e_tests/signed-in.sh specs/b-candidate.spec.ts
```

## Translations

Every language has every key of `en.json`, with the same placeholders and plurals:

```bash
docker compose exec frontend pnpm check:messages
```

## End-to-end test

An end-to-end run with a real generation. It needs `OPENAI_API_KEY` and costs a few cents and a few minutes.

1. A company generates an interview and invites a candidate.
2. The candidate takes it from the invite link.
3. The company sees the scorecard and pays for that candidate.

Its accounts, company and data are deleted at the end, however the run ends.

```bash
python3 e2e_tests/flow.py
```

## Load tests

Load tests with k6, in its Docker image, against the local stack only: never production, and not in CI.

- Scenarios: many candidates taking a test, owners on the dashboard, the public pages.
- Throwaway users, companies and tests from local templates, all deleted and counted afterwards.
- Settings, thresholds and results are in [e2e_tests/load/README.md](../e2e_tests/load/README.md).

```bash
./e2e_tests/load.sh candidates      # or: dashboard, public; VUS=20 ITERATIONS=2 ./e2e_tests/load.sh candidates
```

## Model and prompt evals

Model and prompt quality is tested offline with the prepared datasets, judge prompts and metrics in [evals/](../evals/README.md).

## CI

CI runs all of these except the end-to-end test, which needs an OpenAI key.

- It also builds every production image.
- It starts the whole stack for the smoke, integration, page and signed-in tests.
- Its stack has no templates, so before the signed-in tests it adds a small English one (`e2e_tests/signed-in/seed/template.py`, no OpenAI).
- Its superadmin is a CI-only emulator account.
- On failure, the screenshots and traces are kept as the run's `signed-in-test-results` artifact.

When CI runs, and how releases follow it, is in [Deployment](deployment.md#cicd).
