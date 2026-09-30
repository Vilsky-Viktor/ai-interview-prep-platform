# Prepza improvement plan

Written 2026-09-30, based on a full read of every service, the frontend, the gateway, compose and the migrations. The findings come from that reading, not from running the app. Line links point at the code as it was on that date.

The project is not yet under git and has no CI, even though every service has tests. Set up both before starting the refactors below.

---

## 0. Top findings, by impact

1. **Interviews look stuck for everyone except their creator (bug).** The companies service fetches the generated set using the *caller's* token ([interviews.py:14](../services/companies/app/helpers/interviews.py#L14)). The generation service only returns a generation to its owner ([generations.py:18](../services/generation/app/routers/generations.py#L18)). So other admins, and candidates, see "Generating…" or "Interview is not ready yet" until the creator happens to open the interview again after it finishes.
2. **Cost is dominated by volume, not by model choice alone.** The default is 100 questions per topic with 1.2× oversampling, and every question gets an answer plus 3 wrong answer options, all on `gpt-4o`. That's up to about 1,000 fully answered questions per preparation, while a user answers maybe 10–20 per round.
3. **Feedback is thrown away.** Re-generating a question deletes its ratings and reports ([preparations.py:190-200](../services/library/app/storage/preparations.py#L190)). That is exactly the data the quality loop needs.
4. **The preparation page gets slower as a user practices.** It loads the entire preparation, including every answer, plus every finished round with its full question snapshot, once per mode, on every view ([coverage.py:11-18](../services/rounds/app/services/coverage.py#L11)).
5. **Rate-limit keys can stay forever.** `INCR` and then `EXPIRE` are two separate calls ([rate_limit.py:10-13](../services/rounds/app/helpers/rate_limit.py#L10)). If the process dies between them, the key never expires and that user is blocked permanently.
6. **"Passed" means three different things.** "Passed" topics and the "Done" badge count any finished round at 70% or more, including multiple choice ([rounds.py:122](../services/rounds/app/storage/rounds.py#L122), [rounds.ts:26](../frontend/lib/rounds.ts#L26)). The certificate requires open-answer coverage of every question. Users see contradictory signals.
7. **The library ranks by raw average rating** ([search.py:31](../services/library/app/storage/search.py#L31)). One 5★ vote beats a hundred 4.8★ votes.
8. **Back arrows sit outside the page container** ([back-link.tsx:23](../frontend/components/back-link.tsx#L23)), so they're off-screen on phones. Many layouts also use fixed widths.

---

## 1. Reliability

**Status (2026-09-30):** Done:
- R1 (interim fix: a service-authenticated internal endpoint, not events yet), R2, R3 (atomic counter; no refund for failed LLM calls yet), R8, R10, R11.
- R4 retry, from the failed screen. There is no sweeper for stuck rows yet.
- R6 (periodic reclaim, attempt limit, dead-letter stream, stream trimming).
- E1 (`question_progress` table).
- C1 (usage and cost per generation), the configurable model, and the lower default question count.
- UI items 1, 2, 4 and 5, and the Bayesian library ranking.

| # | Problem | Fix |
|---|---|---|
| R1 | Interview `set_id` is found by polling the generation service with the user's token (bug above). | The generation service publishes `generation.completed {generation_id, set_id, kind, company_id}` to the existing Redis stream. The companies service consumes it and stores `set_id` and `title`. Delete `attach_set`. Until then, call a service-authenticated internal `GET /internal/generations/{id}` instead. |
| R2 | Only the creator can review topics for a company interview. `/generate/[id]` returns 404 for other admins. | Serve the review through companies (after checking membership), or authorize company generations by `company_id`. |
| R3 | Non-atomic rate limiter (in both generation and rounds). | `SET key 0 EX window NX`, then `INCR`, in one pipeline. Only count the call once the LLM call succeeds, or refund it on failure. |
| R4 | Failed generations can't be retried. The UI only offers "Start over" ([generation-view.tsx:168](../frontend/components/generation/generation-view.tsx#L168)), which loses the pasted text. | Add `POST /generations/{id}/retry`, which re-enqueues the job; the checkpoint already supports resuming. Add a sweeper that marks rows stuck in `queued`/`running` past `JOB_TIMEOUT_SECONDS` as failed. Expire `awaiting_review` rows after N days. |
| R5 | Duplicate sets are possible. If `create_preparation` succeeds but the response is lost, a retry creates a second set ([pipeline.py:53-55](../services/generation/app/services/pipeline.py#L53)). | Add a unique `generation_id` column on `sets` and make the internal create endpoint idempotent. |
| R6 | Notifications: failed events are only reclaimed at startup ([consumer.py:60](../services/notifications/app/services/consumer.py#L60)). There's no attempt limit, and the stream is never trimmed. | Run `XAUTOCLAIM` periodically in the loop. Send an event to a dead-letter list after N attempts. `XADD ... MAXLEN ~ 10000`. |
| R7 | Gateway timeouts. nginx's default `proxy_read_timeout` is 60s. Grading (with 3 LLM retries) and re-generating through companies (the client waits 120s) can exceed it, so the user gets a 504 while the work still completes. | Raise the timeout for `/api/rounds/` and `/api/companies/`, or better, make re-generation a background job. Put explicit per-call timeouts on the LLM clients. |
| R8 | Re-inviting the same candidate email hits the unique constraint and returns a 500 ([interviews.py:134](../services/companies/app/routers/interviews.py#L134)). The UI shows "Check the email". | Upsert and resend, as preparation shares already do. |
| R9 | Deleting a company leaves orphaned sets (library), sessions (rounds) and generations. Preparations can't be deleted at all. | Publish a `company.deleted` or `set.deleted` event and have each owning service delete its own data. Add a delete-preparation endpoint and button. |
| R10 | `serverFetch` returns `null` on *any* error ([server-api.ts:13](../frontend/lib/server-api.ts#L13)), so a 500 or an expired token renders as "Not found". | Return a status: `notFound()` only on 404, throw on 5xx so `error.tsx` shows, and treat 401 as signed-out. |
| R11 | `FIREBASE_AUTH_EMULATOR_HOST` is in the shared env anchor for every service ([docker-compose.yml:3](../docker-compose.yml#L3)). If it's ever set in production, unsigned tokens are accepted. | Move it into `docker-compose.override.yml` only, and refuse to start if it's set while the project id doesn't start with `demo-`. |
| R12 | Health checks don't touch the database or Redis. Migrations run on every API container start ([Dockerfile:18](../services/generation/Dockerfile#L18)). | Add a `/ready` endpoint with `SELECT 1` and `PING`. Run migrations as a one-off compose service or job, which is also required before running more than one replica. |
| R13 | LangGraph checkpoints are never deleted. With append-style fields (`question_pool`, `answer_pool`), each checkpoint grows. | Delete the thread after `DONE`/`FAILED`, or see S1, which removes checkpoints entirely. |

## 2. Efficiency

| # | Problem | Fix |
|---|---|---|
| E1 | `answered_counts` loads the full preparation content and all finished rounds, twice ([coverage.py](../services/rounds/app/services/coverage.py)). `finish_round` and `create_round` do similar work. | Add a `question_progress(user_id, topic_id, mode, question_id, latest_score, question_version)` table, upserted on every answer. Coverage, "answered", unanswered-first ordering and certificates become single aggregate queries. The text-comparison trick in `latest_scores` goes away. |
| E2 | Listing interviews makes 2 sequential HTTP calls per interview ([interviews.py:58](../services/companies/app/routers/interviews.py#L58)). | Store `set_id` and `title` in companies (R1). If a call is still needed, batch it (`POST /internal/sets:batch`) and use `asyncio.gather`. |
| E3 | Every integration call creates a new `httpx.AsyncClient` (18 places). | Create one client per service in the lifespan, reuse it, and set retries and timeouts once. |
| E4 | Library summaries use 4 correlated subqueries per row. Search uses `ILIKE '%q%'` with no index ([search.py:16](../services/library/app/storage/search.py#L16)). There's no pagination. | Denormalize `rating_sum`, `rating_count` and `join_count` onto `sets` and update them in the same transaction. Add a `pg_trgm` index on the title, or put the title into the existing tsvector. Add cursor pagination. |
| E5 | The topic-questions endpoints load full `Question` rows, with answers and options, just to return the text. | Select only `id, text`. |
| E6 | The chat sends its full history every time. | Cap it to the last N messages, and the system prompt already holds the context. |

## 3. Scalability

- **LLM throughput is the real limit.** 4 jobs × 8 concurrent calls per worker, with no limit shared across workers. Add a Redis token-bucket semaphore around the LLM client, shared by the generation worker and rounds, sized to your OpenAI rate limits. Also give interactive work (grading, chat) priority over bulk generation.
- **Generation job size.** One job can hold about 1,000 LLM calls under a 1-hour timeout. Split the work into one arq job per topic after approval, so it parallelizes across workers and a failure retries only that topic.
- **Precomputed counters** (E1, E4) keep request cost flat as users and rounds grow.
- **Stateless APIs are fine to replicate** once migrations move out of startup (R12). Set the SQLAlchemy pool size explicitly per process, and keep the total below Postgres `max_connections`. Consider PgBouncer when replicas are added.
- **Trim the event stream** (R6) and delete checkpoints (R13) so Redis and Postgres storage stay bounded.

## 4. Separation of concerns and services

**Recommendation: don't add new HTTP services yet.** The service boundaries (library, generation, rounds, companies, notifications) are sensible. The problems are in how the services talk to each other and in duplicated code:

1. **Use events instead of polling and synchronous chains.** Extend the existing Redis stream with `generation.completed`, `answer.graded`, `question.rated`, `question.reported` and `set.deleted`. Each consumer gets its own consumer group.
2. **Add a library worker, not a new service.** Question stats, quality scores, embeddings and bank search (sections 7–8) need library's database. Run them as an arq worker process inside the library service. Split it into a separate "quality" service only if it grows large.
3. **Put "can this user edit this set" in library only.** Today generation decides preparation ownership itself ([questions.py](../services/generation/app/routers/questions.py)). Instead, the frontend calls library, library authorizes and then calls generation's internal endpoint. Companies does the same for interviews.
4. **Keep business rules on the backend.** The pass threshold, max answer length and report-comment length are duplicated in [constants/rounds.ts](../frontend/constants/rounds.ts) and [constants/feedback.ts](../frontend/constants/feedback.ts). The frontend also works out "done"/"passed" itself. Return these flags from the API.
5. **Shared code.** `auth.py`, `service_auth.py`, `helpers/logging.py`, `rate_limit.py`, `storage/db.py` and `schemas/user.py` are copied into 5 services. Auth and service-auth are security-critical, so put them in a small path-installed `packages/common` (the Docker build context then becomes the repo root). Leave the rest duplicated if you prefer independence.
6. **Types.** Generate frontend types from each service's OpenAPI with `openapi-typescript`, instead of the hand-copied [types/](../frontend/types/) files. The same applies to `PreparationIn`, which is copied into both generation and library.
7. **Frontend logic.** [round-view.tsx](../frontend/components/rounds/round-view.tsx) (292 lines) and [session-view.tsx](../frontend/components/company/session-view.tsx) (283 lines) are close to the 300-line limit. They mix fetching, cursor restore and rendering. Extract `useRoundPlayer` and `useSessionPlayer` hooks into `hooks/`.

## 5. Simplification

- **S1: Replace LangGraph with two plain arq jobs.** Stage 1 runs extraction, the optional company search and topic generation, then saves topics to the `generations` row (it already has a `topics` column) and sets `awaiting_review`. Review either revises the topics (one LLM call) or approves them, which queues stage 2: per topic, questions then answers, using `asyncio.gather` with a semaphore. This removes `graph.py`, `state.py`, the `Send` fan-outs, the reducers, the checkpointer, `track_progress`'s chunk parsing and `RECURSION_LIMIT`. For crash safety, store per-topic results in the row as each topic completes. It's less code than today and fixes R13.
- **S2: One session per interview for candidates, not one per topic.** The per-topic sessions force the recursive auto-chaining in `session-view.tsx` (`openSection` calls itself, "finish" finishes all sections). A single session with topic sections would simplify rounds, companies and the frontend.
- **S3:** Replace the two mode validators with `Literal["open", "choice"]` in [companies schemas](../services/companies/app/schemas/interviews.py). Merge the two near-identical `review_session` branches in [sessions.py](../services/rounds/app/routers/sessions.py). Share one answer-submission core between `answers.py` and `session_answers.py`; they're about 80% identical.
- **S4:** Drop the round-cursor `sessionStorage` restore logic once the API returns "last answered question and its result" directly in `GET /rounds/{id}`.

## 6. UI

1. **Navigation.** Preparations, Library and Companies are only reachable from the avatar menu. Signed-out users can't find the Library at all. Add a visible top nav.
2. **Mobile.** Fix the absolutely positioned `BackLink`, the fixed `w-24`/`w-32` candidate columns, `grid-cols-2` on the compare page, and the 3-column topic row grid. Stack them below the `sm` breakpoint.
3. **The topic row is overloaded.** Today it shows Start, an editable "N of M, per round" field, per-mode score chips with "answered/total", Certificate, History and a Done check. Replace this with:
   - One progress bar: coverage plus average, using the certificate definition.
   - One primary **Practice** button, with the mode picker inside it.
   - An overflow menu with History, Certificate and Questions.
   - Owner-only settings (limit, re-generate, reports) in a "Manage questions" dialog.
4. **One definition of "mastered".** Use the certificate criteria everywhere: the Done badge, passed topics and the list page.
5. **Consistent send keys.** The goal form and open answers use Shift+Enter to send, while chat uses Enter. Use ⌘/Ctrl+Enter for all multi-line inputs.
6. **Feedback timing.** Thumbs and report are shown *before* answering and lock after one click. Show them after the answer is revealed, allow changing a vote, and label them clearly ("Good question?"). The same applies to the star rating: allow editing, and show the average and count.
7. **Topic review.** Allow inline edits (rename, remove a subtopic, add a topic) without an LLM round-trip; use the LLM only for free-text instructions. Also fix `key={topic.main_topic}`, which breaks when two topics share a name.
8. **Generation progress and failure.** Show per-topic progress ("Topic 3 of 7") instead of "steps", add a Retry button (R4), and keep the pasted text on failure.
9. **Candidate interview.** Show a section overview with per-section progress. Make "Finish interview" explicit about finishing *all* sections. Don't show mid-interview rating controls, or show them after each answer.
10. **Company pages.** Replace the "Show results/Hide results" badge with "Candidates see scores". Add invite resend and revoke, and deleting preparations and interviews.
11. **Round summary.** Show the change against the previous round and the effect on coverage, instead of a bare "Failed".

---

## 7. Reusing generated questions

**Goal:** fill part of each new preparation or interview with proven high-quality questions, and always generate fresh ones too.

### Data model (library)

- On `questions`, add:
  - `origin_id` (the canonical question this one was copied from; null means original)
  - `level`, `subtopic`
  - `embedding vector(1536)` (pgvector; switch the image to `pgvector/pgvector:pg18`)
  - `shareable bool`
  - `model` and `prompt_version`
- Add a `question_stats(root_id, …)` table, keyed by the origin root so that all copies of a question share one quality record. It holds: likes, dislikes, reports by reason, `answers`, `avg_score`, `correct_rate`, `option_picks[4]`, `quality`, `status`. Status is `active | probation | flagged | retired`.
- **Reuse copies rows** and sets `origin_id`. Sets stay independent (limits, re-generation), and feedback aggregates across copies. This is simpler than a shared many-to-many bank.

### Privacy boundary (decide before building)

Only reuse questions that are:
- `shareable = true`, meaning generated without company context or checked not to mention the company, **and**
- from public preparations, **or** from the requester's own sets, **or**, for interviews, from the same company.

Never reuse one company's private interview questions for another company.

### Selection at generation time (after topics are approved)

For each subtopic:
1. Embed `"{topic} / {subtopic} / {level}"` and query candidates with cosine similarity ≥ 0.80, the same level (or adjacent, marked), and `status = active`.
2. Rank candidates by the quality lower bound (section 8). Require at least 3 ratings or 5 answers, so reuse is based on evidence rather than luck.
3. **Mix quota:** reuse at most `REUSE_MAX_SHARE` (start at 50%) of the subtopic's target, and always generate at least `FRESH_MIN_SHARE` (start at 40%) new questions, even if the bank could fill everything. That gives exploration and novelty.
4. Pass the reused texts into the question prompt as "existing questions, cover different angles", so fresh questions complement them.
5. **Deduplicate semantically.** Replace `normalize()` exact matching with an embedding check (cosine ≥ 0.92 counts as a duplicate), across both reused and fresh questions.
6. Never reuse a question the same user has already answered in another preparation. Use `question_progress` (E1) plus `origin_id` for this.

### Exploration

New questions start in `probation` and are served normally so they collect signal. Weighted round selection (8.3) gives them fair exposure. Questions that do well become reusable; bad ones are flagged.

## 8. Using ratings, likes, dislikes and reports to improve quality automatically

### 8.1 Collect more, and better, signal

- **Stop deleting feedback on re-generation.** Move the old content and its stats into `question_revisions`.
- Rounds emits `answer.graded {question_id, mode, score, correct, option_index}`. This gives per-question difficulty and wrong-option statistics without any extra user effort.
- Add a **"Disagree with grade"** action. It's the only way to measure grader quality, and nothing collects that today.
- Let users change a thumbs vote, and collect it after the answer is revealed (UI item 6).
- Candidates' interview answers and reports feed the same stats.

### 8.2 Quality score per question root

- `like_lb` = Wilson lower bound of likes / (likes + dislikes).
- Penalties: `wrong_answer` reports count most, then `unclear`, then `off_topic`, each normalized by exposure.
- Psychometric flags:
  - `correct_rate ≥ 0.95` means too easy for its level.
  - `≤ 0.10` means too hard or broken.
  - A wrong option picked more often than the correct one suggests the answer key is wrong.
  - Open answers with a very high variance in scores suggest the question is ambiguous.
- Store the result as `quality` in [0, 1] plus a `status`.

### 8.3 Actions, run automatically by the library worker

| Trigger | Action |
|---|---|
| Reports ≥ 2 **or** a suspected wrong key | A stronger verifier LLM checks the question and reference answer. If confirmed wrong, it re-generates the **answer and options only**, bumps the version and notifies the owner. If not confirmed, the question returns to `active`. |
| `unclear` reports, or high score variance | Rewrite the question for clarity (same intent) and put it on probation. |
| `off_topic` reports, or `quality` below the retire threshold | Retire it; for sets below their limit, queue a replacement using the existing re-generate path. |
| Too easy or too hard for the level | Relabel the level so reuse matches correctly, instead of deleting it. |

- **Round and interview selection:** [round_questions](../services/rounds/app/helpers/rounds.py#L9) and [pick_questions](../services/companies/app/helpers/interviews.py#L57) skip `flagged` and `retired` questions. They weight by `quality` (probation questions get an exploration bonus) instead of pure random or shuffle.
- **Better prompts over time:** tag every question with `model` and `prompt_version`. A weekly job compares average quality by version, so prompt and model changes are judged on data, not by feel. Add the top-rated questions for similar subtopics as few-shot examples. Summarize the common reasons for dislikes and reports into an "avoid" list in the prompt.
- **Preparation stars** (1–5): use a Bayesian average for library ranking (fixes finding 7). Low-rated preparations whose topics get many `off_topic` reports feed back into the topic-generation prompt examples.

## 9. Reducing the cost of each preparation or interview

Rough numbers for today's defaults: up to 10 topics × 100 questions, about 1,000 answered questions. That's roughly 80k input and 220k output tokens, about **$2–2.50 per full preparation** at gpt-4o list prices at the time of writing (check current pricing). Most of the cost is the answer and options stage.

| # | Lever | Expected effect |
|---|---|---|
| C1 | **Measure first.** Record token usage per LLM call (`usage_metadata`) as `cost` on the `generations` row, and per answer and chat in rounds. | You can't tune what you can't see. |
| C2 | **Generate a smaller pool and top it up on demand.** Start at about 25–30 per topic. When a user's unanswered pool for a topic falls below about 30%, a background job tops it up (reuse first, then generate). | About 3–4× less at creation, and spending follows actual use. |
| C3 | **Reuse from the bank** (section 7). | Up to 50% fewer generated questions once the bank is warm. |
| C4 | **Use smaller models for bulk steps.** Try a mini-class model for questions, answers and options and for grading, and keep `gpt-4o` for the verifier (8.3) and for extraction and topics (few calls). Validate on an offline evaluation set built from high- and low-rated questions. | About 10× cheaper per token on the bulk. |
| C5 | Generate question, answer and options **in one call** per subtopic batch, instead of separate question and answer stages. Lower the oversample from 1.2 once semantic dedup is in place. | No second call re-sending the question text, and one fewer stage of latency. |
| C6 | **Cache** Tavily company summaries per normalized company name, and extraction and topics per hash of the source text (companies often paste the same job description). | Repeated interviews for the same company become almost free before the review step. |
| C7 | **Inline topic edits** (UI item 7) instead of an LLM revision for simple renames and removals. | Fewer revision calls. |
| C8 | **Grading:** give empty or trivial answers 0 without calling the LLM, cache grades by `(question_id, normalized answer hash)`, and cap chat history. | Smaller savings, but these run on every answer. |
| C9 | Use the **OpenAI Batch API** (about 50% off) for work nobody is waiting on: top-ups, verification, re-embedding and quality re-checks. | Half price on background work. |
| C10 | If prompts grow past about 1,024 tokens (for example with few-shot examples), put the static instructions first so automatic prompt caching applies. | Cheaper repeated input tokens. |

---

## 10. Suggested order

1. **Fix bugs and cheap wins (days):** git and CI, R1–R3, R8, R10, R11, C1, and the Bayesian library ranking.
2. **Reduce cost (1–2 weeks):** C2, C4 (with an evaluation set), C5, C6, then S1 (the LangGraph removal), which is easiest to do together with C5.
3. **Data foundations:** the `question_progress` table (E1), event emission, keeping feedback on re-generation, `question_stats`, and pgvector with embeddings.
4. **Quality loop:** scoring, the verifier actions and weighted selection (section 8).
5. **Reuse:** bank retrieval with the privacy rules and mix quotas (section 7), then C3 and the C9 background jobs.
6. **UI pass,** in parallel from step 1: navigation, mobile, the topic row, a single "mastered" definition, feedback timing and the candidate flow.
7. **Scale when needed:** the shared LLM limiter, per-topic jobs, the migrations job and denormalized counters.

## Open decisions

These need an answer before steps 3–5:

- **Privacy:** can questions from private preparations ever be reused for other users?
- **Probation length:** how much exposure a new question gets before it can be reused.
- **Approach:** whether to accept S1 (dropping LangGraph) and S2 (one session per interview).
