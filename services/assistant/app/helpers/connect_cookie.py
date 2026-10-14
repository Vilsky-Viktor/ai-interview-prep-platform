from urllib.parse import parse_qs, urlparse

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.config.settings import settings
from app.constants.mcp import CONNECT_COOKIE, CONNECT_COOKIE_PATH, CONNECT_PATH, REQUEST_SECONDS


def request_of(location: str) -> str | None:
    """The request id a redirect to the consent page carries."""
    url = urlparse(location)

    if url.path != CONNECT_PATH:
        return None

    return (parse_qs(url.query).get("request") or [None])[0]


def cookie(request_id: str) -> str:
    secure = "; Secure" if settings.site_url.startswith("https://") else ""

    return (
        f"{CONNECT_COOKIE}={request_id}; Path={CONNECT_COOKIE_PATH}; Max-Age={REQUEST_SECONDS};"
        f" HttpOnly; SameSite=Lax{secure}"
    )


class MarkBrowser:
    """Wraps /authorize: its redirect to the consent page also marks the browser that asked
    (services/connections.py approve() requires it)."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def marked(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                request_id = request_of(headers.get(b"location", b"").decode())

                if request_id:
                    marking = (b"set-cookie", cookie(request_id).encode())
                    message["headers"] = [*message.get("headers", []), marking]

            await send(message)

        await self.app(scope, receive, marked)
