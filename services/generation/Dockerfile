# Built from the repo root (see docker-compose.yml), so the shared package can be copied in.
FROM python:3.13-alpine AS base

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

# The image mirrors the repo layout, so pyproject.toml's path source (../../packages/common)
# finds the shared package.
WORKDIR /services/generation

COPY packages/common /packages/common
COPY services/generation/pyproject.toml services/generation/uv.lock services/generation/.python-version ./
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

COPY services/generation/alembic.ini ./
COPY services/generation/migrations ./migrations
COPY services/generation/app ./app

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
