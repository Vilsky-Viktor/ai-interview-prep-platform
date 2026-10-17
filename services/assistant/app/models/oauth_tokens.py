from mcp.server.auth.provider import AccessToken, AuthorizationCode, RefreshToken
from pydantic import Field


class Code(AuthorizationCode):
    """A code the user's allowing gave the app, with what the connection is called."""

    client_name: str
    redirect_host: str


class Refresh(RefreshToken):
    grant_id: str


class Access(AccessToken):
    """An app's access (its connection, grant_id), or an AI agent's API key: the key's id, its
    company and permissions."""

    client_name: str
    grant_id: str | None = None
    key_id: str | None = None
    company_id: str | None = None
    permissions: list[str] = Field(default_factory=list)
