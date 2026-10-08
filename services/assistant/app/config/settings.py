from prepza_common.settings import ServiceSettings
from pydantic import Field


class Settings(ServiceSettings):
    # The API description lists every route, internal ones too: development only.
    api_docs: bool = False
    # Conversations and their messages; Redis counts each user's messages and spending.
    database_url: str
    redis_url: str
    # Signs calls from other services (library deletes and exports a user's conversations).
    service_secret: str
    # OpenAI: the chat and speech-to-text. Empty in CI, where nothing calls OpenAI.
    openai_api_key: str = ""
    # The chat model, and how hard it thinks: "none", "minimal", "low", "medium" or "high".
    assistant_model: str = "gpt-6-luna"
    assistant_reasoning_effort: str = "low"
    # Turns a held voice message into text.
    transcribe_model: str = "gpt-4o-mini-transcribe"
    # Conversations nobody has added to for this many days are deleted.
    assistant_retention_days: int = Field(default=90, gt=0)
    # The services whose user-facing GET routes are the assistant's tools, called with the
    # user's own token.
    companies_url: str
    billing_url: str
    library_url: str
    notifications_url: str
    ats_url: str
    api_url: str
    rounds_url: str

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
