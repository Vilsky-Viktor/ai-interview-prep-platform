FROM python:3.13-alpine AS base

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

WORKDIR /service

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

# Development: docker-compose.yml mounts the source, and the consumer restarts on change.
FROM base AS dev

ENV PYTHONPYCACHEPREFIX=/tmp/pycache WATCHFILES_FORCE_POLLING=true

CMD ["uv", "run", "--with", "watchfiles", "--no-sync", "watchfiles", "--filter", "python", \
    "python -m app.main", "/service/app"]

# Production: the source is part of the image.
FROM base AS prod

COPY app ./app

CMD ["uv", "run", "--no-sync", "python", "-m", "app.main"]
