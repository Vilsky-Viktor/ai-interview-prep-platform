from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    firebase_project_id: str
    firebase_auth_emulator_host: str = ""
    database_url: str
    redis_url: str
    library_url: str
    service_secret: str
    questions_per_topic: int = Field(default=100, gt=0)
    llm_model: str = "gpt-6-luna"
    generation_limit: int = Field(default=20, ge=0)
    generation_window_seconds: int = Field(default=86_400, gt=0)
    regeneration_limit: int = Field(default=100, ge=0)
    # LLM requests a second across the API and every worker; 0 turns the limit off. The default
    # stays under OpenAI's 500 requests a minute on its first tier.
    llm_requests_per_second: int = Field(default=8, ge=0)

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
