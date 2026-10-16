---
name: verify
description: Choose and run the right test suites for a change (unit, database, browser, end to end) and handle the slow local dev server. Use before calling any change done.
---

# Verify a change

Rule 8: every change ships with its tests, and the affected suites run before it's done.
For a change a user sees, only after the user has approved the UI (rule 14): a test run slows
the local site so much that the user can't review it meanwhile.

## Which suites

| What changed | Run |
|---|---|
| A service's code | `cd services/<svc> && uv run pytest -q tests/unit` |
| Anything touching the database, Redis or another service | `scripts/integration.sh <svc>` |
| `packages/common` | `cd packages/common && uv run pytest -q tests/unit`, plus every service that uses the changed code |
| Python style | `uvx ruff@0.16.10 check --fix services packages && uvx ruff@0.16.10 format services packages` |
| Frontend code | `cd frontend && npx tsc --noEmit -p . && npx eslint <files> && pnpm test` |
| Frontend texts | `cd frontend && node scripts/check-messages.mjs` |
| A signed-in screen or flow | `e2e_tests/signed-in.sh specs/<name>.spec.ts --retries=0` |
| A public page | `e2e_tests/pages.sh <name>.spec.ts --workers=1` |
| The whole hiring flow | `python3 e2e_tests/flow.py` (a real generation: a few cents of OpenAI) |
| Terraform | `docker run --rm -v "$PWD/infra/terraform:/tf" -w /tf hashicorp/terraform fmt -check` / `validate` |

Run a unit test's whole suite, not one file: fakes in other files often depend on what changed.

## What a test checks

Behaviour and data, never wording (CLAUDE.md rule 8). No assertions on, and no locators by,
placeholders, headings' copy, button labels, tooltips or messages: copy changes freely and such a
check proves nothing. Find elements by role and position (`getByRole("main").getByRole("textbox")`,
a dialog's `spinbutton`, `.first()`), or by a `data-testid` added to the component when nothing
else tells them apart. Assert what was found, saved, refused or changed, and the data the test
made (its company's name, an email, a note). An accessible name is checked only where it is the
feature itself (an icon button's screen-reader label).

## The local dev server

The frontend is a Next.js dev server and compiles pages on first visit, so browser tests can
time out on cold pages. These are not code failures:

- Warm the pages a test opens first: `curl -s -m 180 -o /dev/null http://127.0.0.1:8090/<path>`.
- A `page.goto` timeout, `ERR_ABORTED`, a 502 or a 90-second `visit` timeout: run the test again.
- A failure at a different step on each run is timing; the same failure twice is real.
- When the frontend container passes about 6 GB (`docker stats --no-stream`), restart it:
  `/opt/homebrew/bin/docker-compose restart frontend`, then warm pages again.
- A run with no output for many minutes may be stuck on a colima `chmod` of `test-results`:
  find it with `ps aux | grep signed-in.sh`, kill it, and run again.
- `pages.sh -g "a|b"` breaks on the pipe: run each name separately.

## Report

Say which suites ran and their counts, and name anything not checked (for example a path only
a production build can show).
