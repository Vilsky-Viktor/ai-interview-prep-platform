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
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("SERVICE_SECRET", "test-secret-that-is-at-least-32-bytes")
os.environ.setdefault("GENERATION_URL", "http://generation")
os.environ.setdefault("LIBRARY_URL", "http://library")
os.environ.setdefault("ROUNDS_URL", "http://rounds")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client
