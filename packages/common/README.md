# prepza-common

Code every prepza API service shares: sign-in, service tokens, logging, database and HTTP setup,
the outbox and Pub/Sub, notifications, translated messages, a small in-memory cache, the admin
zone's stats counting and the limits several services read.
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
