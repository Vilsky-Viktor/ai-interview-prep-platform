from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    firebase_project_id: str
    firebase_auth_emulator_host: str = ""
    database_url: str
    redis_url: str
    service_secret: str
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
