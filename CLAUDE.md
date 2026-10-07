# Rules for this repo

1. **An empty line before each block and each return.** In generated code, put an
   empty line before every block statement (`if`, `for`, `while`, `try`, `with`,
   `switch`, nested functions and similar) and before every `return`. The exception
   is when that statement is the first line of its enclosing block; formatters
   remove a blank line there anyway.

2. **At most 300 lines per file.** When a file would grow past 300 lines, split it
   along the lines of rule 4 before adding more.

3. **Separate logical modules.** Keep each kind of code in its own file for
   readability and maintainability: schemas, models, types, helper functions,
   prompts and constants each get their own module. Don't mix them with the logic
   that uses them.

   Group modules into folders by kind. A service's `app/` folder holds only very
   general files: `main.py` (app setup: lifespan, routers, health check) and auth
   (`auth.py`, `service_auth.py`). `main.py` defines no route logic: routes live in
   `routers/`. Everything else goes in a subfolder, for example `routers/`,
   `models/`, `prompts/`, `helpers/` (pure helpers), `storage/` (databases, file
   storage, anything that persists data), `services/`, `integrations/` (external
   services) and `constants/`.

4. **Keep code as simple as possible.** Strictly avoid overcomplicating and
   overengineering: no abstractions, layers, options or generalizations that the
   current need doesn't require. Choose the most direct solution that works.

5. **No business logic on the frontend.** Rules, thresholds, limits and decisions
   (what passes, what counts as done, what is allowed) live in the backend services,
   which return the results. The frontend only displays data, collects input and
   sends it to the API.

6. **Every page has the same width.** A page's `<main>` is
   `mx-auto max-w-5xl px-6`, the width of the header, so content lines up with the
   logo and the menu on every page. No page is narrower or wider. Cards, forms and
   prompts inside a page may be narrower, but the page itself never is.

7. **One design language across the app.** Build a new page or piece of UI from the
   patterns the app already has, never from scratch. Before writing it, find the
   closest existing page and copy its layout, sizes and components: a list page looks
   like the companies list (a `text-3xl` title with its main action button on the
   right, rows in one `divide-y rounded-2xl border` list), a page that starts a test
   looks like the home page's start (a large title and the shared `DescriptionBox`),
   and a detail page looks like a company's test page. Reuse the shared components
   (`DescriptionBox`, `BackLink`, `PageHeader`, `EditableTitle`, `TopicQuestions`)
   instead of new look-alikes. Keep it minimal: no new colors, shadows, gradients or
   effects unless asked.

8. **Every piece of functionality is covered by tests, on the backend and the
   frontend.** New or changed behaviour ships with its tests in the same change:
   unit tests for logic (`services/<svc>/tests/unit`, `frontend/tests`), integration
   tests for anything that touches the database, Redis or another service
   (`services/<svc>/tests/integration`, run with `scripts/integration.sh`), and a
   browser test for every user-facing flow or screen (`e2e_tests/pages` signed out,
   `e2e_tests/signed-in` signed in). A bug fix adds a test that fails without it.
   Run the affected suites before calling the work done.

9. **READMEs stay current.** When a change affects anything a README describes
   (features, behaviour, setup, settings, commands, tests, deployment), update that
   README in the same change: the root `README.md`, `infra/README.md` and any README
   next to the changed code. Describe what is true now, not the change itself.

10. **No duplicated functionality or logic.** Before writing something, look for code
    that already does it and reuse it. Logic repeated across services goes into a
    shared library (`packages/common`, `prepza_common`); repeated frontend logic into
    one helper or component. A logically grouped domain that several services keep
    reimplementing gets its own service.

11. **Check every event-driven flow end to end.** When code publishes, consumes or
    schedules events (outbox, Pub/Sub, webhooks, scheduled jobs), trace the whole flow
    from producer to every consumer, and check it for the common issues: idempotency
    (a redelivered or duplicate event changes nothing twice), race conditions
    (concurrent handlers, out-of-order events, read-then-write without a lock or a
    unique constraint), rate limits (of external APIs and of our own services, with
    retries and backoff), and failures (what is retried, what is lost, what a handler
    does halfway through).
