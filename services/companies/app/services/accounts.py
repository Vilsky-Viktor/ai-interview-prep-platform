from app.constants.roles import Role
from app.services import candidate_billing, company_deletion
from app.storage import accounts


async def delete_user(user_id: str, email: str) -> None:
    """A company whose only owner leaves is deleted with them; other memberships just end.
    The user's candidate invites stay with the companies, without their email. Safe to repeat."""
    for member, company, owner_count in await accounts.memberships(user_id):
        if member.role == Role.OWNER and owner_count == 1:
            await company_deletion.delete_company(company.id)
        else:
            await accounts.remove_member(member.id)

    await candidate_billing.release_unfinished(await accounts.candidate_invites(user_id, email))
    await accounts.forget_candidate(user_id, email)
