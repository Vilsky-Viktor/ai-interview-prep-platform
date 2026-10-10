# AI apps over MCP (Claude, ChatGPT)

A user connects prepza to their own AI app (Claude, ChatGPT, Claude Code, or any app that speaks the Model Context Protocol) and asks it about their companies, interviews and candidates, or to make changes, in that app's chat. The app calls the in-app assistant's tools as the user, with exactly their permissions; no model runs on prepza's side. The MCP server and its OAuth authorization server are part of the assistant service (`services/assistant`).

- [Connecting](#connecting)
- [The authorization flow](#the-authorization-flow)
- [Tools](#tools)
- [Calling the services as the user](#calling-the-services-as-the-user)
- [Connections and tokens](#connections-and-tokens)
- [Limits](#limits)
- [Audit and analytics](#audit-and-analytics)
- [Routes](#routes)
- [Settings](#settings)

## Connecting

- The server's address is `<SITE_URL>/mcp` (`https://prepza.ai/mcp`). The company's Integrations → AI apps page shows it with the steps for Claude (Settings → Connectors → Add custom connector) and ChatGPT (Settings → Apps & Connectors, developer mode), and Claude Code's one line: `claude mcp add --transport http prepza <SITE_URL>/mcp`.
- The app opens prepza's consent page, `/connect?request=…`, in the browser. A signed-out user signs in there first. The page names the app, the site it returns to (`redirect_host`) and the user's account, lists what it can do, and has Allow and Deny. An app whose site prepza doesn't know gets a warning.
- The app is known by the site it returns to, not by the name it gives itself (`app/constants/mcp.py` `KNOWN_CLIENTS`): `claude.ai` and `claude.com` are Claude, `chatgpt.com` is ChatGPT. An app on the user's own computer (a `localhost` or `127.0.0.1` address: Claude Code, Claude Desktop, MCP Inspector) is known too and named as it says, since its code never leaves that computer. Any other site is unknown, named as it says.
- A connection belongs to the account, not to a company: the app acts in every company the user is in. The AI apps page lists the user's connected apps (name, site, when connected and last used) on every company's Integrations tab, and Disconnect stops one at once.

## The authorization flow

OAuth 2.1 with PKCE (`S256`) and dynamic client registration, from the MCP SDK's building blocks (`mcp` 2.x, `mcp.server.auth`), at the site's root:

1. The app calls `/mcp` and gets a `401` whose `WWW-Authenticate` names the resource metadata (`/.well-known/oauth-protected-resource/mcp`, also at `/.well-known/oauth-protected-resource`). That names the site as the authorization server, whose metadata is at `/.well-known/oauth-authorization-server`.
2. It registers at `/register` (public clients without a secret are welcome; `token_endpoint_auth_method: none`). Its registration is kept in Postgres (`oauth_clients`).
3. `GET /authorize` (the SDK checks the client, the redirect URI, the scope and PKCE) keeps the request in Redis for 10 minutes and sends the browser to `/connect?request=<id>`. A `resource` other than `<SITE_URL>/mcp` is refused (`invalid_target`).
4. The consent page reads it (`GET /api/assistant/connect/{id}`) and answers with the user's Firebase token: `POST …/approve` takes the request (Redis `GETDEL`, so it's answered once) and makes a single-use code bound to the user, the app, the redirect URI and the PKCE challenge (Redis, 5 minutes, kept as its hash); `POST …/deny` returns `error=access_denied`. Either answers `{"redirect_url"}`, where the page sends the browser.
5. `POST /token` exchanges the code with the PKCE verifier for an access token (1 hour) and a refresh token (90 days). The code works once.
6. A refresh replaces both tokens; the old refresh token then gets `invalid_grant`. Of two refreshes with one token only the first wins (no family revocation, so a client's racing refreshes don't cut it off).
7. `POST /revoke` (the app removed there) deletes the connection.

## Tools

- Every tool of the in-app assistant (`app/services/registry.py`), except `delete_account` and `delete_company` (`MCP_EXCLUDED`): deleting the account or a company (with its paid credits) is done in prepza itself, and calling them answers so. The panel's own `show` and `sign_out` aren't offered.
- Each tool has its description and parameters as the assistant's model sees them, and hints for the app's own approval prompt: reads are `readOnlyHint`; writes carry `destructiveHint` (the actions the panel warns about) and `idempotentHint` (`PUT` and `DELETE`); none reaches the open web.
- A write runs at once: the app asks the user before calling it, instead of the panel's confirmation card. It still passes the panel's checks (`app/services/mcp_tools.py`): the emergency pause, what it's about must be the user's (`subject`, else a `404`), a partial update sends only what changes (nothing to change is refused), and it counts against the user's 30 actions an hour. It runs once with a new `Idempotency-Key`.
- A string argument holding a secret is refused with the chat's "secrets never through the chat" reply, before anything is sent.
- A result is the tool's data as JSON (trimmed as for the model, with `shown`/`more` on a cut list) and `links` to the prepza pages that show it, absolute. An error (the service's own, in the user's language, or a limit) is a result with `isError`.
- The server's instructions (`app/prompts/mcp.py`) tell the app to get ids from the companies tools, to use `get_platform_guide` for how-to and pricing, never to ask for secrets, and that deletions are done in prepza.
- Streamable HTTP, stateless, with plain JSON answers: no sessions and no streams held open, so any assistant instance answers any request.

## Calling the services as the user

The tools call the other services' user-facing routes exactly as the panel does, with a Firebase ID token of the user's, so every role, rule and the language apply unchanged. The assistant gets one per user (`app/integrations/firebase_tokens.py`): it reads the account with the Admin SDK (a deleted or disabled one gets nothing, and a custom token is never made for an unknown uid, which would create that user), signs a custom token for it and exchanges it at Firebase's `accounts:signInWithCustomToken` with the public web key (the Auth emulator's locally). The token is kept in memory until 5 minutes before it expires, and dropped after `update_language` so the next calls use the new language. In Google Cloud the assistant's account needs `roles/firebaseauth.viewer` and to sign as itself (`roles/iam.serviceAccountTokenCreator` on itself; `infra/terraform/iam.tf`).

## Connections and tokens

- `mcp_grants` (Postgres `assistant`), one row a connection: the user, the app, the name and site the user saw, when it was connected and last used (written at most once an hour), and the SHA-256 hashes of its tokens (`pzm_…`, opaque) with their expiry. A leaked database gives no working tokens.
- `GET /api/assistant/connections` lists the user's own; `DELETE /api/assistant/connections/{id}` disconnects one (a `404` for one that isn't theirs).
- Deleting an account deletes its connections; "Download my data" lists them (`connected_ai_apps`: name, site, dates).
- The daily retention (`/internal/schedules/retention`) deletes connections whose refresh token expired and registered apps that have had no connection for 30 days.

## Limits

Constants in `app/constants/limits.py`, counted in Redis; with Redis down they're skipped rather than refusing everything.

| Limit | Value |
|---|---|
| Calls of a user's apps | 60 a minute, 3,000 a day |
| Writes (with the panel's actions) | 30 a user an hour |
| Registrations | 300 an address an hour, 5,000 a day for everyone (Claude and ChatGPT register from their own servers) |
| Token requests | 30 an app a minute |
| Connections a user allows | 20 an hour |

The services' own limits (generation, emails, credits) apply as they do in the app, and so do the emergency pause and maintenance mode.

## Audit and analytics

- Calls to companies carry the signed `X-Assistant` header issued as `mcp`: a candidate's results read through an app are audited with `via: "mcp"` and kept out of the "results viewed" funnel.
- Funnel events (`internal_docs/measurement.md`): `mcp_connected {client}`, `mcp_disconnected {by: user|client}`, `mcp_action {tool, ok}` for writes, and `mcp_active {client}` at most once a day for each user and app (`client` is `claude`, `chatgpt` or `other`).

## Routes

| Route | What |
|---|---|
| `/mcp` | The MCP endpoint (bearer token) |
| `/.well-known/oauth-protected-resource/mcp`, `/.well-known/oauth-protected-resource` | The resource's metadata |
| `/.well-known/oauth-authorization-server` | The authorization server's metadata |
| `/authorize`, `/token`, `/register`, `/revoke` | OAuth |
| `/api/assistant/connect/{id}` (`GET`, `…/approve`, `…/deny`) | The consent page's API (Firebase token) |
| `/api/assistant/connections` (`GET`, `DELETE …/{id}`) | The user's connected apps (Firebase token) |

The root paths are exact matches in the gateway (`gateway/nginx.conf`) and the load balancer (`infra/terraform/locals.tf` `mcp_paths`), sent to the assistant as they are; no frontend page may use them.

## Settings

| Setting | What it sets |
|---|---|
| `SITE_URL` | The issuer (the site's root) and the resource (`<SITE_URL>/mcp`); where the consent page is |
| `FIREBASE_WEB_API_KEY` | Firebase's public web key (the frontend's `NEXT_PUBLIC_FIREBASE_API_KEY`), to sign the user in for the services |
