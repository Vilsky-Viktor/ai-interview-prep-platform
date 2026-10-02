import os

# Integration tests (tests/integration) use a database of their own, never the dev one: the
# service's database name with "_test" added.
if os.getenv("INTEGRATION_TESTS"):
    os.environ["DATABASE_URL"] += "_test"

os.environ.setdefault("FIREBASE_PROJECT_ID", "demo-test")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("SERVICE_SECRET", "test-secret-that-is-at-least-32-bytes")
os.environ.setdefault("PADDLE_WEBHOOK_SECRET", "pdl_ntfset_test_secret")
os.environ.setdefault("PADDLE_PRICE_CANDIDATES_10", "pri_candidates_10")
os.environ.setdefault("PADDLE_PRICE_JOB_SEARCH_PASS", "pri_pass")
os.environ.setdefault("PADDLE_PRICE_GENERATIONS_3", "pri_generations_3")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client
