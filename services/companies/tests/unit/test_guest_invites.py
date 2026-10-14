from types import SimpleNamespace

import pytest
from firebase_admin import auth as firebase_auth
from prepza_common.auth import current_user
from prepza_common.user import User

import app.routers.invites as routes
from app.constants.invites import NOT_THE_GUEST, InviteStatus
from app.main import app
from tests.unit.test_invites import INVITE_ID, invite_page, stored_invite  # noqa: F401 (fixtures)

GUEST = f"guest-{INVITE_ID}"


def sign_in(uid, email=""):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=email, email_verified=bool(email)
    )


@pytest.fixture
def guest_invite(monkeypatch, invite_page):  # noqa: F811
    """The invite a company's platform sent with sign_in false, its candidate in it already, and
    the sessions it starts recorded instead of made."""
    invite_page.guest = True
    invite_page.status = InviteStatus.IN_PROCESS
    started = []

    async def start(invite, interview, user):
        started.append(user.uid)

        return {"sessions": []}

    monkeypatch.setattr(routes, "start_sessions", start)
    monkeypatch.setattr(
        firebase_auth, "create_custom_token", lambda uid: f"custom-for-{uid}".encode()
    )

    return started


def test_a_guest_invitation_says_so_and_signs_its_link_in(client, guest_invite):
    assert client.get("/invites/token-1").json()["guest"] is True

    response = client.post("/invites/token-1/guest")

    assert response.status_code == 200
    assert response.json() == {"token": f"custom-for-{GUEST}"}


def test_an_invitation_by_email_has_no_guest_sign_in(client, invite_page):  # noqa: F811
    assert client.get("/invites/token-1").json()["guest"] is False
    assert client.post("/invites/token-1/guest").status_code == 404


def test_an_expired_guest_invitation_signs_no_one_in(
    client,
    guest_invite,
    invite_page,  # noqa: F811
):
    invite_page.status = InviteStatus.EXPIRED

    assert client.post("/invites/token-1/guest").status_code == 404


def test_the_guest_starts_without_an_email(client, guest_invite):
    sign_in(GUEST)

    assert client.post("/invites/token-1/start").status_code == 200
    assert guest_invite == [GUEST]


def test_only_the_guest_starts_a_guest_invitation_not_even_the_invited_email(client, guest_invite):
    sign_in("bob", "bob@example.com")
    response = client.post("/invites/token-1/start")

    assert response.status_code == 403
    assert response.json()["detail"] == NOT_THE_GUEST
    assert guest_invite == []


def test_only_a_guest_invitation_may_be_embedded_and_only_on_the_companys_site(
    client,
    monkeypatch,
    invite_page,  # noqa: F811
):
    import app.routers.invites as routes

    async def company(company_id):
        return SimpleNamespace(
            name="Acme", website_domain="acme.com", verified_domain=None, suspended_at=None
        )

    monkeypatch.setattr(routes.companies, "get", company)
    monkeypatch.setattr(routes, "logo_path", lambda company: None)

    assert client.get("/invites/token-1").json()["embed_domain"] is None

    invite_page.guest = True

    assert client.get("/invites/token-1").json()["embed_domain"] == "acme.com"
