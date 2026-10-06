#!/usr/bin/env bash
# Browser tests of the signed-out pages (e2e_tests/pages), in Playwright's Docker image, against
# the running stack: the browser opens SITE_URL, which Chromium resolves to the gateway on the
# stack's own network. Usage: e2e_tests/pages.sh
set -euo pipefail

cd "$(dirname "$0")/.."

if docker compose version >/dev/null 2>&1; then
  compose=(docker compose)
else
  compose=(docker-compose)
fi

gateway="$("${compose[@]}" ps -q gateway)"
network="$(docker inspect -f '{{range $name, $_ := .NetworkSettings.Networks}}{{$name}}{{end}}' "$gateway")"

docker run --rm --network "$network" \
  -v "$PWD/e2e_tests/pages:/tests" -w /tests \
  -e SITE_URL=http://localhost:8090 \
  -e HOST_RULES="MAP localhost:8090 gateway:80" \
  mcr.microsoft.com/playwright:v1.63.0-noble \
  sh -c "npm ci --no-audit --no-fund --loglevel=error && npx playwright test"
