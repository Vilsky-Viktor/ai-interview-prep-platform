# Each tool call waits this long for its service (an ATS's job list is a live call to the ATS).
TOOL_TIMEOUT_SECONDS = 20
# Tool calls one step of a turn runs at the same time.
MAX_PARALLEL_TOOL_CALLS = 4
# What a tool's data may hold for the model: lists of at most a tool's max_items (or
# DEFAULT_MAX_ITEMS), strings of at most MAX_STRING_LENGTH characters.
DEFAULT_MAX_ITEMS = 20
MAX_STRING_LENGTH = 300
# Routes the assistant never calls: other services' and prepza's own team's.
FORBIDDEN_PATH_PREFIXES = ("/internal", "/superadmin")
# The header that tells companies a read came through the assistant (audited as such), holding a
# service token signed for companies, so it can't be forged.
ASSISTANT_HEADER = "X-Assistant"
# Where each tool's service is: the settings attribute holding its base URL.
SERVICE_URLS = {
    "companies": "companies_url",
    "billing": "billing_url",
    "library": "library_url",
    "notifications": "notifications_url",
    "ats": "ats_url",
    "api": "api_url",
    "rounds": "rounds_url",
}
# What the model reads when a tool's service didn't answer.
SERVICE_UNAVAILABLE = "The service didn't answer. Try again later."
INVALID_ARGUMENTS = "Invalid arguments"
UNKNOWN_TOOL = "There is no such tool."
