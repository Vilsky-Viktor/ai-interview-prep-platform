import uuid
from datetime import UTC, datetime

from fastapi import HTTPException

from app.constants.roles import MAX_PENDING_INVITES, MEMBER_INVITES_PER_UNPAID_DAY, TOO_MANY_PENDING
from app.integrations import billing
from app.models.companies import Member
from app.routers import members as members_router
from tests.unit.test_members import COMPANY_ID, sign_in, team  # noqa: F401

URL = f"/members?company_id={COMPANY_ID}"


def test_a_company_holds_a_limited_number_of_pending_invites(client, team):  # noqa: F811
    listed, added, _ = team
    listed.extend(
        Member(
            id=uuid.uuid4(),
            invited_email=f"waiting{index}@example.com",
            role="viewer",
            created_at=datetime.now(UTC),
        )
        for index in range(MAX_PENDING_INVITES - 1)
    )
    sign_in("ann@example.com", uid="ann")

    response = client.post(URL, json={"email": "new@example.com"})

    assert response.status_code == 409
    assert response.json() == {"detail": TOO_MANY_PENDING}
    assert added == []


def test_a_company_that_never_paid_sends_a_limited_number_of_invites_a_day(
    client,
    team,  # noqa: F811
    monkeypatch,
):
    _, added, _ = team
    counted = []

    async def unpaid(_company_id):
        return False

    async def hit(redis, key, limit, window):
        counted.append((key, limit))

        if len(counted) > MEMBER_INVITES_PER_UNPAID_DAY:
            raise HTTPException(429, "Too many requests. Try again later.")

    monkeypatch.setattr(billing, "company_paid", unpaid)
    monkeypatch.setattr(members_router, "hit", hit)
    sign_in("ann@example.com", uid="ann")

    for index in range(MEMBER_INVITES_PER_UNPAID_DAY):
        assert client.post(URL, json={"email": f"m{index}@example.com"}).status_code == 201

    assert client.post(URL, json={"email": "one-more@example.com"}).status_code == 429
    assert counted[0] == (f"rate:member-invites:{COMPANY_ID}", MEMBER_INVITES_PER_UNPAID_DAY)
    assert len(added) == MEMBER_INVITES_PER_UNPAID_DAY
