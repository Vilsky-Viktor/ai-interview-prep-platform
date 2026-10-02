from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    firebase_project_id: str
    firebase_auth_emulator_host: str = ""
    # The API description (/docs, /openapi.json) lists every route, internal ones too, so it's
    # served only in development, where the frontend's types are generated from it.
    api_docs: bool = False
    database_url: str
    redis_url: str
    service_secret: str
    # Invite emails a user may send (shares and candidate invites together), and invites one
    # address may get a day for the same thing; 0 turns a limit off.
    email_hourly_limit: int = Field(default=30, ge=0)
    email_daily_limit: int = Field(default=200, ge=0)
    email_recipient_daily_limit: int = Field(default=3, ge=0)
    generation_url: str
    library_url: str
    rounds_url: str
    # Off in tests, which have no Redis.
    consume_events: bool = True

    @model_validator(mode="after")
    def emulator_only_for_demo_projects(self) -> "Settings":
        # With the emulator host set, firebase_admin accepts unsigned tokens.
        if self.firebase_auth_emulator_host and not self.firebase_project_id.startswith("demo-"):
            raise ValueError("FIREBASE_AUTH_EMULATOR_HOST is only allowed for a demo- project")

        return self

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
