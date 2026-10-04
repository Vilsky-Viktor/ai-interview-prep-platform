import os

# Integration tests (tests/integration) use a database of their own, never the dev one: the
# service's database name with "_test" added.
if os.getenv("INTEGRATION_TESTS"):
    os.environ["DATABASE_URL"] += "_test"

os.environ.setdefault("FIREBASE_PROJECT_ID", "demo-test")
# A demo- project: no Google Cloud, so calls from Pub/Sub, Cloud Tasks and Scheduler aren't
# token-checked, and jobs run locally.
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "demo-test")
os.environ.setdefault("BILLING_URL", "http://billing:8000")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("REDIS_URL", "redis://localhost")
# The daily cap is on by default; tests that check it turn it on themselves.
os.environ.setdefault("DAILY_GENERATION_LIMIT", "0")
os.environ.setdefault("LIBRARY_URL", "http://library")
os.environ.setdefault("SERVICE_SECRET", "test-secret-that-is-at-least-32-bytes")
os.environ.setdefault("LIBRARY_SERVICE_SECRET", "test-secret-that-is-at-least-32-bytes")
os.environ.setdefault("GENERATION_SERVICE_SECRET", "test-secret-that-is-at-least-32-bytes")
os.environ.setdefault("ROUNDS_SERVICE_SECRET", "test-secret-that-is-at-least-32-bytes")
os.environ.setdefault("COMPANIES_SERVICE_SECRET", "test-secret-that-is-at-least-32-bytes")
os.environ.setdefault("BILLING_SERVICE_SECRET", "test-secret-that-is-at-least-32-bytes")
os.environ.setdefault("GENERATION_LIMIT", "0")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    # No lifespan: tests don't have Redis.
    return TestClient(app)


@pytest.fixture(autouse=True)
def queued(monkeypatch):
    """Worker jobs the code queues, recorded instead of sent: (path, payload)."""
    from app.integrations import tasks

    jobs = []

    async def enqueue(path, payload):
        jobs.append((path, payload))

    monkeypatch.setattr(tasks, "enqueue", enqueue)

    return jobs
