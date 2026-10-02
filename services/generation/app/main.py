import logging
from contextlib import asynccontextmanager

import firebase_admin
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, HTTPException, Request, status
from prepza_common import http
from prepza_common.logging import RequestLogMiddleware, configure_logging

from app.config.settings import settings
from app.routers import generations, internal
from app.storage.db import ping as ping_database

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})
    app.state.arq = await create_pool(RedisSettings.from_dsn(settings.redis_url))

    yield

    await app.state.arq.aclose()
    await http.get_client().aclose()


app = FastAPI(title="generation", lifespan=lifespan)
app.add_middleware(RequestLogMiddleware)
app.include_router(generations.router)
app.include_router(internal.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request) -> dict:
    """Ready only once the database and Redis answer; Docker's healthcheck uses this."""
    try:
        await ping_database()
        await request.app.state.arq.ping()
    except Exception:
        logging.getLogger(__name__).exception("Not ready")

        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Not ready")

    return {"status": "ready"}
