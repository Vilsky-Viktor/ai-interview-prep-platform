from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    firebase_project_id: str
    firebase_auth_emulator_host: str = ""
    # The API description lists every route, internal ones too: development only.
    api_docs: bool = False
    database_url: str
    service_secret: str
    # Paddle: "sandbox" or "production", the client-side token for Paddle.js (public by design),
    # and the secret that signs its webhooks.
    paddle_environment: str = "sandbox"
    paddle_client_token: str = ""
    paddle_webhook_secret: str = ""
    # Paddle's price id of each product (see constants/products.py); unset products aren't sold.
    paddle_price_candidates_10: str = ""
    paddle_price_candidates_50: str = ""
    paddle_price_candidates_200: str = ""
    paddle_price_job_search_pass: str = ""
    paddle_price_generations_3: str = ""

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
