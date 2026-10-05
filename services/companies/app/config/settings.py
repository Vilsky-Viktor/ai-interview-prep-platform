from prepza_common.settings import ServiceSettings
from pydantic import Field


class Settings(ServiceSettings):
    # The API description (/docs, /openapi.json) lists every route, internal ones too, so it's
    # served only in development, where the frontend's types are generated from it.
    api_docs: bool = False
    database_url: str
    redis_url: str
    service_secret: str
    # Invite emails a user may send (shares and candidate invites together), and invites one
    # address may get a day for the same thing; 0 turns a limit off.
    email_hourly_limit: int = Field(default=100, ge=0)
    email_daily_limit: int = Field(default=200, ge=0)
    email_recipient_daily_limit: int = Field(default=3, ge=0)
    generation_url: str
    library_url: str
    rounds_url: str
    billing_url: str

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
