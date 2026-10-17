from prepza_common.settings import ServiceSettings

from app.constants.generation import ReasoningEffort


class Settings(ServiceSettings):
    # The API description (/docs, /openapi.json) lists every route, internal ones too, so it's
    # served only in development, where the frontend's types are generated from it.
    api_docs: bool = False
    database_url: str
    redis_url: str
    library_url: str
    # Notifications keeps the campaigns this service translates.
    notifications_url: str = "http://notifications:8000"
    # Where Cloud Tasks (or, locally, the API itself) sends jobs.
    worker_url: str = "http://generation-worker:8000"
    # Google Cloud only: the queue ("projects/<p>/locations/<l>/queues/<q>") and the service
    # account whose signed token Cloud Tasks attaches.
    tasks_queue: str = ""
    invoker_service_account: str = ""
    service_secret: str
    # Each AI task has its own model and effort, so one can change without the others. Effort is
    # how hard a reasoning model thinks: "none", "minimal", "low", "medium" or "high".
    # Generation: extraction, topics, questions, answers and a re-generated question; also
    # translates news posts and campaigns.
    interview_model: str = "gpt-6.1-sol"
    interview_reasoning_effort: ReasoningEffort = "low"
    # Checks answer keys, at once and in batches: rare, and it must be right.
    verify_model: str = "gpt-6.1-sol"
    verify_reasoning_effort: ReasoningEffort = "medium"


settings = Settings()
