from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prepza_common.service_auth import callee_secret, issue_token, service_caller

LIBRARY_SECRET = "library-secret-that-is-at-least-32-bytes"
ROUNDS_SECRET = "rounds-secret-that-is-at-least-32-bytes!"


def library():
    """Library's app, admitting calls signed with its key and addressed to it."""
    app = FastAPI()
    caller = service_caller(LIBRARY_SECRET, "library")

    @app.get("/internal")
    def internal(name: caller) -> dict:
        return {"caller": name}

    return TestClient(app)


def call(token):
    return library().get("/internal", headers={"Authorization": f"Bearer {token}"})


def test_a_token_for_library_signed_with_its_key_names_the_caller():
    response = call(issue_token("companies", "library", LIBRARY_SECRET))

    assert response.status_code == 200
    assert response.json() == {"caller": "companies"}


@pytest.mark.parametrize(
    "token",
    [
        # Addressed to rounds: useless at library, even with library's key.
        issue_token("companies", "rounds", LIBRARY_SECRET),
        # Signed with another service's key.
        issue_token("companies", "library", ROUNDS_SECRET),
        jwt.encode(
            {"iss": "companies", "aud": "library", "exp": datetime.now(UTC) - timedelta(seconds=1)},
            LIBRARY_SECRET,
            algorithm="HS256",
        ),
        # The old kind of token, without an audience.
        jwt.encode(
            {"iss": "companies", "exp": datetime.now(UTC) + timedelta(seconds=30)},
            LIBRARY_SECRET,
            algorithm="HS256",
        ),
    ],
    ids=["for another service", "wrong key", "expired", "no audience"],
)
def test_other_tokens_are_refused(token):
    assert call(token).status_code == 401


def test_a_caller_reads_the_key_of_the_service_it_calls(monkeypatch):
    monkeypatch.setenv("LIBRARY_SERVICE_SECRET", LIBRARY_SECRET)

    assert callee_secret("library") == LIBRARY_SECRET
