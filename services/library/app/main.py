from contextlib import asynccontextmanager

import firebase_admin
from fastapi import FastAPI

from app.config.settings import settings
from app.helpers.logging import RequestLogMiddleware, configure_logging
from app.integrations.events import get_redis
from app.routers import (
    internal,
    internal_feedback,
    joins,
    library,
    me,
    preparations,
    questions,
    shares,
)

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})

    yield

    await get_redis().aclose()


app = FastAPI(title="library", lifespan=lifespan)
app.add_middleware(RequestLogMiddleware)
app.include_router(me.router)
app.include_router(preparations.router)
app.include_router(joins.router)
app.include_router(shares.router)
app.include_router(questions.router)
app.include_router(library.router)
app.include_router(internal.router)
app.include_router(internal_feedback.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
