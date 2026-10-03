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
    # Paddle's price id of each top-up (see constants/products.py); one without an id isn't sold.
    paddle_price_topup_10: str = ""
    paddle_price_topup_25: str = ""
    paddle_price_topup_50: str = ""
    paddle_price_topup_100: str = ""
    paddle_price_topup_250: str = ""
    paddle_price_topup_500: str = ""
    # Paddle's $1 price; a custom amount buys it in a quantity of 10 to 500.
    paddle_price_topup_custom: str = ""
    # Automatic top-up: the server-side API key that charges the saved card, and the $0
    # monthly price whose checkout saves it. Without both, it isn't offered.
    paddle_api_key: str = ""
    paddle_price_auto_top_up: str = ""

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
