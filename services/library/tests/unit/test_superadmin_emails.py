import logging
from types import SimpleNamespace

import pytest
from firebase_admin import auth as firebase_auth
from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.emails import DEFAULTS
from app.main import app
from app.storage import emails

ACCOUNT = SimpleNamespace(uid="ann", email="ann@example.com")


@pytest.fixture
def signed_in(monkeypatch):
    """Firebase knows Ann; storage records the changes. Signs in as the superadmin Sam, or as
    `email`."""
    monkeypatch.setenv("SUPERADMIN_EMAILS", "sam@prepza.dev")
    asked = []
    changes = []

    def get_user_by_email(email):
        asked.append(email)

        if email != ACCOUNT.email:
            raise firebase_auth.UserNotFoundError("none")

        return ACCOUNT

    def get_user(uid):
        if uid != ACCOUNT.uid:
            raise firebase_auth.UserNotFoundError("none")

        return ACCOUNT

    async def preferences(user_id):
        return dict(DEFAULTS)

    async def change(user_id, settings, source, changed_by=None):
        changes.append((user_id, settings, source, changed_by))

        return {**DEFAULTS, **settings}

    monkeypatch.setattr(firebase_auth, "get_user_by_email", get_user_by_email)
    monkeypatch.setattr(firebase_auth, "get_user", get_user)
    monkeypatch.setattr(emails, "preferences", preferences)
    monkeypatch.setattr(emails, "change", change)

    def sign_in(email="sam@prepza.dev"):
        app.dependency_overrides[current_user] = lambda: User(
            uid="sam", email=email, email_verified=True
        )

    sign_in()
    yield SimpleNamespace(asked=asked, changes=changes, sign_in=sign_in)

    app.dependency_overrides.clear()


def test_a_superadmin_finds_an_account_by_its_address_whatever_its_case(client, signed_in):
    response = client.post("/superadmin/emails/lookup", json={"email": " Ann@Example.COM "})

    assert response.status_code == 200
    assert response.json() == {
        "account": {"user_id": "ann", "email": "ann@example.com", "preferences": DEFAULTS}
    }
    assert signed_in.asked == ["ann@example.com"]


def test_an_address_without_an_account_finds_none(client, signed_in):
    response = client.post("/superadmin/emails/lookup", json={"email": "zoe@example.com"})

    assert response.json() == {"account": None}


def test_a_superadmins_change_is_logged_with_the_admin_source_and_their_id(
    client, signed_in, caplog
):
    off = {"updates": False, "promotions": False}

    with caplog.at_level(logging.WARNING):
        response = client.put("/superadmin/emails/ann/preferences", json={"changes": off})

    assert response.status_code == 200
    assert response.json() == {**DEFAULTS, **off}
    assert signed_in.changes == [("ann", off, "admin", "sam")]
    assert "changed by superadmin sam" in caplog.text


def test_a_change_to_an_account_that_is_gone_is_not_found(client, signed_in):
    response = client.put(
        "/superadmin/emails/gone/preferences", json={"changes": {"updates": False}}
    )

    assert response.status_code == 404
    assert signed_in.changes == []


@pytest.mark.parametrize("changes", [{}, {"newsletter": False}])
def test_a_change_names_known_settings(client, signed_in, changes):
    response = client.put("/superadmin/emails/ann/preferences", json={"changes": changes})

    assert response.status_code == 422


def test_anyone_else_gets_not_found(client, signed_in):
    signed_in.sign_in("bob@example.com")

    lookup = client.post("/superadmin/emails/lookup", json={"email": "ann@example.com"})
    change = client.put("/superadmin/emails/ann/preferences", json={"changes": {"updates": False}})

    assert (lookup.status_code, change.status_code) == (404, 404)
    assert (signed_in.asked, signed_in.changes) == ([], [])


def test_signed_out_gets_401(client):
    assert client.post("/superadmin/emails/lookup", json={"email": "a@b.c"}).status_code == 401
