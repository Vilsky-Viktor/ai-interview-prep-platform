# Who may do what in a company, as the companies service answers it. The api, ats and
# notifications guard company pages with it, and keep API keys, web hooks and Slack working only
# while whoever made them is still an owner or admin.
from fastapi import HTTPException, status
from prepza_common import http


async def access(companies_url: str, token: str, company_id, user_id: str) -> dict:
    """What the user may do in the company: {"member": bool, "editor": bool} (an editor is an
    owner or admin). A company that's gone is one nobody may do anything in; companies failing
    otherwise raises."""
    response = await http.get_client().get(
        f"{companies_url}/internal/companies/{company_id}/access",
        params={"user_id": user_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        return {"member": False, "editor": False}

    response.raise_for_status()

    return response.json()


def require(found: dict, editor: bool) -> None:
    """A member may look; only an editor may change. Others get 404, as if the company weren't
    there; a viewer changing gets 403."""
    if not found["member"]:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    if editor and not found["editor"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Viewers can't change anything here")
