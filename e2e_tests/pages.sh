#!/usr/bin/env bash
# Browser tests of the signed-out pages (e2e_tests/pages), in Playwright's Docker image, against
# the running stack: the browser opens SITE_URL, which Chromium resolves to the gateway on the
# stack's own network. Tests that need templates add their own straight into the library database
# (POSTGRES_PASSWORD from .env, mounted read-only) and delete them after, so the platform's own
# templates are never read or changed.
# Usage: e2e_tests/pages.sh [playwright args], e.g. --workers=2
set -euo pipefail

cd "$(dirname "$0")/.."

if docker compose version >/dev/null 2>&1; then
  compose=(docker compose)
else
  compose=(docker-compose)
fi

gateway="$("${compose[@]}" ps -q gateway)"
network="$(docker inspect -f '{{range $name, $_ := .NetworkSettings.Networks}}{{$name}}{{end}}' "$gateway")"

# The secret that signs emails' unsubscribe links, as notifications has it (compose's default when
# .env has none), passed by name so it's never printed or put on the command line.
EMAIL_LINK_SECRET="$(sed -n 's/^EMAIL_LINK_SECRET=//p' .env 2>/dev/null)"
export EMAIL_LINK_SECRET="${EMAIL_LINK_SECRET:-local-email-link-secret}"

docker run --rm --network "$network" \
  -v "$PWD/e2e_tests/pages:/tests" -w /tests \
  -v "$PWD/.env:/env/.env:ro" \
  -e EMAIL_LINK_SECRET \
  -e SITE_URL=http://localhost:8090 \
  -e HOST_RULES="MAP localhost:8090 gateway:80" \
  -e REQUEST_URL=http://gateway \
  mcr.microsoft.com/playwright:v1.63.0-noble \
  sh -c "npm ci --no-audit --no-fund --loglevel=error && npx playwright test $*"
