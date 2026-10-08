from app.constants.tool_calls import FORBIDDEN_PATH_PREFIXES

# What a parameter's schema keeps for the model; the rest (titles, defaults) is noise.
KEPT_KEYWORDS = ("type", "enum", "format", "maxLength", "minLength", "minimum", "maximum")


def check_route(name: str, entry: dict) -> None:
    """Refuses an allow-list entry the assistant must never call: anything but GET, and other
    services' or prepza's own team's routes."""
    if entry["method"] != "GET":
        raise ValueError(f"Tool {name}: only GET routes are allowed, not {entry['method']}")

    if entry["path"].startswith(FORBIDDEN_PATH_PREFIXES):
        raise ValueError(f"Tool {name}: {entry['path']} is not a user-facing route")


def resolve(schema: dict, components: dict) -> dict:
    """The schema a $ref points to, and the non-null choice of an optional one."""
    if "$ref" in schema:
        return resolve(components[schema["$ref"].rsplit("/", 1)[-1]], components)

    choices = [choice for choice in schema.get("anyOf", []) if choice.get("type") != "null"]

    if len(choices) == 1:
        return resolve(
            {**choices[0], **{k: v for k, v in schema.items() if k != "anyOf"}}, components
        )

    return schema


def parameter_schema(parameter: dict, components: dict) -> dict:
    schema = resolve(parameter["schema"], components)
    kept = {key: schema[key] for key in KEPT_KEYWORDS if key in schema}
    description = parameter.get("description") or schema.get("description")

    if description:
        kept["description"] = description

    return kept


def definition(name: str, entry: dict, operation: dict, components: dict, max_items: int) -> dict:
    """The function the model is given for a tool: its allow-listed parameters as the route
    declares them, `limit` capped at the tool's `max_items`."""
    declared = {parameter["name"]: parameter for parameter in operation.get("parameters", [])}
    properties = {}

    for param in entry["params"]:
        if param not in declared:
            raise ValueError(f"Tool {name}: the route has no parameter {param}")

        properties[param] = parameter_schema(declared[param], components)

    if "limit" in properties:
        properties["limit"]["maximum"] = min(
            properties["limit"].get("maximum", max_items), max_items
        )
        properties["limit"]["description"] = f"Number of items to return, up to {max_items}"

    required = [param for param, parameter in declared.items() if parameter.get("required")]
    missing = [param for param in required if param not in properties]

    if missing:
        raise ValueError(f"Tool {name}: required parameters not allowed: {missing}")

    description = entry.get("description") or operation.get("description") or operation["summary"]

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }
