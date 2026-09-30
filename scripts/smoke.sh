#!/usr/bin/env bash
# Hits the public pages and service health endpoints through the gateway.
set -euo pipefail

base="${1:-http://localhost:8090}"

check() {
  local path="$1"
  local code

  code="$(curl -sS -o /dev/null -w '%{http_code}' "$base$path")"

  if [[ "$code" != "200" ]]; then
    echo "FAIL $path -> $code" >&2

    exit 1
  fi

  echo "ok $path"
}

check /
check /library
check /api/library/health
check /api/generate/health
check /api/rounds/health
check /api/companies/health

echo "smoke ok"
