# prepza-common

Code every prepza API service shares: sign-in, service tokens, logging, database and HTTP setup,
the outbox and Pub/Sub, notifications, who may do what in a company (asked of companies; a
company that's gone is no access), translated messages, a small in-memory cache, the admin zone's
stats counting and the limits several services read (`rate_limit.hit` counts uses, `rate_limit.spend`
adds up a cost such as tokens against a budget) and server-sent events (`sse`: the help chat's
and the assistant's answers, the bell's stream), secret tokens kept as their hashes (`tokens`: API
keys, AI apps' access) and a visitor's address behind the load balancer (`client_ip`).
OpenAI chat models: `llm.chat_model` builds them one way for every service (a temperature only at
reasoning effort `none`). It needs the package's `llm` extra (langchain-openai), so a service that
calls OpenAI depends on `prepza-common[llm]`; the others don't install it.
Logs: `logging.configure_logging` writes one JSON line per entry in the fields Cloud Logging reads
(`severity`, `message`), and `RequestLogMiddleware` ties every line logged while serving a request
to its trace (`logging.googleapis.com/trace`, from the load balancer's `X-Cloud-Trace-Context`).
Settings: `ServiceSettings` (`settings.py`) is the base of every service's `Settings`, with the
sign-in settings they all read (`FIREBASE_PROJECT_ID`, and `FIREBASE_AUTH_EMULATOR_HOST`, refused
unless the project is a `demo-` one). Each service's own settings live in its
`app/config/settings.py`, and it passes in what differs (its name, its database URL). Otherwise the
package reads only environment variables every service has: `SENTRY_*`, `GOOGLE_CLOUD_PROJECT`,
`PUBSUB_EMULATOR_HOST` (locally), `ANALYTICS_SALT`, `SUPERADMIN_EMAILS`, `INVOKER_SERVICE_ACCOUNT`
and `INVOKER_AUDIENCE`, and the `<SERVICE>_SERVICE_SECRET` keys of the services it calls.

Services depend on it by path (see `[tool.uv.sources]` in each service's `pyproject.toml`). To
publish it instead, run `uv build` and `uv publish` here, then replace the path source with a
version requirement such as `prepza-common>=0.1`.
