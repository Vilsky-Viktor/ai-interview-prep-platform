# Built from the repo root (see docker-compose.yml), so the shared package can be copied in.
FROM python:3.13-alpine AS base

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

# The image mirrors the repo layout, so pyproject.toml's path source (../../packages/common)
# finds the shared package.
WORKDIR /services/rounds

COPY packages/common /packages/common
COPY services/rounds/pyproject.toml services/rounds/uv.lock services/rounds/.python-version ./
RUN uv sync --frozen --no-dev

EXPOSE 8000

# Development: docker-compose.yml mounts the source, and the server reloads on change.
FROM base AS dev

# Bytecode stays out of the mounted source, so tests run on the host can't leave a half-written
# .pyc that a reloading container then fails to import. Polling sees changes from the host.
ENV PYTHONPYCACHEPREFIX=/tmp/pycache WATCHFILES_FORCE_POLLING=true

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
    "--reload", "--reload-dir", "app", "--reload-dir", "/packages/common/src"]

# Production: the source is part of the image. Migrations run in a one-off container
# (alembic upgrade head) before the API starts.
FROM base AS prod

COPY services/rounds/alembic.ini ./
COPY services/rounds/migrations ./migrations
COPY services/rounds/app ./app

# An unprivileged user that can read the code but not change it. Bytecode is compiled now, as
# that user can't write it later.
RUN python -m compileall -q app && adduser -D -H -u 10001 app
ENV UV_CACHE_DIR=/tmp/uv-cache
USER app

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
