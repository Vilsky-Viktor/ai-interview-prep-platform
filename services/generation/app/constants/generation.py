from typing import Literal

from prepza_common.constants import MAX_GOAL_LENGTH  # noqa: F401 (re-exported)

MAX_CONCURRENCY = 8
RECURSION_LIMIT = 200

# A topic's or subtopic's name, drafted or edited by hand during review. How many topics and
# subtopics a test has are settings (MAX_TOPICS, MAX_SUBTOPICS).
MAX_TOPIC_NAME_LENGTH = 50
TOPIC_ATTEMPTS = 2
# Questions are written for this many times a topic's size, to replace the ones dropped as
# ambiguous or duplicate. 1.0 since testing (evals/README.md): rounding each subtopic's count up
# left enough spares, and fill_topics covers whatever is still missing.
QUESTION_OVERSAMPLE = 1.0
# Questions, each with its options, per call. A subtopic needing more is split into calls.
QUESTION_BATCH_SIZE = 20
# Each call for the same subtopic takes the next angle, so parallel calls don't write the same
# obvious questions.
QUESTION_FOCUSES = (
    "core concepts: what they mean in practice and how they differ",
    "applying it to a concrete case: working out the result or choosing the right approach",
    "situations: what happens next, what went wrong, or what to do first",
    "trade-offs, edge cases and common mistakes",
)
# Questions whose embeddings are this close (cosine distance) ask the same thing in other words.
DUPLICATE_DISTANCE = 0.08
ANSWER_ATTEMPTS = 3
QUESTION_ATTEMPTS = 3
# Output cap per call, reasoning tokens included. A model that loops fails at this many tokens
# instead of writing until its own limit, minutes later.
MAX_OUTPUT_TOKENS = 16_000
# Writing MAX_OUTPUT_TOKENS can take a few minutes; a call silent for longer has hung.
LLM_TIMEOUT_SECONDS = 300
# What OpenAI accepts for a reasoning model's effort; the settings pick one (see config).
ReasoningEffort = Literal["none", "minimal", "low", "medium", "high"]
DISTRACTORS = 3
# Upper bound for any answer option; most are much shorter. Longer options are rejected.
MAX_OPTION_CHARS = 250
REGENERATE_ATTEMPTS = 3
# Rounds of extra questions for a topic that ended short, before the generation fails.
FILL_ATTEMPTS = 3
# Extra questions a fill-up asks for beyond what's missing: it runs one round after another, so a
# spare saves a round when one comes back a duplicate.
FILL_SPARE_QUESTIONS = 2

# The changes a reviewer describes in words during topic review, and how many times one
# generation's topics may be revised that way.
MAX_INSTRUCTIONS_LENGTH = 500
MAX_TOPIC_REVISIONS = 10
TOO_MANY_REVISIONS = "These topics can't be changed in words any more. Choose the topics to keep."

# A generation stops after this long: Cloud Tasks gives one request at most 30 minutes.
JOB_TIMEOUT_SECONDS = 25 * 60
# How long Cloud Tasks waits for the worker's answer; a little over JOB_TIMEOUT_SECONDS.
TASK_DEADLINE_SECONDS = 28 * 60
CLOUD_TASKS_URL = "https://cloudtasks.googleapis.com"
# The worker's job endpoints.
RUN_GENERATION = "/internal/jobs/run-generation"
VERIFY_QUESTION = "/internal/jobs/verify-question"
# A running job updates its row as it goes; one untouched for longer than a job may run has lost
# its worker. The margin covers the last update coming a little before the timeout.
STUCK_AFTER_SECONDS = JOB_TIMEOUT_SECONDS + 10 * 60
# A queued generation may only be waiting for a free worker; one queued this long has lost its
# job (the queue failed to take it).
QUEUED_STUCK_AFTER_SECONDS = 2 * 60 * 60

GENERATION_FAILED = "Generation failed. Please try again."
GENERATION_STOPPED = "Generation stopped unexpectedly. Please try again."
# Topics left waiting for review this long are cancelled; nothing has been generated yet.
REVIEW_EXPIRY_DAYS = 14

# Extraction and drafted topics are reused for the same prompt and input for this long.
DRAFT_CACHE_SECONDS = 30 * 24 * 60 * 60

# Redis counters for the LLM requests made in each second, shared by all generation processes.
LLM_RATE_KEY = "rate:llm"
# Connections of the checkpointer's own pool, on top of the SQLAlchemy pool.
CHECKPOINTER_POOL_SIZE = 4

# The daily generation budget: its counter, kept a little over a day, and the refusal.
BUDGET_KEY = "budget:generations"
BUDGET_KEY_SECONDS = 2 * 24 * 60 * 60
GENERATIONS_PAUSED = (
    "We've reached today's limit for new generations. Please try again tomorrow; practice and "
    "interviews keep working."
)
