# Generation and question quality

How prepza turns a job description into an interview, how questions are reused and checked, and the settings that shape it. The `generation` service runs it; the `library` service stores the results (see [Architecture](architecture.md)).

- [Generation pipeline](#generation-pipeline)
- [Reusing proven questions](#reusing-proven-questions)
- [Question quality](#question-quality)
- [Generation settings](#generation-settings)
- [Models](#models)
- [Rate limits](#rate-limits)

## Generation pipeline

```
job text -> extract requirements and level -> draft topics          (both cached per input)
         -> human review loop (checkboxes, inline edits, or free-text revision)
         -> reuse proven questions from similar templates          (pgvector)
         -> questions with their options, in parallel calls per subtopic
         -> drop duplicates by meaning                             (embeddings)
         -> top up any topic short of its size -> save to the library
```

- The pipeline is a LangGraph graph, run by the generation worker (`app/worker_main.py`) as Cloud Tasks jobs.
- The graph is checkpointed in Postgres, so a failed run can be retried from where it stopped.
- Companies hears how an interview's generation ends through events: `generation.completed` stores its questions and title, `generation.failed` (a failed run, or one the sweeper finds stuck) marks it as failed until a retry, and `generation.cancelled` removes it. Interview lists read only what these stored and never ask generation; an interview's own page asks once, in case an event hasn't come yet, and shows what companies knows when generation can't answer.
- A generation can be cancelled at any step.
- Every LLM call of the pipeline shares one rate limit across the API and all workers (`LLM_REQUESTS_PER_SECOND`).

## Reusing proven questions

The question bank is the superadmins' templates; their stages (private, retiring, revealed) are in [Templates and practice](features/templates-and-practice.md#the-question-bank).

- Reused questions fill at most half of a new interview's topic.
- Only proven private questions qualify: from templates of the same level and language, answered at least 5 times, never flagged.
- Template topics keep embeddings, so proven questions on similar topics can be found (pgvector).

## Question quality

### Before an interview is ready

Before a new interview or template is ready, the verifier checks one random answer key a topic, and fixes or replaces what's wrong (`KEY_CHECKS_PER_TOPIC`, about $0.001 a check).

A company's owners and admins can also mark a question's answer wrong in one click, which sends it to the verifier at once.

### From answers, votes and reports

Rounds publish every answer. Library keeps per-question stats (answers, correct, picks per option) next to thumbs and reports, and flags a question when they show a problem.

- An answer re-checks a question only once the question has been shown 30 times, as answer-based flags need that many.
- Votes, reports and finished topics re-check it every time.
- An answer event missing a field is logged and dropped rather than retried forever.

| Flag | When | What the verifier does |
|---|---|---|
| `wrong_key` | 2 "wrong answer" reports, or a wrong option picked more than the marked one (after 30 answers) | Checks the key through OpenAI's Batch API (half price, every 10 minutes): keeps the question, moves the key, or replaces it |
| `rewrite` | 2 "unclear" or "off topic" reports, 3+ dislikes at twice the likes, or ≤ 15% correct | Writes a new question in its place |
| `weak_options` | A wrong option almost nobody picks, or ≥ 95% correct | Writes new options for the same question |

### Fixes

- Fixes happen in place, so a topic's size never changes.
- The replaced version is archived with its stats and feedback.
- A replacement question must differ in meaning from every question already in the topic, checked by embeddings like the pipeline's duplicate step.

Superadmins see flagged and replaced questions on the admin zone's Quality tab (see [Admin zone](features/admin-zone.md#quality)).

## Generation settings

These settings in `.env` shape every generation. Terraform passes none of them to Google Cloud, so production runs on the defaults below (see [infra/README.md](../infra/README.md#notes)).

| Setting | Default | What it sets |
|---|---|---|
| `MAX_TOPICS` | 10 | Main topics an interview or template has. The review page follows it |
| `MAX_SUBTOPICS` | 10 | Subtopics per topic; every subtopic is at least one model call. The review page follows it |
| `INTERVIEW_QUESTIONS_PER_TOPIC` | 70 | Questions per topic of a company's interview, from which each candidate gets a random subset |
| `TEMPLATE_QUESTIONS_PER_TOPIC` | 90 | Questions per topic of a template; a third is revealed for free practice, the rest is copied into companies' interviews |
| `LLM_REQUESTS_PER_SECOND` | 8 | Generation's LLM requests a second, shared by the API and every worker through Redis; 0 turns it off. The help chat isn't limited by it, so it stays responsive during big generations |
| `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` | Off | Trace generation and help chat calls to LangSmith |

## Models

Each AI task has its own model and reasoning effort. The effort is `none`, `minimal`, `low`, `medium` or `high`; only reasoning models take an effort.

| Task | Model | Effort |
|---|---|---|
| Generation of an interview or template, at any level | `INTERVIEW_MODEL` (`gpt-6.1-sol`) | `INTERVIEW_REASONING_EFFORT` (`low`) |
| Verifier: answer-key checks, at once and in batches | `VERIFY_MODEL` (`gpt-6.1-sol`) | `VERIFY_REASONING_EFFORT` (`medium`) |
| FAQ help chat | `HELP_MODEL` (`gpt-6-luna`) | `HELP_REASONING_EFFORT` (`none`, which also lets it take a temperature) |

Every generation runs on `gpt-6.1-sol` at low. In testing ([evals/README.md](../evals/README.md)):

- `gpt-6-luna` at high wrote basic and medium questions as accurately, at a fraction of the price but more slowly.
- Its hard questions came out too easy.
- So generation stays on Sol, for one quality everywhere.
- The verifier did as well at low as at medium, and stays at medium.

## Rate limits

| Limit | Setting | Default |
|---|---|---|
| Generations per account in the window (0 turns it off) | `GENERATION_LIMIT` | 20 |
| The window for the per-account limits | `GENERATION_WINDOW_SECONDS` | A day |
| Re-generated questions per account in the same window (0 turns it off) | `REGENERATION_LIMIT` | 100 |
| Revisions in words per topic review; after that, topics are only chosen by checkbox | `MAX_TOPIC_REVISIONS` | 10 |
| New generations a day for everyone together, a ceiling on LLM spending (0 turns it off) | `DAILY_GENERATION_LIMIT` | 200 |
| Question reports per user a day (library) | `REPORTS_PER_DAY` | 30 |
| Thumbs (ratings) per user a day (library) | `RATINGS_PER_DAY` | 200 |
| Verifier jobs a day for everyone together; a superadmin's "Fix now" isn't counted | `DAILY_VERIFY_LIMIT` | 300 |

Email limits are in [Candidates](features/candidates.md#email-limits).
