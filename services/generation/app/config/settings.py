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
    # Where Cloud Tasks (or, locally, the API itself) sends jobs.
    worker_url: str = "http://generation-worker:8000"
    # Google Cloud only: the queue ("projects/<p>/locations/<l>/queues/<q>") and the service
    # account whose signed token Cloud Tasks attaches.
    tasks_queue: str = ""
    invoker_service_account: str = ""
    service_secret: str
    interview_questions_per_topic: int = Field(default=70, gt=0)
    # Templates get more: a third is revealed for free practice at once, and the rest is copied
    # into many companies' tests.
    template_questions_per_topic: int = Field(default=90, gt=0)
    # Main topics a test has, and subtopics each topic has. Every subtopic is at
    # least one model call, so fewer of them cost less.
    max_topics: int = Field(default=10, gt=0)
    max_subtopics: int = Field(default=10, gt=0)
    # Each AI task has its own model and effort, so one can change without the others. Effort is
    # how hard a reasoning model thinks: "none", "minimal", "low", "medium" or "high".
    # Generation: extraction, topics, questions, answers and a re-generated question; also
    # translates news posts.
    interview_model: str = "gpt-6.1-sol"
    interview_reasoning_effort: ReasoningEffort = "low"
    # Checks answer keys, at once and in batches: rare, and it must be right.
    verify_model: str = "gpt-6.1-sol"
    verify_reasoning_effort: ReasoningEffort = "medium"
    generation_limit: int = Field(default=20, ge=0)
    generation_window_seconds: int = Field(default=86_400, gt=0)
    regeneration_limit: int = Field(default=100, ge=0)
    # New generations a day, for everyone together: a ceiling on LLM spending (about $1.00 a
    # test, so roughly $200 a day). 0 turns it off.
    daily_generation_limit: int = Field(default=200, ge=0)
    # LLM requests a second across the API and every worker; 0 turns the limit off. The default
    # stays under OpenAI's 500 requests a minute on its first tier.
    llm_requests_per_second: int = Field(default=8, ge=0)

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
