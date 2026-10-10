from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser, OptionalUser
from prepza_common.constants import DAY_SECONDS
from prepza_common.paging import PageParams
from prepza_common.rate_limit import hit, hit_emails

from app.config.settings import settings
from app.constants.roles import (
    MAX_PENDING_INVITES,
    MEMBER_INVITES_PER_UNPAID_DAY,
    TOO_MANY_PENDING,
    Role,
)
from app.helpers.logos import logo_path
from app.integrations import billing
from app.integrations.redis import get_redis
from app.models.companies import Member
from app.schemas.companies import AdminInviteOut, MemberIn, MemberOut, MemberRoleIn
from app.services import outbox as outbox_service
from app.services.access import is_owner, require_company
from app.storage import members

router = APIRouter(prefix="/members", tags=["members"])


def member_out(member: Member, caller: Member) -> MemberOut:
    joined = member.user_id is not None

    return MemberOut(
        id=member.id,
        email=member.invited_email,
        role=member.role,
        joined=joined,
        token=None if joined else member.token,
        removable=is_owner(caller) and not is_owner(member),
        created_at=member.created_at,
    )


@router.get("")
async def list_members(company_id: UUID, user: CurrentUser, page: PageParams) -> list[MemberOut]:
    company, caller = await require_company(user, company_id)
    rows = await members.list_for_company(company.id, page.offset, page.limit)

    return [member_out(member, caller) for member in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
async def invite_member(company_id: UUID, body: MemberIn, user: CurrentUser) -> MemberOut:
    """The owner invites an admin or a viewer, who is emailed the join link; the role applies
    once the invite is accepted."""
    company, caller = await require_company(user, company_id)

    if not is_owner(caller):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can add members")

    email = str(body.email).lower()

    if email == user.email.lower():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You're already a member")

    if any(member.invited_email == email for member in company.members):
        raise HTTPException(status.HTTP_409_CONFLICT, "That email is already invited")

    if sum(member.user_id is None for member in company.members) >= MAX_PENDING_INVITES:
        raise HTTPException(status.HTTP_409_CONFLICT, TOO_MANY_PENDING)

    if not await billing.company_paid(company.id):
        key = f"rate:member-invites:{company.id}"
        await hit(get_redis(), key, MEMBER_INVITES_PER_UNPAID_DAY, DAY_SECONDS)

    # The invite emails the member, so it counts toward the owner's email limits.
    await hit_emails(
        get_redis(),
        user.uid,
        f"member:{company.id}:{email}",
        settings.email_hourly_limit,
        settings.email_daily_limit,
        settings.email_recipient_daily_limit,
    )
    sender = {
        "company": company.name,
        "company_id": str(company.id),
        "logo_path": logo_path(company),
        "inviter": user.name or user.email,
        "language": user.language,
    }

    member = await members.add(company.id, email, body.role, sender)
    # The email goes out now; the outbox's regular run sends it if this fails.
    await outbox_service.flush_quietly()

    return member_out(member, caller)


async def owned_member(user: CurrentUser, company_id: UUID, member_id: UUID) -> Member:
    """A member or pending invite the owner manages; never the owner."""
    company, caller = await require_company(user, company_id)
    member = next((item for item in company.members if item.id == member_id), None)

    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Member not found")

    if not is_owner(caller):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can manage members")

    if is_owner(member):
        raise HTTPException(status.HTTP_409_CONFLICT, "The owner can't be changed")

    return member


@router.put("/{member_id}/role", status_code=status.HTTP_204_NO_CONTENT)
async def change_role(
    company_id: UUID, member_id: UUID, body: MemberRoleIn, user: CurrentUser
) -> None:
    """The owner makes an admin a viewer or the other way round. A new viewer's automatic
    top-up goes off, as viewers spend no credits."""
    member = await owned_member(user, company_id, member_id)

    if body.role == Role.VIEWER and member.user_id is not None:
        await billing.turn_off_auto_top_up(company_id, member.user_id)

    await members.set_role(member.id, body.role)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(company_id: UUID, member_id: UUID, user: CurrentUser) -> None:
    """The owner removes a member or withdraws a pending invite; never the owner. An automatic
    top-up paid with the removed member's card goes off, so it's never charged again."""
    member = await owned_member(user, company_id, member_id)

    if member.user_id is not None:
        await billing.turn_off_auto_top_up(company_id, member.user_id)

    await members.remove(member.id)


@router.get("/invites/{token}")
async def get_admin_invite(token: str, user: OptionalUser) -> AdminInviteOut:
    """Open to visitors, so they see what they're invited to before signing in; the invited
    email only once signed in, so a visitor with the link doesn't learn it."""
    found = await members.get_by_token(token)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    member, company = found

    return AdminInviteOut(
        company_name=company.name,
        email=member.invited_email if user else None,
        joined=member.user_id is not None,
    )


@router.post("/invites/{token}/accept", status_code=status.HTTP_204_NO_CONTENT)
async def accept_admin_invite(token: str, user: CurrentUser) -> None:
    """Only the invited email can accept, so a forwarded link is useless to anyone else."""
    found = await members.get_by_token(token)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    member, company = found

    if not user.email_verified or user.email.lower() != member.invited_email:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This invite was sent to a different email address"
        )

    await members.accept(member, company, user.uid)
    # The owner's notification goes out now; the outbox's regular run sends it if this fails.
    await outbox_service.flush_quietly()
