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
    # Each AI task has its own model and effort, so one can change without the others. Effort is
    # how hard a reasoning model thinks: "none", "minimal", "low", "medium" or "high".
    # Generation (extraction, topics, questions, answers, a re-generated question) by who it's for:
    # a company's interview, whatever its level, since candidates are judged on it;
    interview_model: str = "gpt-6.1-sol"
    interview_reasoning_effort: ReasoningEffort = "low"
    # a learner's basic or medium kit, where Luna at high reasoning was as accurate as Sol in
    # testing at about a seventh of the price, though slower (evals/README.md);
    kit_model: str = "gpt-6-luna"
    kit_reasoning_effort: ReasoningEffort = "high"
    # and a learner's hard kit, where Luna's questions came out too easy, plus reading a learner's
    # text before its level is known.
    hard_kit_model: str = "gpt-6.1-sol"
    hard_kit_reasoning_effort: ReasoningEffort = "low"
    # Checks answer keys, at once and in batches: rare, and it must be right.
    verify_model: str = "gpt-6.1-sol"
    verify_reasoning_effort: ReasoningEffort = "medium"
    # Checks that a public kit's title names no company.
    title_check_model: str = "gpt-6.1-sol"
    title_check_reasoning_effort: ReasoningEffort = "low"
    generation_limit: int = Field(default=20, ge=0)
    generation_window_seconds: int = Field(default=86_400, gt=0)
    regeneration_limit: int = Field(default=100, ge=0)
    # New generations a day, for everyone together: a ceiling on LLM spending (about $1.60
    # each). 0 turns it off.
    daily_generation_limit: int = Field(default=200, ge=0)
    # LLM requests a second across the API and every worker; 0 turns the limit off. The default
    # stays under OpenAI's 500 requests a minute on its first tier.
    llm_requests_per_second: int = Field(default=8, ge=0)

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
