import logging

from fastapi import HTTPException
from mcp.server.auth.handlers.metadata import MetadataHandler
from mcp.server.auth.middleware.client_auth import AuthenticationError, ClientAuthenticator
from mcp.server.auth.routes import (
    REGISTRATION_PATH,
    REVOCATION_PATH,
    build_metadata,
    cors_middleware,
    create_auth_routes,
    create_protected_resource_routes,
)
from mcp.server.auth.settings import ClientRegistrationOptions, RevocationOptions
from prepza_common.client_ip import client_ip
from prepza_common.constants import DAY_SECONDS, HOUR_SECONDS
from prepza_common.rate_limit import hit
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send

from app.constants.limits import REGISTRATIONS_PER_DAY, REGISTRATIONS_PER_IP_HOUR
from app.constants.mcp import MCP_SCOPE
from app.integrations.redis import get_redis
from app.services.oauth_provider import Provider, auth_settings

logger = logging.getLogger(__name__)

AUTHORIZATION_METADATA_PATH = "/.well-known/oauth-authorization-server"
# Some apps look for the resource's metadata at the root, without the resource's path.
ROOT_RESOURCE_METADATA_PATH = "/.well-known/oauth-protected-resource"
# Apps registered without a secret (most do: Claude Code, MCP Inspector) are welcome too.
AUTH_METHODS = ["none", "client_secret_post", "client_secret_basic"]


class LimitedRegistrations:
    """Registration, counted per address and for everyone; over a limit, refused (429). With
    Redis down, not counted rather than refused."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["method"] == "POST":
            redis = get_redis()
            key = f"rate:assistant:mcp:register:{client_ip(Request(scope))}"

            try:
                await hit(redis, key, REGISTRATIONS_PER_IP_HOUR, HOUR_SECONDS)
                await hit(redis, "rate:assistant:mcp:register", REGISTRATIONS_PER_DAY, DAY_SECONDS)
            except HTTPException as error:
                body = {"error": "invalid_client_metadata", "error_description": error.detail}
                await JSONResponse(body, status_code=error.status_code)(scope, receive, send)

                return
            except Exception:
                logger.warning("Registration limit skipped, Redis failed", exc_info=True)

        await self.app(scope, receive, send)


async def revoke(request: Request) -> Response:
    """An app revoking its access or refresh token (RFC 7009): the connection goes. Answered
    here rather than by the SDK's handler, which requires a client_secret field that apps
    registered without a secret don't send. An unknown token is a 200 too."""
    provider = Provider()

    try:
        client = await ClientAuthenticator(provider).authenticate_request(request)
    except AuthenticationError as error:
        body = {"error": "unauthorized_client", "error_description": error.message}

        return JSONResponse(body, status_code=401)

    token = (await request.form()).get("token")

    if not isinstance(token, str) or not token:
        return JSONResponse({"error": "invalid_request"}, status_code=400)

    found = await provider.load_access_token(token) or await provider.load_refresh_token(
        client, token
    )

    if found is not None and found.client_id == client.client_id:
        await provider.revoke_token(found)

    return Response(status_code=200, headers={"Cache-Control": "no-store"})


def routes() -> list[Route]:
    """prepza as the authorization server of AI apps, at the site's root (the MCP SDK's
    handlers): its metadata, /authorize (to the consent page), /token, /register and /revoke; and
    the MCP endpoint's resource metadata, which names it."""
    urls = auth_settings()
    issuer = urls.issuer_url
    registration = ClientRegistrationOptions(
        enabled=True, valid_scopes=[MCP_SCOPE], default_scopes=[MCP_SCOPE]
    )
    revocation = RevocationOptions(enabled=True)
    metadata = build_metadata(issuer, None, registration, revocation)
    metadata.token_endpoint_auth_methods_supported = AUTH_METHODS
    metadata.revocation_endpoint_auth_methods_supported = AUTH_METHODS
    found = []

    for route in create_auth_routes(Provider(), issuer, None, registration, revocation):
        if route.path == AUTHORIZATION_METADATA_PATH:
            handler = cors_middleware(MetadataHandler(metadata).handle, ["GET", "OPTIONS"])
            route = Route(route.path, endpoint=handler, methods=["GET", "OPTIONS"])
        elif route.path == REGISTRATION_PATH:
            limited = LimitedRegistrations(route.app)
            route = Route(route.path, endpoint=limited, methods=["POST", "OPTIONS"])
        elif route.path == REVOCATION_PATH:
            handler = cors_middleware(revoke, ["POST", "OPTIONS"])
            route = Route(route.path, endpoint=handler, methods=["POST", "OPTIONS"])

        found.append(route)

    resource = create_protected_resource_routes(
        urls.resource_server_url, [issuer], scopes_supported=[MCP_SCOPE], resource_name="prepza"
    )
    root = Route(ROOT_RESOURCE_METADATA_PATH, endpoint=resource[0].app, methods=["GET", "OPTIONS"])

    return [*found, *resource, root]
