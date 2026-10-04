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
| **Time** | Generation: seconds per 100-question topic | `generate_kits.py` | ≤ 60 s |
| | Tutor: seconds to the first word, median and slowest | `tutor_test.py` | median ≤ 2 s, slowest ≤ 5 s |
| **Price** | Generation: USD per 100-question topic | Token usage × list price | ≤ $0.25 |
| | Tutor: USD per turn | Token usage × list price | ≤ $0.004 (a paid turn sells for $0.02) |
| **Tutor quality** | Every claim and calculation in the reply is correct | Judge (`judges/tutor_review.md`) | ≥ 97% |
| | Helpful, 1–5 | Judge | ≥ 4.8 |
| **Judge reliability** | Planted wrong keys it catches (`key_traps.json`) | `review_questions.py` | 100% |
| | Agreement with the reference verdicts (`reviews.json`) | `review_questions.py --compare-reference` | ≥ 95% |

Questions also report their average length and the share that show an example (code, a query,
a formula); a programming kit should have at least a third with one.

**Judges have noise.** The same kit's scores move by up to about 0.3 between judge runs, and a
40-question sample can't separate small differences. Compare large differences, or review more.

## Baselines (2026-10-04)

**Generation**, `gpt-6.1-sol` at low reasoning, current prompts, on `questions.json` (240 questions,
8 domains), judged by `gpt-6.1-sol` at high reasoning:

| Clarity | Relevance | One answer | Key correct | Code answers | Distractors | Correct is longest | Per topic |
|---|---|---|---|---|---|---|---|
| 4.95 | 4.23 | 98% | 99% | 13 of 13 | 3.03 | 11% | $0.21–0.25, 49–61 s |

For comparison, `gpt-6-luna` at low reasoning: about $0.006 and 17 s a topic, but more
miscalculations on hard topics, questions judged too easy for the level, and the correct option
the longest 26–46% of the time.

**Tutor**, on `follow_ups.json` (45):

| Setting | Correct | Helpful | First word, median / slowest | Per turn |
|---|---|---|---|---|
| `gpt-6-luna` low | 40 of 45 | 4.82 | 1.4 s / 5.7 s | $0.00015 |
| **`gpt-6.1-sol` low** (in use) | 44 of 45 | 4.96 | 1.5 s / 4.9 s | $0.0029 |

**Judge**, `gpt-6.1-sol` at high reasoning: caught 60 of 60 planted wrong keys.

## Datasets

All in `datasets/`, frozen: rebuild one only on purpose (a new domain, a new prompt generation),
note the date, and re-run the baselines on it.

| File | What | Built by | Cost to rebuild |
|---|---|---|---|
| `inputs.json` | 8 domains (software, marketing, nursing, accounting, Spanish for travel, school chemistry, electrician apprentice, project management): a job description or goal for the full pipeline, plus fixed topics and subtopics for question-only tests | By hand | — |
| `questions.json` | 240 reference questions, 5 per subtopic, written with the generation prompt of the date inside | `build_questions.py` | about $0.50 |
| `reviews.json` | The reference judge's verdict on each of those questions | `review_questions.py --save-reference` | about $3 |
| `key_traps.json` | 60 of those questions with the key moved to a wrong option on purpose | `build_traps.py` | free |
| `follow_ups.json` | 45 hard tutor follow-ups (defending a wrong pick, a "what if", a step-by-step request) | `build_follow_ups.py` | about $0.50 |

`reviews.json` flags 4 questions as flawed (q0008, q0072, q0094, q0232). They're kept on purpose:
real generations have such slips, and a tutor or verifier test should see some.

## Running a test

The scripts run inside the local stack's service containers, which have the service code,
packages and OpenAI key. `run.sh` copies `evals/` in, runs the script, and copies results back to
`results/` (not committed).

```bash
# New kits from the full pipeline: price, time, tokens; then review and check them
evals/run.sh generation generate_kits.py python_backend senior_accountant --label new-prompt
evals/run.sh generation review_questions.py results/kit_python_backend_new-prompt.json --sample 40
evals/run.sh generation check_code.py results/kit_python_backend_new-prompt.json

# Another generation model or effort
MODEL=gpt-6-luna EFFORT=low evals/run.sh generation generate_kits.py --all --label luna-low

# Tutor settings, cheapest first, stopping at the first that gets everything right
evals/run.sh rounds tutor_test.py gpt-6-luna/low gpt-6-luna/medium gpt-6.1-sol/low --stop-when-all-correct

# A cheaper judge, tested against the reference and the traps
JUDGE_MODEL=gpt-6-luna JUDGE_EFFORT=medium evals/run.sh generation review_questions.py datasets/questions.json --compare-reference
JUDGE_MODEL=gpt-6-luna JUDGE_EFFORT=medium evals/run.sh generation review_questions.py datasets/key_traps.json
```

| Test | Cost |
|---|---|
| A full kit, `gpt-6.1-sol` | $1.60–2.30 |
| A full kit, `gpt-6-luna` | about $0.05 |
| Reviewing 40 questions (Sol judge, high) | about $0.50 |
| A tutor setting on all 45 follow-ups, with the judge | about $0.60 on Sol, $0.45 on Luna |
| Code check, measurements, traps | free |

Use `--sample` to review part of a kit, and judge first with the reference only when a cheaper
judge hasn't been shown to agree.

## Lessons so far

- **More reasoning on the same model didn't help:** `gpt-6-luna` at medium wasn't more accurate
  than at low, for questions or the tutor, only slower and dearer. A stronger model did help.
- **Put what must not be lost in its own output field:** asked to embed code in the question
  text, a low-effort model forgot it in up to 1 in 6 questions; a separate `example` field fixed it.
- **Prompts must work for any domain:** test every prompt change on several of the 8 domains, not
  only software; `test_question_prompts_ask_for_pick_one_questions_without_engineering_terms` in
  generation's tests keeps software terms out of the prompts.
