import logging
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    RefreshToken,
    TokenError,
)
from mcp.server.auth.settings import AuthSettings
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from prepza_common.analytics import track
from prepza_common.rate_limit import hit
from prepza_common.tokens import hashed, new_token

from app.config.settings import settings
from app.constants.limits import TOKEN_REQUESTS_PER_CLIENT_MINUTE
from app.constants.mcp import (
    ACCESS_SECONDS,
    CONNECT_PATH,
    FUNNEL_CLIENTS,
    MCP_PATH,
    MCP_SCOPE,
    MINUTE_SECONDS,
    REFRESH_SECONDS,
    TOKEN_BYTES,
    TOKEN_PREFIX,
)
from app.helpers.mcp_clients import describe_client
from app.integrations.redis import get_redis
from app.models.oauth import McpGrant
from app.storage import oauth, oauth_requests

logger = logging.getLogger(__name__)


def resource_url() -> str:
    """The MCP endpoint, the one resource prepza's access is for."""
    return settings.site_url.rstrip("/") + MCP_PATH


def auth_settings() -> AuthSettings:
    """The site as the authorization server (its root is the issuer) and the MCP endpoint as
    the resource, as URLs the SDK writes without a trailing slash."""
    return AuthSettings(
        issuer_url=settings.site_url.rstrip("/"),
        resource_server_url=resource_url(),
        validate_token_resource=True,
    )


def funnel_client(client_name: str) -> str:
    return FUNNEL_CLIENTS.get(client_name, "other")


class Code(AuthorizationCode):
    """A code the user's allowing gave the app, with what the connection is called."""

    client_name: str
    redirect_host: str


class Refresh(RefreshToken):
    grant_id: str


class Access(AccessToken):
    grant_id: str
    client_name: str


def new_tokens() -> tuple[OAuthToken, dict]:
    """A new access and refresh token for the app, and what the connection keeps of them."""
    access, access_hash = new_token(TOKEN_PREFIX, TOKEN_BYTES)
    refresh, refresh_hash = new_token(TOKEN_PREFIX, TOKEN_BYTES)
    now = datetime.now(UTC)
    kept = {
        "access_hash": access_hash,
        "access_expires_at": now + timedelta(seconds=ACCESS_SECONDS),
        "refresh_hash": refresh_hash,
        "refresh_expires_at": now + timedelta(seconds=REFRESH_SECONDS),
    }
    token = OAuthToken(
        access_token=access, expires_in=ACCESS_SECONDS, scope=MCP_SCOPE, refresh_token=refresh
    )

    return token, kept


async def limit_tokens(client_id: str) -> None:
    """Counts one token request of the app; over the limit, refused. With Redis down, not
    counted rather than refused."""
    key = f"rate:assistant:mcp:token:{client_id}"

    try:
        await hit(get_redis(), key, TOKEN_REQUESTS_PER_CLIENT_MINUTE, MINUTE_SECONDS)
    except HTTPException:
        raise TokenError("invalid_request", "Too many token requests; try again in a minute.")
    except Exception:
        logger.warning("Token request limit skipped, Redis failed", exc_info=True)


class Provider:
    """prepza as the authorization server of AI apps (the MCP SDK's
    OAuthAuthorizationServerProvider): apps register themselves, the user allows them on the
    site's /connect page, and they get opaque tokens, kept as hashes, one connection each."""

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        found = await oauth.get_client(client_id)

        return OAuthClientInformationFull.model_validate(found) if found else None

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        info = client_info.model_dump(mode="json", exclude_none=True)
        await oauth.save_client(client_info.client_id, info)

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        """Keeps the request for the user to answer, and sends them to the consent page."""
        if params.resource is not None and params.resource.rstrip("/") != resource_url():
            raise AuthorizeError("invalid_target", "prepza only grants access to its MCP server.")

        name, host, known = describe_client(client.client_name, str(params.redirect_uri))
        request_id = secrets.token_urlsafe(24)
        request = {
            "client_id": client.client_id,
            "client_name": name,
            "redirect_host": host,
            "known_client": known,
            "redirect_uri": str(params.redirect_uri),
            "redirect_uri_provided_explicitly": params.redirect_uri_provided_explicitly,
            "code_challenge": params.code_challenge,
            "state": params.state,
            "scopes": params.scopes or [MCP_SCOPE],
        }
        await oauth_requests.save_request(request_id, request)

        return f"{settings.site_url.rstrip('/')}{CONNECT_PATH}?request={request_id}"

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> Code | None:
        found = await oauth_requests.peek_code(hashed(authorization_code))

        if found is None or found["client_id"] != client.client_id:
            return None

        return Code(
            code=authorization_code,
            scopes=found["scopes"],
            expires_at=found["expires_at"],
            client_id=found["client_id"],
            code_challenge=found["code_challenge"],
            redirect_uri=found["redirect_uri"],
            redirect_uri_provided_explicitly=found["redirect_uri_provided_explicitly"],
            resource=resource_url(),
            subject=found["user_id"],
            client_name=found["client_name"],
            redirect_host=found["redirect_host"],
        )

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: Code
    ) -> OAuthToken:
        """The code, once, for the connection's first tokens."""
        await limit_tokens(client.client_id)

        if await oauth_requests.take_code(hashed(authorization_code.code)) is None:
            raise TokenError("invalid_grant", "authorization code does not exist")

        token, kept = new_tokens()
        grant = McpGrant(
            user_id=authorization_code.subject,
            client_id=client.client_id,
            client_name=authorization_code.client_name,
            redirect_host=authorization_code.redirect_host,
            **kept,
        )
        await oauth.add_grant(grant)
        client_label = funnel_client(authorization_code.client_name)
        await track("mcp_connected", user_id=authorization_code.subject, client=client_label)

        return token

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> Refresh | None:
        grant = await oauth.by_refresh(hashed(refresh_token))

        if grant is None or grant.client_id != client.client_id:
            return None

        return Refresh(
            token=refresh_token,
            client_id=grant.client_id,
            scopes=[MCP_SCOPE],
            expires_at=int(grant.refresh_expires_at.timestamp()),
            resource=resource_url(),
            subject=grant.user_id,
            grant_id=str(grant.id),
        )

    async def exchange_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: Refresh, scopes: list[str]
    ) -> OAuthToken:
        """New tokens for the connection; the old ones stop working. Of two refreshes with the
        same token, the second is refused."""
        await limit_tokens(client.client_id)
        token, kept = new_tokens()

        if not await oauth.rotate(UUID(refresh_token.grant_id), hashed(refresh_token.token), kept):
            raise TokenError("invalid_grant", "refresh token does not exist")

        return token

    async def load_access_token(self, token: str) -> Access | None:
        grant = await oauth.by_access(hashed(token))

        if grant is None or grant.access_expires_at <= datetime.now(UTC):
            return None

        return Access(
            token=token,
            client_id=grant.client_id,
            scopes=[MCP_SCOPE],
            expires_at=int(grant.access_expires_at.timestamp()),
            resource=resource_url(),
            subject=grant.user_id,
            grant_id=str(grant.id),
            client_name=grant.client_name,
        )

    async def revoke_token(self, token: Access | Refresh) -> None:
        """The app disconnects itself (it was removed there): the connection goes."""
        removed = await oauth.remove(UUID(token.grant_id))

        if removed is not None:
            await track("mcp_disconnected", user_id=removed.user_id, by="client")
