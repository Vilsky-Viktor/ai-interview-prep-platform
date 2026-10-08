from functools import cache

import httpx

from app.constants.api import SIGNATURE_HEADER, WEBHOOK_TIMEOUT_SECONDS


@cache
def get_client() -> httpx.AsyncClient:
    """Web hooks' own client, keeping no connections: one opened for a host would otherwise be
    reused for another host at the same address, without checking that host's certificate."""
    return httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=0))


async def post(url: str, address: str, body: bytes, signature: str) -> None:
    """Sends an event to a company's endpoint at `address`, the one its host was checked to have
    (see public_address), with the host's name in the Host header and TLS (SNI and the
    certificate check), without following redirects; anything but a 2xx answer raises an
    httpx.HTTPError."""
    target = httpx.URL(url)
    response = await get_client().post(
        target.copy_with(host=address),
        content=body,
        headers={
            "Host": target.netloc.decode(),
            "Content-Type": "application/json",
            SIGNATURE_HEADER: signature,
        },
        extensions={"sni_hostname": target.raw_host.decode()},
        timeout=WEBHOOK_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
