---
name: api-types
description: Refresh the assistant's API snapshots and the frontend's generated API types after a service's routes or schemas change.
---

# Refresh API snapshots and frontend types

A change to a service's routes or schemas must reach two generated copies in the same commit:

- the assistant's snapshots, `services/assistant/app/openapi/<service>.json`, which its tools
  are built from;
- the frontend's types, `frontend/types/api/<service>.ts` (ats, billing, companies, generation,
  library, notifications, rounds).

The local stack must be running with the change loaded (the services reload on save).

## Steps

```bash
scripts/assistant-openapi.sh

cd frontend
for svc in ats billing companies library notifications rounds; do
  npx openapi-typescript http://127.0.0.1:8090/api/$svc/openapi.json -o types/api/$svc.ts
done
# Generation is served at /api/generate, not /api/generation.
npx openapi-typescript http://127.0.0.1:8090/api/generate/openapi.json -o types/api/generation.ts
npx prettier --write types/api
npx tsc --noEmit -p .
```

Regenerate only the services that changed when you know which. Prettier run over wider paths
may rewrite `components/superadmin/decline-verification.tsx` and `components/ui/switch.tsx`;
revert those (`git checkout --`) unless you meant to change them.

## Check

- `git diff --stat frontend/types/api services/assistant/app/openapi`: only what the change
  explains. A larger diff means an earlier change was never refreshed; keep it, and say so.
- `cd services/assistant && uv run pytest -q tests/unit` still passes.
- If a URL answers 500 or times out, it may be the frontend answering an unknown path: check the
  gateway's route in `gateway/nginx.conf` before suspecting the service.
