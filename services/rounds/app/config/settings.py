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
    llm_model: str = "gpt-6-luna"
    # The FAQ page's help chat is free and open to visitors: messages per signed-in account an
    # hour, and in all a day, which caps what it can cost. Cloud Armor limits each visitor's IP.
    help_user_limit: int = Field(default=30, ge=0)
    help_daily_limit: int = Field(default=5_000, ge=0)

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
