from dataclasses import dataclass, field
from uuid import UUID

from app.models.tools import ToolResult


@dataclass
class Answer:
    """The assistant's answer as a turn builds it: its text so far, the blocks the panel shows,
    the tools it called and the tokens its model calls used."""

    parts: list[str] = field(default_factory=list)
    blocks: list[dict] = field(default_factory=list)
    results: list[ToolResult] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def content(self) -> str:
        return "".join(self.parts)

    @property
    def tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class Turn:
    """One message's turn: whose it is, in which conversation and language. The token is the
    user's own, which the tools send on; it's never stored, logged or shown to the model."""

    conversation_id: UUID
    user_id: str
    company_id: UUID | None
    token: str = field(repr=False)
    language: str
