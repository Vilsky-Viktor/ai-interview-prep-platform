# The assistant's tools: user-facing GET routes of the other services, called with the user's own
# token, so roles and every other rule apply there unchanged. Each entry names its service and
# route (the path as that service sees it, in its snapshot in app/openapi/), and:
# - params: the route's parameters the model may set (every required one among them);
# - fields: the keys the model reads, at every level of the data (all when left out);
# - max_items: the longest list it reads (DEFAULT_MAX_ITEMS when left out); a `limit` the model
#   sets is capped at it;
# - max_length: the longest string it reads (MAX_STRING_LENGTH when left out);
# - render: the kind of block the panel shows for the result, and link: the page each item (or,
#   for "link", the result) opens, filled only from ids in the arguments and the data;
# - description: what the model is told the tool does (the route's docstring when left out).
# A new tool is a new entry here; scripts/assistant-openapi.sh refreshes the snapshots.


from app.constants.actions import ACTIONS
from app.constants.company_tools import COMPANY_TOOLS
from app.constants.detail_tools import DETAIL_TOOLS

TOOLS = {
    **COMPANY_TOOLS,
    **DETAIL_TOOLS,
    **ACTIONS,
    "get_price_catalog": {
        "service": "billing",
        "method": "GET",
        "path": "/catalog",
        "params": [],
        # Not Paddle's settings.
        "fields": [
            "currency",
            "candidate_credits",
            "candidate_prices",
            "candidate_cents_min",
            "candidate_cents_max",
            "welcome_company",
            "free_candidates",
            "referral_company",
            "from_dollars",
            "cents",
            "products",
            "key",
            "title",
            "price_cents",
            "credits",
            "candidates",
            "candidate_cents",
        ],
        "render": "link",
        "link": "/pricing",
    },
    "list_ats_connections": {
        "service": "ats",
        "method": "GET",
        "path": "/connections",
        "params": ["company_id"],
        "render": "link",
        "link": "/companies/{company_id}/integrations",
    },
    "list_ats_links": {
        "service": "ats",
        "method": "GET",
        "path": "/links",
        "params": ["company_id"],
        "render": "link",
        "link": "/companies/{company_id}/integrations",
    },
    "list_ats_jobs": {
        "service": "ats",
        "method": "GET",
        "path": "/{provider}/jobs",
        "params": ["provider", "company_id"],
        "render": "link",
        "link": "/companies/{company_id}/integrations/{provider}",
    },
    "get_slack": {
        "service": "notifications",
        "method": "GET",
        "path": "/slack",
        "params": ["company_id"],
        "fields": ["connected", "status", "team", "channel", "kinds"],
        "render": "link",
        "link": "/companies/{company_id}/integrations/slack",
    },
    "get_api_settings": {
        "service": "api",
        "method": "GET",
        "path": "/manage",
        "params": ["company_id"],
        # Never a web hook's URL, which can carry a secret.
        "fields": [
            "keys",
            "webhooks",
            "id",
            "name",
            "shown",
            "created_at",
            "expires_at",
            "expired",
            "last_used_at",
            "failing",
        ],
        "render": "link",
        "link": "/companies/{company_id}/integrations/api",
    },
    "list_notifications": {
        "service": "notifications",
        "method": "GET",
        "path": "/me",
        "params": [],
        "fields": [
            "items",
            "unread",
            "id",
            "kind",
            "data",
            "created_at",
            "title",
            "topic",
            "count",
            "credits",
            "email",
            "ats",
        ],
    },
    "get_me": {
        "service": "library",
        "method": "GET",
        "path": "/me",
        "params": [],
        "fields": ["email", "email_verified", "name", "language"],
        "render": "link",
        "link": "/settings",
    },
    "search_templates": {
        "service": "library",
        "method": "GET",
        "path": "/templates",
        "params": ["q", "level", "language", "offset", "limit"],
        "fields": ["id", "title", "level", "language", "topic_count"],
        "render": "link",
        "link": "/companies/{company_id}/templates",
    },
    "list_template_filters": {
        "service": "library",
        "method": "GET",
        "path": "/templates/filters",
        "params": [],
    },
    "get_template": {
        "service": "library",
        "method": "GET",
        "path": "/templates/{key}",
        "params": ["key"],
        "fields": ["id", "title", "level", "language", "topic_count", "topics", "subtopics"],
        "render": "link",
        "link": "/companies/{company_id}/templates/{id}",
    },
    "get_faq": {
        "service": "rounds",
        "method": "GET",
        "path": "/help/faq",
        "params": [],
        "fields": ["question", "answer"],
        "max_items": 100,
        "max_length": 2_000,
        "render": "link",
        "link": "/faq",
    },
    "get_platform_guide": {
        "service": "rounds",
        "method": "GET",
        "path": "/help/guide",
        "params": [],
        # The whole guide, which is long.
        "max_length": 100_000,
        "description": (
            "Everything prepza's help knows, in the user's language: what prepza can do and how "
            "to use each feature, the FAQ, today's prices and credits, payments and refunds, "
            "the terms of use and the privacy policy. Use it for how-to, pricing, policy and "
            '"what can prepza do" questions, before saying you don\'t know.'
        ),
        "render": "link",
        "link": "/faq",
    },
}
