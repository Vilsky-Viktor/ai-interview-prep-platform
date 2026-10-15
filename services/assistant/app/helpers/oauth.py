from datetime import UTC, datetime, timedelta

from mcp.server.auth.settings import AuthSettings
from mcp.shared.auth import OAuthToken
from prepza_common.tokens import new_token

from app.config.settings import settings
from app.constants.mcp import (
    ACCESS_SECONDS,
    FUNNEL_CLIENTS,
    MCP_PATH,
    MCP_SCOPE,
    REFRESH_SECONDS,
    TOKEN_BYTES,
    TOKEN_PREFIX,
)


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
