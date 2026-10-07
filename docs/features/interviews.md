# Interviews

An interview is a timed multiple-choice test for one role. A company makes it from a job description or a ready-made template, then invites candidates to it (see [Candidates](candidates.md)).

## Making an interview

There are two ways to start:

- **From a template:** pick a ready-made interview, searchable by role, level and language. It is copied at once, for free. The list shows only templates that can still be copied (see [Templates and practice](templates-and-practice.md#copying-a-template)).
- **From a job description:** paste it or describe the role. The AI extracts the requirements and proposes topics.

For each topic, set how many questions it asks each candidate: 10 by default, drawn from the topic's 70.

Generating an interview is free. A company can have at most 3 interviews waiting without a candidate before it generates another, and generates at most 10 a day (see [Credits and payments](billing.md)).

### Reviewing the topics

Before anything expensive runs, the company reviews the proposed topics, for free:

- uncheck the topics it doesn't need,
- rename a topic or edit its subtopics in place,
- or describe bigger changes in plain text.

A review takes at most 10 revisions in words; after that, topics are only chosen by checkbox (see [Generation](../generation.md#rate-limits)).

### Questions

- Every topic gets a bank of multiple-choice questions.
- Each question has one correct option and three plausible wrong ones.
- Owners and admins can re-generate individual questions.
- An interview's questions page always shows each question with its answer options.
- Questions improve on their own: candidates' answers, votes and reports flag weak ones, and a background verifier fixes or replaces them (see [Question quality](../generation.md#question-quality)).

How generation works step by step is in [Generation](../generation.md).

## The interview page

An interview's page has three tabs:

| Tab | Who sees it | What it holds |
|---|---|---|
| **topics** | Every member | The interview's topics and questions |
| **candidates** | Every member | The candidate list (see [Candidates](candidates.md#the-candidate-list)) |
| **settings** | Owners and admins | Time per question, pass mark and "Mark as hired", each saved as it changes |

### Settings

- **Time per question:** 60 seconds by default, adjustable per interview (see [Timing](candidates.md#timing)).
- **Pass mark:** 70% by default, from 1 to 100. Grades show green or red against it.
- **Mark as hired:** marks the interview as hired and stops its shareable link at once.

### Status

Each interview shows its status:

| Status | Meaning |
|---|---|
| new | No candidates yet |
| in process | Candidates invited |
| hired | "Mark as hired" was set on its settings tab |

## Preview

Any company member can preview an interview as a candidate, with the play button on the interview list or page.

- It shows the same timed questions.
- It is free.
- It is kept out of the candidate list.
- Its answers are kept out of the questions' statistics.

## Lists and text fields

- Every list loads more as you scroll and renders only what's on screen, however long it gets.
- Every text field stops at the length its service accepts, so nothing is refused on sending. The limits live in the services; `frontend/constants/limits.ts` mirrors them.

| Field | Limit (characters) |
|---|---|
| Title | 70 |
| Company name | 45 |
| Topic name | 50 |
| Job description | 10,000 |
| Email | 254 |
| A pasted or uploaded list of emails | 50,000 |
