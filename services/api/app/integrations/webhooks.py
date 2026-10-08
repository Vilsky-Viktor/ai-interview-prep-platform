from prepza_common import http

from app.constants.api import SIGNATURE_HEADER, WEBHOOK_TIMEOUT_SECONDS


async def post(url: str, body: bytes, signature: str) -> None:
    """Sends an event to a company's endpoint, without following redirects; anything but a 2xx
    answer raises an httpx.HTTPError."""
    response = await http.get_client().post(
        url,
        content=body,
        headers={"Content-Type": "application/json", SIGNATURE_HEADER: signature},
        timeout=WEBHOOK_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
