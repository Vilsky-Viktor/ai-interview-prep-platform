# Offline evaluation

Prepared datasets, judge prompts and scripts for testing models and prompts without rebuilding
test data each time. A test that once cost $5–10 and an hour of setup now costs only the model
calls under test.

## Metrics and targets

Every test reports these, measured the same way, so results are comparable over time. Targets
are what the current setup (October 2026) reaches; a change that misses one needs a reason.

| What | Metric | How it's measured | Target |
|---|---|---|---|
| **Question quality** | Clarity, 1–5 | Judge (`judges/question_review.md`) | ≥ 4.7 |
| | Relevance for the level, 1–5 (too easy or too hard scores lower) | Judge | ≥ 4.0 |
| | Exactly one defensible answer | Judge, share of questions | ≥ 97% |
| **Right answer quality** | The marked answer is correct | Judge, share of questions | ≥ 98% |
| | Code answers match the real output | `check_code.py` runs the example | 100% |
| **Distractor quality** | How tempting the wrong options are, 1–5 | Judge | ≥ 3.0 (the weakest metric; raise it) |
| | The correct option is the longest of the four | Counted, share of questions; about 25% when length gives nothing away | 15–35% |
| **Time** | Generation: seconds per 100-question topic | `generate_tests.py` | ≤ 60 s |
| **Price** | Generation: USD per 100-question topic | Token usage × list price | ≤ $0.25 |
| **Judge reliability** | Planted wrong keys it catches (`key_traps.json`) | `review_questions.py` | 100% |
| | Agreement with the reference verdicts (`reviews.json`) | `review_questions.py --compare-reference` | ≥ 95% |

Questions also report their average length and the share that show an example (code, a query,
a formula); a programming test should have at least a third with one.

**Judges have noise.** The same test's scores move by up to about 0.3 between judge runs, and a
40-question sample can't separate small differences. Compare large differences, or review more.

## Baselines (2026-10-04)

**Generation**, `gpt-6.1-sol` at low reasoning, current prompts, on `questions.json` (240 questions,
8 domains), judged by `gpt-6.1-sol` at high reasoning; price and time per topic measured at 100
questions a topic, before tests went to 70:

| Clarity | Relevance | One answer | Key correct | Code answers | Distractors | Correct is longest | Per topic |
|---|---|---|---|---|---|---|---|
| 4.95 | 4.23 | 98% | 99% | 13 of 13 | 3.03 | 11% | $0.21–0.25, 49–61 s |

At 70 questions a topic and oversample 1.0 that comes to about $0.13–0.16 a topic, and about $1.00
for a 7-topic test (estimated from these runs, not measured).

For comparison, `gpt-6-luna` at low reasoning: about $0.006 and 17 s a topic, but more
miscalculations on hard topics, questions judged too easy for the level, and the correct option
the longest 26–46% of the time.

`gpt-6-luna` at **high** reasoning (2026-10-04, 236 questions on the same subtopics, same judge;
price and time from full Python backend and senior accountant tests):

| Clarity | Relevance | One answer | Key correct | Code answers | Distractors | Correct is longest | Per topic |
|---|---|---|---|---|---|---|---|
| 4.91 | 3.97 (hard level 2.40, Sol 3.10) | 97% | 99% | 8 of 8 | 2.87 | 25% | $0.030–0.035, 87–92 s |

As accurate as Sol and 7–8 times cheaper, but about 1.6 times slower, and its hard-level
questions are too easy: relevance on hard topics is the gap, and it misses the relevance,
distractor and time targets, so every test is generated on Sol at low. At 70 questions a topic
(the oversampling runs below, Python backend and Spanish for travel): $0.015–0.024 and 51–66 s a
topic; a 7-topic test $0.16 in under 8 minutes.

**Verifier** (`verify_test.py`, the service's key-check prompt on the 60 traps and the same 60
questions with their real key): `gpt-6.1-sol` at low and at medium both fixed 60 of 60 traps and
kept 60 of 60 real keys, at $0.0009 a check and 1.8 s; medium is in use.

**Judge**, `gpt-6.1-sol` at high reasoning: caught 60 of 60 planted wrong keys.

**Hard-level prompt** (2026-10-04: "a scenario alone doesn't make a question hard: two or more
steps, or factors that pull in different directions"), 60 hard reference subtopics' questions, Sol
judge: `gpt-6.1-sol` low relevance 3.10 → 3.67, distractors 3.15 → 3.53, key correct 100%, but
questions about 75% longer, so a hard Sol test costs roughly 50–70% more; `gpt-6-luna` high 2.40 →
2.68, still too easy for hard tests. Basic and medium on Luna unchanged within judge noise
(medium relevance 4.29 → 4.17, basic distractors 2.80 → 2.60).

**Oversampling** (`generate_tests.py` with `OVERSAMPLE`, Luna high, 70 questions a topic, Python
backend and Spanish for travel): no topic came up short at 1.1 (13 topics) or at 1.0 (12), so no
fill-up call was made; 1.0 saves about 9% of question generation and is in use.

## Datasets

All in `datasets/`, frozen: rebuild one only on purpose (a new domain, a new prompt generation),
note the date, and re-run the baselines on it.

| File | What | Built by | Cost to rebuild |
|---|---|---|---|
| `inputs.json` | 8 domains (software, marketing, nursing, accounting, Spanish for travel, school chemistry, electrician apprentice, project management): a job description or role for the full pipeline, plus fixed topics and subtopics for question-only tests | By hand | — |
| `questions.json` | 240 reference questions, 5 per subtopic, written by `gpt-6.1-sol` at low with the generation prompt of the date inside (a rebuild uses the service's model, `INTERVIEW_MODEL`) | `build_questions.py` | about $0.50 |
| `reviews.json` | The reference judge's verdict on each of those questions | `review_questions.py --save-reference` | about $3 |
| `key_traps.json` | 60 of those questions with the key moved to a wrong option on purpose | `build_traps.py` | free |

`reviews.json` flags 4 questions as flawed (q0008, q0072, q0094, q0232). They're kept on purpose:
real generations have such slips, and a verifier test should see some.

## Running a test

The scripts run inside the local stack's service containers, which have the service code,
packages and OpenAI key. `run.sh` copies `evals/` in, runs the script, and copies results back to
`results/` (not committed). Use `generation-worker` in place of `generation` to run a second
generation test at the same time. LangSmith tracing is off for test runs. `MODEL`, `EFFORT`,
`JUDGE_MODEL`, `JUDGE_EFFORT` and `OVERSAMPLE` are passed into the container when set; without
`MODEL` and `EFFORT`, generation tests use the service's own model.

```bash
# New tests from the full pipeline: price, time, tokens; then review and check them
evals/run.sh generation generate_tests.py python_backend senior_accountant --label new-prompt
evals/run.sh generation review_questions.py results/test_python_backend_new-prompt.json --sample 40
evals/run.sh generation check_code.py results/test_python_backend_new-prompt.json

# Another model or effort on the reference subtopics, then the same review as the baseline
MODEL=gpt-6-luna EFFORT=high evals/run.sh generation build_questions.py --label luna-high
evals/run.sh generation review_questions.py results/questions_luna-high.json

# Another generation model or effort, on full tests
MODEL=gpt-6-luna EFFORT=low evals/run.sh generation generate_tests.py --all --label luna-low

# Another oversample, on full tests; each result counts the fill-up calls it needed
OVERSAMPLE=1.1 evals/run.sh generation-worker generate_tests.py python_backend --label os-1.1

# Verifier settings, on the traps and the same questions with their real key
evals/run.sh generation verify_test.py gpt-6.1-sol/low gpt-6.1-sol/medium

# A cheaper judge, tested against the reference and the traps
JUDGE_MODEL=gpt-6-luna JUDGE_EFFORT=medium evals/run.sh generation review_questions.py datasets/questions.json --compare-reference
JUDGE_MODEL=gpt-6-luna JUDGE_EFFORT=medium evals/run.sh generation review_questions.py datasets/key_traps.json
```

| Test | Cost |
|---|---|
| A full test, `gpt-6.1-sol` low | $1.60–2.30 at 100 questions a topic (7–10 topics); about $1.00 for 7 topics at 70 (estimated) |
| A full test, `gpt-6-luna` high, 70 questions a topic | $0.07–0.20 (4–9 topics) |
| A full test, `gpt-6-luna` low | about $0.05 at 100 questions a topic |
| A verifier setting on 120 checks (`verify_test.py`) | about $0.11 on Sol |
| Reviewing 40 questions (Sol judge, high) | about $0.50 |
| Code check, measurements, traps | free |

Use `--sample` to review part of a test, and judge first with the reference only when a cheaper
judge hasn't been shown to agree.

## Lessons so far

- **Check which efforts a model takes before testing one:** `gpt-6.1-sol` accepts only `low`,
  `medium`, `high` and `xhigh` (it refuses `none` and `minimal`), so `low` is its cheapest setting.
- **More reasoning on the same model didn't help:** `gpt-6-luna` at medium wasn't more accurate
  than at low, only slower and dearer. A stronger model did help.
- **Put what must not be lost in its own output field:** asked to embed code in the question
  text, a low-effort model forgot it in up to 1 in 6 questions; a separate `example` field fixed it.
- **Prompts must work for any domain:** test every prompt change on several of the 8 domains, not
  only software; `test_question_prompts_ask_for_pick_one_questions_without_engineering_terms` in
  generation's tests keeps software terms out of the prompts.
