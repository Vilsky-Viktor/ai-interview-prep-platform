import uuid

import pytest
from fastapi import HTTPException
from prepza_common.rate_limit import hit_emails
from redis.asyncio import Redis

from app.config.settings import settings


def test_email_limits_count_in_real_redis(run):
    sender = f"sender-{uuid.uuid4()}"

    async def scenario():
        redis = Redis.from_url(settings.redis_url)

        try:
            for _ in range(3):
                await hit_emails(redis, sender, "interview:carol@example.com", 30, 200, 3)

            with pytest.raises(HTTPException) as refused:
                await hit_emails(redis, sender, "interview:carol@example.com", 30, 200, 3)

            ttl = await redis.ttl("rate:emails:recipient:interview:carol@example.com")
            await redis.delete(
                f"rate:emails:hour:{sender}",
                f"rate:emails:day:{sender}",
                "rate:emails:recipient:interview:carol@example.com",
            )
        finally:
            await redis.aclose()

        return refused.value.status_code, ttl

    status, ttl = run(scenario())

    assert status == 429
    # Every counter expires, so a limit never sticks forever.
    assert 0 < ttl <= 24 * 60 * 60


def test_invites_refused_for_credits_use_up_no_email_limits(run, monkeypatch):
    """A company out of credits (an ATS sending candidates) must not use up the limits, or its
    invites are refused with 429 once it tops up."""
    from prepza_common.user import User

    from app.integrations import billing
    from app.services import candidate_invites
    from app.storage import companies, interviews

    credits = {"left": False}

    async def hold(company_id, key):
        if not credits["left"]:
            raise HTTPException(402, "No candidate credits left.")

    monkeypatch.setattr(billing, "hold_candidate", hold)
    sender = User(uid=f"sender-{uuid.uuid4()}", email="", email_verified=True)
    email = "dana@example.com"

    async def scenario():
        redis = Redis.from_url(settings.redis_url)
        monkeypatch.setattr(candidate_invites, "get_redis", lambda: redis)
        company = await companies.create(f"Acme {uuid.uuid4()}", sender.uid, "o@example.com")
        created = await interviews.create(company.id, uuid.uuid4(), "en")
        await interviews.set_set_id(created.id, uuid.uuid4())
        # Titled, so nothing asks library for it.
        await interviews.set_title(created.id, "Backend interview")
        interview = await interviews.get(created.id)
        codes = []

        try:
            for left in (False,) * 4 + (True,) * 3:
                credits["left"] = left

                try:
                    await candidate_invites.invite(interview, company, sender, email)
                    codes.append(201)
                except HTTPException as error:
                    codes.append(error.status_code)

            await redis.delete(
                f"rate:emails:hour:{sender.uid}",
                f"rate:emails:day:{sender.uid}",
                f"rate:emails:recipient:{interview.id}:{email}",
            )
        finally:
            await redis.aclose()

        return codes

    assert run(scenario()) == [402] * 4 + [201] * 3
