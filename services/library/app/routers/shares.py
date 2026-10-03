from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams
from prepza_common.rate_limit import hit_emails

from app.config.settings import settings
from app.constants.sets import MAX_SHARES, TOO_MANY_SHARES
from app.integrations.redis import get_redis
from app.schemas.sharing import ShareIn, ShareInviteOut, ShareOut
from app.services import outbox as outbox_service
from app.services.access import require_owner
from app.storage import preparations, shares

router = APIRouter(tags=["shares"])


@router.post("/preparations/{preparation_id}/shares", status_code=status.HTTP_201_CREATED)
async def share(preparation_id: UUID, body: ShareIn, user: CurrentUser) -> ShareOut:
    """Invites one email; sharing the same email again resends the invite."""
    question_set = require_owner(await preparations.get(preparation_id), user.uid)
    email = body.email.lower()

    if email == user.email.lower():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You can't share with yourself")

    # Resending to someone already invited is always allowed.
    invited = await shares.is_invited(preparation_id, email)
    people = await shares.count_for_set(preparation_id)

    if not invited and people >= MAX_SHARES:
        await track("limit_hit", user_id=user.uid, which="shares")

        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, TOO_MANY_SHARES)

    await hit_emails(
        get_redis(),
        user.uid,
        f"{preparation_id}:{email}",
        settings.email_hourly_limit,
        settings.email_daily_limit,
        settings.email_recipient_daily_limit,
    )
    invite = await shares.upsert(
        preparation_id,
        email,
        user.uid,
        question_set.title,
        user.name or user.email,
        question_set.language,
    )
    await outbox_service.flush_quietly()

    if not invited:
        await track("kit_shared", user_id=user.uid, people=people + 1)

    return ShareOut(
        email=invite.email, accepted=invite.accepted_by is not None, created_at=invite.created_at
    )


@router.get("/preparations/{preparation_id}/shares")
async def list_shares(preparation_id: UUID, user: CurrentUser, page: PageParams) -> list[ShareOut]:
    require_owner(await preparations.get(preparation_id), user.uid)

    return [
        ShareOut(
            email=invite.email,
            accepted=invite.accepted_by is not None,
            undelivered=invite.undelivered_at is not None,
            created_at=invite.created_at,
        )
        for invite in await shares.list_for_set(preparation_id, page.offset, page.limit)
    ]


@router.get("/shares/{token}")
async def get_share(token: str, user: CurrentUser) -> ShareInviteOut:
    found = await shares.get_by_token(token)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    invite, question_set = found

    return ShareInviteOut(
        preparation_id=question_set.id,
        title=question_set.title,
        email=invite.email,
        accepted=invite.accepted_by is not None,
    )


@router.post("/shares/{token}/accept", status_code=status.HTTP_204_NO_CONTENT)
async def accept_share(token: str, user: CurrentUser) -> None:
    """Only the invited email can accept, so a forwarded link is useless to anyone else."""
    found = await shares.get_by_token(token)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    invite, _ = found

    if not user.email_verified or user.email.lower() != invite.email:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This invite was sent to a different email address"
        )

    await shares.accept(invite, user.uid)
