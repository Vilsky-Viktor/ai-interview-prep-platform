from dataclasses import dataclass


@dataclass(frozen=True)
class Tool:
    """A tool the model may call, built from its allow-list entry and its route's snapshot."""

    name: str
    service: str
    path: str
    path_params: tuple[str, ...]
    query_params: tuple[str, ...]
    # The function definition the model is given (OpenAI's tool format).
    definition: dict
    fields: frozenset[str] | None
    max_items: int
    max_length: int
    render: str | None
    link: str | None

    @property
    def parameters(self) -> dict:
        return self.definition["function"]["parameters"]


@dataclass(frozen=True)
class ToolResult:
    """One call's outcome: what the model reads, and the block the panel shows."""

    tool: str
    arguments: dict
    # The service's status; None when it didn't answer (or the arguments were refused).
    status_code: int | None
    # {"data", "source"} on success, {"error", "detail"} otherwise.
    content: dict
    block: dict | None
    duration_ms: int

    @property
    def succeeded(self) -> bool:
        return self.status_code is not None and 200 <= self.status_code < 300
