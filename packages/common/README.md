# prepza-common

Code every prepza API service shares. It reads no service settings: each service passes in
what differs (its name, the service secret, its database URL).

Services depend on it by path (see `[tool.uv.sources]` in each service's `pyproject.toml`). To
publish it instead, run `uv build` and `uv publish` here, then replace the path source with a
version requirement such as `prepza-common>=0.1`.
