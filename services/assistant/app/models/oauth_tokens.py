from mcp.server.auth.provider import AccessToken, AuthorizationCode, RefreshToken


class Code(AuthorizationCode):
    """A code the user's allowing gave the app, with what the connection is called."""

    client_name: str
    redirect_host: str


class Refresh(RefreshToken):
    grant_id: str


class Access(AccessToken):
    grant_id: str
    client_name: str
