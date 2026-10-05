# prepza-common

Code every prepza API service shares: sign-in, service tokens, logging, database and HTTP setup,
the outbox and Pub/Sub, notifications, translated messages and the limits several services read.
It holds no service's settings: each service passes in
what differs (its name, its service secret, its database URL). It reads only the environment
variables every service has, such as `SENTRY_*`, `GOOGLE_CLOUD_PROJECT`, `ANALYTICS_SALT`,
`SUPERADMIN_EMAILS` and the `<SERVICE>_SERVICE_SECRET` keys of the services it calls.

Services depend on it by path (see `[tool.uv.sources]` in each service's `pyproject.toml`). To
publish it instead, run `uv build` and `uv publish` here, then replace the path source with a
version requirement such as `prepza-common>=0.1`.
