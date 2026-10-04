from prepza_common.settings import ServiceSettings
from pydantic import Field


class Settings(ServiceSettings):
    # The API description (/docs, /openapi.json) lists every route, internal ones too, so it's
    # served only in development, where the frontend's types are generated from it.
    api_docs: bool = False
    database_url: str
    redis_url: str
    library_url: str
    billing_url: str
    service_secret: str
    llm_limit: int = Field(default=400, ge=0)
    llm_window_seconds: int = Field(default=3_600, gt=0)
    # Each AI task has its own model and effort: how hard a reasoning model thinks, "none",
    # "minimal", "low", "medium" or "high".
    # The tutor, which explains hard questions and their what-ifs: Sol at low reasoning answered
    # every complex follow-up correctly in testing, where Luna got some wrong.
    tutor_model: str = "gpt-6.1-sol"
    tutor_reasoning_effort: str = "low"
    # The FAQ's help chat, free for everyone and answering from fixed texts: fast and cheap.
    help_model: str = "gpt-6-luna"
    help_reasoning_effort: str = "none"
    # The FAQ page's help chat is free and open to visitors: messages per signed-in account an
    # hour, and in all a day, which caps what it can cost. Cloud Armor limits each visitor's IP.
    help_user_limit: int = Field(default=30, ge=0)
    help_daily_limit: int = Field(default=5_000, ge=0)
    # Contact page messages a day in all, so a flood can't bury the inbox. Cloud Armor limits
    # each visitor's IP.
    contact_daily_limit: int = Field(default=200, ge=0)

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
