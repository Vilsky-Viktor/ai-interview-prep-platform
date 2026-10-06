import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.integrations import billing
from app.main import app
from app.models.companies import Company, Member
from app.storage import companies, members

MEMBER_ID = uuid.uuid4()
COMPANY_ID = uuid.uuid4()


def sign_in(email, verified=True, uid="admin"):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=email, email_verified=verified, name="Bob"
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def stored_invite(monkeypatch):
    member = Member(
        id=MEMBER_ID,
        company_id=COMPANY_ID,
        invited_email="bob@example.com",
        token="token-1",
        role="admin",
        created_at=datetime.now(UTC),
    )
    company = Company(id=COMPANY_ID, name="Arcolabs", created_at=datetime.now(UTC))
    accepted = []

    async def fake_get(token):
        return (member, company) if token == "token-1" else None

    async def fake_accept(item, user_id):
        accepted.append(user_id)

    monkeypatch.setattr(members, "get_by_token", fake_get)
    monkeypatch.setattr(members, "accept", fake_accept)

    return accepted


def test_invited_email_accepts(client, stored_invite):
    sign_in("Bob@Example.com", uid="bob")

    assert client.post("/members/invites/token-1/accept").status_code == 204
    assert stored_invite == ["bob"]


@pytest.mark.parametrize(
    ("email", "verified"), [("eve@example.com", True), ("bob@example.com", False)]
)
def test_other_or_unverified_email_is_rejected(client, stored_invite, email, verified):
    sign_in(email, verified)

    assert client.post("/members/invites/token-1/accept").status_code == 403
    assert stored_invite == []


def test_unknown_token(client, stored_invite):
    sign_in("bob@example.com")

    assert client.post("/members/invites/missing/accept").status_code == 404


def test_invite_view(client, stored_invite):
    sign_in("bob@example.com")
    response = client.get("/members/invites/token-1")

    assert response.status_code == 200
    assert response.json() == {
        "company_name": "Arcolabs",
        "email": "bob@example.com",
        "joined": False,
    }


@pytest.fixture
def team(monkeypatch):
    """Ann owns the company, Bob joined as an admin, Cid's invite is pending. Returns what was
    removed, added or given a new role, and whose auto top-up billing was asked to turn off."""
    company = Company(id=COMPANY_ID, name="Arcolabs", created_at=datetime.now(UTC))
    company.members = [
        Member(
            id=uuid.uuid4(),
            user_id=uid,
            invited_email=f"{name}@example.com",
            role=role,
            created_at=datetime.now(UTC),
        )
        for uid, name, role in (
            ("ann", "ann", "owner"),
            ("bob", "bob", "admin"),
            (None, "cid", "admin"),
        )
    ]
    removed = []
    turned_off = []

    async def fake_company(_company_id):
        return company

    async def fake_remove(member_id):
        removed.append(member_id)

    async def fake_turn_off(company_id, buyer_id=None):
        turned_off.append(buyer_id)

    async def fake_list(company_id, offset, limit):
        return company.members

    async def fake_set_role(member_id, role):
        removed.append((member_id, role))

    async def fake_add(company_id, email, role):
        removed.append((email, role))

        return Member(id=uuid.uuid4(), invited_email=email, role=role, created_at=datetime.now(UTC))

    monkeypatch.setattr(members, "set_role", fake_set_role)
    monkeypatch.setattr(members, "add", fake_add)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(members, "remove", fake_remove)
    monkeypatch.setattr(members, "list_for_company", fake_list)
    monkeypatch.setattr(billing, "turn_off_auto_top_up", fake_turn_off)

    return company.members, removed, turned_off


def remove_url(member):
    return f"/members/{member.id}?company_id={COMPANY_ID}"


def test_the_owner_removes_an_admin_and_their_card_stops_paying(client, team):
    (_, bob, cid), removed, turned_off = team
    sign_in("ann@example.com", uid="ann")

    assert client.delete(remove_url(bob)).status_code == 204
    assert client.delete(remove_url(cid)).status_code == 204
    assert removed == [bob.id, cid.id]
    # A pending invite has no card to stop.
    assert turned_off == ["bob"]


def test_nobody_removes_the_owner_and_admins_remove_nobody(client, team):
    (owner, _, cid), removed, _ = team
    sign_in("ann@example.com", uid="ann")

    assert client.delete(remove_url(owner)).status_code == 409

    sign_in("bob@example.com", uid="bob")

    assert client.delete(remove_url(cid)).status_code == 403
    assert removed == []


def test_the_list_says_which_rows_can_be_removed(client, team):
    sign_in("ann@example.com", uid="ann")
    owners_view = client.get(f"/members?company_id={COMPANY_ID}").json()
    sign_in("bob@example.com", uid="bob")
    admins_view = client.get(f"/members?company_id={COMPANY_ID}").json()

    assert [row["removable"] for row in owners_view] == [False, True, True]
    assert [row["removable"] for row in admins_view] == [False, False, False]


def role_url(member):
    return f"/members/{member.id}/role?company_id={COMPANY_ID}"


def test_the_owner_invites_a_viewer_and_an_admin_by_default(client, team):
    _, changed, _ = team
    sign_in("ann@example.com", uid="ann")
    url = f"/members?company_id={COMPANY_ID}"

    viewer = client.post(url, json={"email": "dan@example.com", "role": "viewer"})
    admin = client.post(url, json={"email": "eve@example.com"})

    assert (viewer.status_code, viewer.json()["role"]) == (201, "viewer")
    assert (admin.status_code, admin.json()["role"]) == (201, "admin")
    assert changed == [("dan@example.com", "viewer"), ("eve@example.com", "admin")]
    # Nobody is invited as a second owner.
    assert client.post(url, json={"email": "fay@example.com", "role": "owner"}).status_code == 422


def test_the_owner_makes_an_admin_a_viewer_and_their_card_stops_paying(client, team):
    (_, bob, cid), changed, turned_off = team
    sign_in("ann@example.com", uid="ann")

    assert client.put(role_url(bob), json={"role": "viewer"}).status_code == 204
    assert client.put(role_url(cid), json={"role": "viewer"}).status_code == 204
    assert client.put(role_url(bob), json={"role": "admin"}).status_code == 204
    assert changed == [(bob.id, "viewer"), (cid.id, "viewer"), (bob.id, "admin")]
    assert turned_off == ["bob"]


def test_only_the_owner_changes_roles_and_never_their_own(client, team):
    (owner, _, cid), changed, _ = team
    sign_in("ann@example.com", uid="ann")

    assert client.put(role_url(owner), json={"role": "viewer"}).status_code == 409

    sign_in("bob@example.com", uid="bob")

    assert client.put(role_url(cid), json={"role": "viewer"}).status_code == 403
    assert changed == []
