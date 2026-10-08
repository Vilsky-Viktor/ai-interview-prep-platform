import re

# A value a link may hold: an id, never text (no slashes, dots, spaces or schemes).
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def link(template: str | None, values: dict) -> str | None:
    """A page of the app, from a tool's link template and ids from the arguments and the data;
    None when an id is missing or isn't one. Never built from the model's or the data's text."""
    if template is None:
        return None

    filled = {}

    for name in PLACEHOLDER.findall(template):
        value = values.get(name)

        if value is None or isinstance(value, bool) or not SAFE_ID.match(str(value)):
            return None

        filled[name] = str(value)

    return PLACEHOLDER.sub(lambda match: filled[match.group(1)], template)


def render_block(kind: str | None, template: str | None, data, context: dict) -> dict | None:
    """What the panel shows for a tool's result: {kind, items, links}. A "link" block is one
    link to the page that shows the result; the others show each item with its own link."""
    if kind is None:
        return None

    if kind == "link":
        # An action's result names what it made ({id} of a new company).
        found = link(template, {**context, **data} if isinstance(data, dict) else context)

        return {"kind": kind, "items": [], "links": [found] if found else []}

    items = [
        item for item in (data if isinstance(data, list) else [data]) if isinstance(item, dict)
    ]
    links = [link(template, {**context, **item}) for item in items]

    return {"kind": kind, "items": items, "links": links}


# What a stored block keeps of each item: ids only, enough to fetch it again with the viewer's
# token when the conversation is opened. Each id comes from the item's key, or else from the
# arguments the tool was called with (an interview's candidates carry only their own id).
REFERENCE_KEYS = {
    "candidate_rows": {"id": "id", "interview_id": "interview_id"},
    "scorecard_summary": {"id": "id", "interview_id": "interview_id"},
    "interview": {"id": "id"},
    "credits": {"company_id": "id"},
}


def reference(block: dict, arguments: dict) -> dict:
    """A block as a conversation stores it: its kind, its items' ids and its links (app paths
    made of ids), never the data it showed."""
    keys = REFERENCE_KEYS.get(block["kind"], {})
    refs = [
        {ref: str(item.get(key) or arguments.get(ref) or "") for ref, key in keys.items()}
        for item in block["items"]
    ]

    return {"kind": block["kind"], "refs": refs, "links": block["links"]}
