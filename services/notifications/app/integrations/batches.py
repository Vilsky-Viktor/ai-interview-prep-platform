from prepza_common import http

from app.constants.member_emails import MAX_IDS_PER_CALL


async def post_ids(url: str, token: str, field: str, ids: list[str], answer: str) -> list[dict]:
    """Posts the ids to another service's batch route as `field`, MAX_IDS_PER_CALL at a time
    (one call for the usual few), and returns the lists under `answer` together."""
    found = []

    for start in range(0, len(ids), MAX_IDS_PER_CALL):
        response = await http.get_client().post(
            url,
            json={field: ids[start : start + MAX_IDS_PER_CALL]},
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        found += response.json()[answer]

    return found
