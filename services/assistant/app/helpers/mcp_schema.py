import mcp_types as types

from app.models.tools import Tool

# Writes that leave the same result when repeated.
IDEMPOTENT_METHODS = ("PUT", "DELETE")


def mcp_tool(tool: Tool) -> types.Tool:
    """A registry tool as an AI app sees it: its function definition's name, description and
    parameters, and hints for the app's own approval prompt (a read, a write, one that can't be
    undone). Every tool works on prepza alone, never the open web."""
    function = tool.definition["function"]
    read_only = tool.method == "GET"
    annotations = types.ToolAnnotations(
        read_only_hint=read_only,
        destructive_hint=None if read_only else tool.destructive,
        idempotent_hint=None if read_only else tool.method in IDEMPOTENT_METHODS,
        open_world_hint=False,
    )

    return types.Tool(
        name=tool.name,
        description=function["description"],
        input_schema=function["parameters"],
        annotations=annotations,
    )
