from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams

from app.constants.roles import Role
from app.integrations import billing
from app.models.companies import Member
from app.schemas.companies import AdminInviteOut, MemberIn, MemberOut
from app.services.access import require_company
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
        removable=caller.role == Role.OWNER and member.role != Role.OWNER,
        created_at=member.created_at,
    )


@router.get("")
async def list_members(company_id: UUID, user: CurrentUser, page: PageParams) -> list[MemberOut]:
    company, caller = await require_company(user, company_id)
    rows = await members.list_for_company(company.id, page.offset, page.limit)

    return [member_out(member, caller) for member in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
async def invite_admin(company_id: UUID, body: MemberIn, user: CurrentUser) -> MemberOut:
    company, caller = await require_company(user, company_id)

    if caller.role != Role.OWNER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can add admins")

    email = str(body.email).lower()

    if email == user.email.lower():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You're already a member")

    if any(member.invited_email == email for member in company.members):
        raise HTTPException(status.HTTP_409_CONFLICT, "That email is already invited")

    return member_out(await members.add_admin(company.id, email), caller)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(company_id: UUID, member_id: UUID, user: CurrentUser) -> None:
    """The owner removes an admin or withdraws a pending invite; never the owner. An automatic
    top-up paid with the removed admin's card goes off, so it's never charged again."""
    company, caller = await require_company(user, company_id)
    member = next((item for item in company.members if item.id == member_id), None)

    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Member not found")

    if caller.role != Role.OWNER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can remove admins")

    if member.role == Role.OWNER:
        raise HTTPException(status.HTTP_409_CONFLICT, "The owner can't be removed")

    if member.user_id is not None:
        await billing.turn_off_auto_top_up(company.id, member.user_id)

    await members.remove(member.id)


@router.get("/invites/{token}")
async def get_admin_invite(token: str, user: CurrentUser) -> AdminInviteOut:
    found = await members.get_by_token(token)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    member, company = found

    return AdminInviteOut(
        company_name=company.name,
        email=member.invited_email,
        joined=member.user_id is not None,
    )


@router.post("/invites/{token}/accept", status_code=status.HTTP_204_NO_CONTENT)
async def accept_admin_invite(token: str, user: CurrentUser) -> None:
    """Only the invited email can accept, so a forwarded link is useless to anyone else."""
    found = await members.get_by_token(token)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    member, _ = found

    if not user.email_verified or user.email.lower() != member.invited_email:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This invite was sent to a different email address"
        )

    await members.accept(member, user.uid)
