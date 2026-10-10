# AI apps (Claude, ChatGPT, ...) connected over MCP: they call the assistant's tools as the user,
# with an access token prepza issued once the user allowed them (OAuth 2.1 with PKCE).

# The one scope an app is given: everything the user may do, as they would in the app.
MCP_SCOPE = "prepza"
# Where the MCP endpoint is, on the site (the resource the access is for), and where the user
# allows or denies an app (the frontend's page).
MCP_PATH = "/mcp"
CONNECT_PATH = "/connect"

MINUTE_SECONDS = 60

# Tokens: this prefix and random bytes; only their hashes are kept.
TOKEN_PREFIX = "pzm_"
TOKEN_BYTES = 32
CODE_BYTES = 32
# How long each lasts: the access an hour, the refresh 90 days from its last use (each refresh
# makes new ones); a code 5 minutes, and a request waiting for the user 10.
ACCESS_SECONDS = 60 * 60
REFRESH_SECONDS = 90 * 24 * 60 * 60
CODE_SECONDS = 5 * 60
REQUEST_SECONDS = 10 * 60
# A connection's "last used" is written at most this often.
LAST_USED_EVERY_SECONDS = 60 * 60
# An app that registered but has had no connection for this many days is deleted.
IDLE_CLIENT_DAYS = 30
# The longest app name kept from what an app says about itself.
MAX_CLIENT_NAME_LENGTH = 80

# Redis: a request waiting for the user, a code waiting to be exchanged, and the day an app was
# last counted as active for a user (the funnel's mcp_active, once a day).
REQUEST_KEY = "mcp:request:{request_id}"
CODE_KEY = "mcp:code:{code_hash}"
ACTIVE_KEY = "mcp:active:{user_id}:{client}"

# Apps known by the address they return to: the name the consent page shows, whatever the app
# says it's called. Any other address gets a warning there.
KNOWN_CLIENTS = {
    "claude.ai": "Claude",
    "claude.com": "Claude",
    "chatgpt.com": "ChatGPT",
}
# An app on the user's own computer (Claude Code, Claude Desktop, MCP Inspector): its code never
# leaves that computer, so it's known too, named as it says.
LOOPBACK_HOSTS = ("localhost", "127.0.0.1", "[::1]", "::1")
LOCAL_APP = "Local app"
# What the funnel calls each app.
FUNNEL_CLIENTS = {"Claude": "claude", "ChatGPT": "chatgpt"}

# A request to connect once it's answered or expired, and a connection that isn't the user's:
# the consent page and the connections list say what it means.
NOT_FOUND = "Not found"

# Tools an app never gets: deleting the account or a company (with its paid credits) is done in
# the app only. The panel's own tools (show, sign_out) aren't tools of the registry at all.
MCP_EXCLUDED = frozenset({"delete_account", "delete_company"})
EXCLUDED_TOOL = (
    "This can only be done in prepza itself: deleting an account or a company can't be undone."
)
# What an app reads when the connection's account is gone or disabled.
ACCOUNT_GONE = "This prepza account no longer exists or is disabled."
# The tool that changes the user's language: their kept sign-in is dropped after it, so the next
# calls answer in the new one.
UPDATE_LANGUAGE = "update_language"
