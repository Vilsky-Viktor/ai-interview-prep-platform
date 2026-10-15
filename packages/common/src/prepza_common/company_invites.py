# Inviting a candidate in the companies service as a member would: the api (an API key's maker)
# and the ats (whoever connected the ATS) do it through companies' one internal route.
from uuid import UUID

from prepza_common import http
from prepza_common.http import passed_on


async def invite(
    companies_url: str, token: str, interview_id: UUID, body: dict, refusals: set[int]
) -> UUID:
    """The invite's id. `body` names the email and `sender_id`, and what else the caller sets;
    companies' refusals in `refusals` reach the caller with their status and reason."""
    response = await http.get_client().post(
        f"{companies_url}/internal/interviews/{interview_id}/invites",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )

    return UUID(passed_on(response, refusals).json()["invite_id"])
