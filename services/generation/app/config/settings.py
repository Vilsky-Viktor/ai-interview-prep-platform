from prepza_common.settings import ServiceSettings
from pydantic import Field

from app.constants.generation import ReasoningEffort


class Settings(ServiceSettings):
    # The API description (/docs, /openapi.json) lists every route, internal ones too, so it's
    # served only in development, where the frontend's types are generated from it.
    api_docs: bool = False
    database_url: str
    redis_url: str
    library_url: str
    billing_url: str
    # Where Cloud Tasks (or, locally, the API itself) sends jobs.
    worker_url: str = "http://generation-worker:8000"
    # Google Cloud only: the queue ("projects/<p>/locations/<l>/queues/<q>") and the service
    # account whose signed token Cloud Tasks attaches.
    tasks_queue: str = ""
    invoker_service_account: str = ""
    service_secret: str
    questions_per_topic: int = Field(default=100, gt=0)
    llm_model: str = "gpt-6-luna"
    # How hard the model thinks: for generation (topics, questions, a re-generated question, the
    # public-title check), and for the verifier's key check, which is rare and must be right.
    # Only reasoning models take an effort.
    llm_reasoning_effort: ReasoningEffort = "low"
    verify_reasoning_effort: ReasoningEffort = "medium"
    generation_limit: int = Field(default=20, ge=0)
    generation_window_seconds: int = Field(default=86_400, gt=0)
    regeneration_limit: int = Field(default=100, ge=0)
    # New generations a day, for everyone together: a ceiling on LLM spending (about $0.03
    # each). 0 turns it off.
    daily_generation_limit: int = Field(default=0, ge=0)
    # LLM requests a second across the API and every worker; 0 turns the limit off. The default
    # stays under OpenAI's 500 requests a minute on its first tier.
    llm_requests_per_second: int = Field(default=8, ge=0)

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
