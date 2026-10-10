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
| Frontend lint, types, translations and unit tests | `cd frontend && pnpm install && pnpm lint && pnpm typecheck && pnpm check:messages && pnpm test` | Nothing running |
| Smoke test | `./e2e_tests/smoke.sh` | The running stack |
| Integration tests | `./scripts/integration.sh` | The running stack |
| Signed-out pages | `./e2e_tests/pages.sh` | The running stack |
| Signed-in pages | `./e2e_tests/signed-in.sh` | The running stack |
| Translations | `cd frontend && pnpm check:messages` | Nothing running |
| End-to-end | `python3 e2e_tests/flow.py` | `OPENAI_API_KEY` |
| AI apps over MCP | `python3 e2e_tests/mcp.py` | The running stack |
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

# Frontend: lint, types, translations, and unit tests of the pure helpers (frontend/tests, vitest)
cd frontend && pnpm install && pnpm lint && pnpm typecheck && pnpm check:messages && pnpm test
```

## Integration tests

Each service's `tests/integration` runs against the running stack's real Postgres and Redis, in a `<service>_test` database created and dropped for the run.

```bash
./scripts/integration.sh            # or: ./scripts/integration.sh rounds library
```

## The assistant's OpenAPI snapshots

The assistant builds its tools from snapshots of the other services' OpenAPI descriptions in `services/assistant/app/openapi/`. After changing a route of companies, billing, library, notifications, ats, api or rounds, refresh them with the stack running and commit the result; CI's stack job runs the script and fails when a snapshot differs.

```bash
./scripts/assistant-openapi.sh
```

## Smoke test

A smoke test against a running stack:

```bash
./e2e_tests/smoke.sh
```

## Browser tests of the signed-out pages

Playwright tests of the signed-out pages, on desktop and phone sizes, in Playwright's Docker image. The pages (`pages.spec.ts`): home, companies, pricing (also in German and Japanese), terms, privacy, documents, FAQ, about, contact, practice, skills tests by role, and the articles (pre-employment testing, AI interviews, a comparison, a guide and their hubs). It also checks that the sign-in dialog offers its two email boxes, unticked.

They check:

- no console errors,
- no sideways scroll,
- the same page width everywhere,
- the footer at the end,
- lowercase titles (articles keep their capitals).

Other specs check the home page's sections: the advantages' titles beside their icons in every language (`advantages.spec.ts`), the ATSs, Slack, the API and MCP with a point each for the ATS, the API and MCP (`ats.spec.ts`), the catalog's prices and free candidates on the home and pricing pages (`pricing.spec.ts`), the chat apps a report can be shared to (`reports.spec.ts`), smooth scrolling and back to top (`scroll.spec.ts`), and the API docs (`api-docs.spec.ts`). `news.spec.ts` checks the news page in English and German whatever posts exist: indexable, its title, description, canonical and hreflang addresses (x-default too), link-preview picture, `Blog` structured data, the RSS link in its head and its RSS icon; the RSS feed in both languages (content type, channel, items linking to the page); the sitemap listing the page but not the feed; and the footer's news link. `connect.spec.ts` checks the AI app consent page signed out: without a request it says the link expired, with one it asks to sign in first (naming the app when the API does), and it isn't indexed. `unsubscribe.spec.ts` checks the unsubscribe page: an invalid link says so, the page isn't indexed, and a candidate's link to a made-up company changes nothing until "Confirm". It signs that link with `EMAIL_LINK_SECRET`, which `pages.sh` passes from `.env` without printing it; each run leaves its made-up companies' opt-outs in the local notifications database.

`seo.spec.ts` checks language addresses and hreflang, titles, structured data, the sitemap, robots.txt, noindex on private pages and thin template pages, links and levels on a template's page in its language, redirects and the footer. `metadata.spec.ts` checks page descriptions, the compare hub's title, FAQ and article data, practice breadcrumbs, the direction of right-to-left template text, the preview picture's noindex and the footer's menu.

Tests that need a template never use the platform's own: each adds its own throwaway templates straight into the library database (`helpers/templates.ts`: a unique title and readable address, topics with subtopics and private and revealed questions; at least 3 topics makes one indexable, fewer doesn't), checks only those, and deletes them when it ends. `pages.sh` mounts `.env` read-only for `POSTGRES_PASSWORD`, read without printing it.

```bash
./e2e_tests/pages.sh
```

Extra arguments go to Playwright, for example `--workers=2` when the dev server is slow to compile.

## Browser tests of the signed-in pages

Playwright tests of the signed-in pages, in the same Docker image, against the running stack.

**Signing in.** Users sign in through "Continue with Google" and the Firebase Auth emulator's own sign-in page (local only), optionally ticking the sign-in's email boxes first (`signInAs(email, { noUpdates, promotions })`). The superadmin is the first address in `SUPERADMIN_EMAILS`.

**Test data.** Every test makes throwaway users, companies and interviews. Interviews are made from local templates: no OpenAI. The owner spec adds and deletes its own throwaway templates in the library database.

**What they cover:**

- a company owner making an interview from a template and inviting a candidate,
- a candidate taking an interview,
- the team and a viewer,
- verification,
- the admin zone's pass rates, stats, pause and maintenance mode (turned off again afterwards),
- the admin zone's news tab: the tabs' order, a post written in the dialog (the characters left, an over-long text refused by the API's message), shown in the tab and on the news page with its blue dot and date, edited with the pencil and deleted with the bin after confirming. Its posts are deleted at the end, even when it fails,
- the admin zone's emails tab: finding an address in another case, turning off all its account's optional emails (still off after a reload), stopping and resuming one inviting company's emails, and "not found" for anyone else,
- the candidates' PDF report,
- a practice result leading to a company's test,
- an interview's settings tab,
- API keys and web hooks,
- each ATS: Workable's linked jobs, and connecting Greenhouse (with who connected it under its title), Teamtailor, Recruitee and Breezy HR,
- Slack,
- the MCP server: its row and Instructions (the server's address, Claude's and ChatGPT's steps, opening on the dialog itself with Close outside the scrolling body, full height on phones), the connected AI apps (saved straight into the assistant database and deleted at the end) and disconnecting them, and the consent page signed in (an expired request, and a request answered in the browser, denied),
- the integrations pages on a phone: small logos beside the names with the buttons under them, the pages' buttons under their titles, Reconnect on its own line, the linked jobs, and full-height Instructions,
- the automatic top-up,
- an interview whose generation failed,
- email settings: the defaults, each kind saved as it changes, the activity digest's box (all, none, some), and what the sign-in's email boxes turn on, at a first sign-in and a later one,
- unsubscribing: a user's activity digest link turns its four kinds off in Settings, and after a candidate's "Don't email me for <company>" link, the company's next invite to that address shows as undelivered. Links are signed with `EMAIL_LINK_SECRET` from `.env`.

**Cleanup.** After every run, `teardown.ts` deletes every throwaway account, and so their companies and data, leftovers of stopped runs included. It fails if any is left.

Screenshots land in `e2e_tests/signed-in/test-results/screenshots`.

```bash
./e2e_tests/signed-in.sh            # or: ./e2e_tests/signed-in.sh specs/b-candidate.spec.ts
```

## Translations

Every language has exactly the keys of `en.json`, with the same arguments and rich-text tags, valid ICU syntax and an `other` form in every plural. In a language whose `one` form also covers other numbers (Filipino's 3, French's 0, Russian's 21), a plural that shows the number uses `=1` for exactly one, so 3 never reads as "your first one". CI runs it in the frontend job.

```bash
cd frontend && pnpm check:messages     # or name languages: pnpm check:messages de fr
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

## AI apps over MCP

`e2e_tests/mcp.py` connects an app to the running stack through the gateway, as Claude or ChatGPT would: it registers itself without a secret, is allowed on the consent page's API with a throwaway emulator user's token, exchanges the code with PKCE (a wrong verifier and a second exchange are refused), lists the tools (without the account's and a company's deletion), calls `get_me`, `create_company` and `list_companies` as the user, refreshes (the old tokens stop working), revokes, and has the user disconnect a second app. The account is deleted at the end, with its company and connections. No OpenAI; CI runs it after the integration tests. Standard library only:

```bash
python3 e2e_tests/mcp.py
```

The assistant's integration tests also connect an app in-process with the MCP SDK's own OAuth client (`tests/integration/test_mcp.py`).

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

CI runs all of these except the end-to-end test, which needs an OpenAI key, and the load tests, but only for what changed.

- A service counts as changed when its folder or `packages/common` changed; the frontend, when `frontend/` did. A change to `ci.yml` or `.python-version` counts as everything.
- A pull request compares with its base. `main` compares with the last commit CI passed on, so a failed run's changes are tested and built by the next one.
- Each changed part's unit tests run and its production image is built. A changed frontend also gets lint, types and the translations check (`pnpm check:messages`). On `main`, an unchanged part's image is the last passing commit's, tagged with the new commit too.
- Ruff runs on every change.
- It starts the whole stack for the smoke, integration, MCP, page and signed-in tests when any part changed, or `e2e_tests/`, `gateway/`, `database/`, `firebase/`, `scripts/`, `compose/` or `docker-compose.yml` did. A change to docs alone skips it.
- Its stack has no templates, so before the signed-in tests it adds a small English one (`e2e_tests/signed-in/seed/template.py`, no OpenAI).
- Its superadmin is a CI-only emulator account.
- On failure, the screenshots and traces are kept as the run's `signed-in-test-results` artifact.

When CI runs, and how releases follow it, is in [Deployment](deployment.md#cicd).
