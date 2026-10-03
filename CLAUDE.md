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
