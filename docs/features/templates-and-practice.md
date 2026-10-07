# Templates and free practice

Templates are ready-made interviews by role, made by prepza's superadmins (see [Admin zone](admin-zone.md#templates)). They are the question bank: companies copy them into interviews, and people preparing for a role practise free on their revealed questions.

## The question bank

Each template question has a stage that only moves forward:

| Stage | Used by | Moves on |
|---|---|---|
| **private** | Company interviews only | After 100 answers across every interview using it, it becomes retiring |
| **retiring** | New interviews stop taking it | Once no interview has used a copy for 90 days, it becomes revealed |
| **revealed** | Free practice, shown with its answer | Final stage |

- A new template reveals a third of each topic at once.
- An interview's copy of a question remembers its original, so its answers count there too.
- A question revealed for practice is no longer given to candidates, even in an interview that copied it earlier.
- A daily job (`/internal/schedules/bank`) moves the stages.

Template topics keep embeddings, so proven questions on similar topics can be found and reused by new interviews (see [Generation](../generation.md#reusing-proven-questions)). Template topics without an embedding get one from:

```bash
docker compose exec generation uv run --no-sync python -m app.jobs.embed_templates
```

## Copying a template

- Copying a template into a company's interview takes only its private questions.
- A topic with fewer than 10 private questions is left out (`MIN_COPY_QUESTIONS`).
- A template with no such topic can't be copied, and companies' template list leaves it out (`GET /templates/copyable`).
- Practice and the admin zone list every template.

## Slugs

Each template has a readable slug made from its title when it's saved: `backend-developer`, then `backend-developer-2`, and so on.

- The slug never changes on rename, so its practice page's URL stays the same.
- `GET /templates/{id or slug}` finds a template by either.
- The public `GET /templates/{id or slug}/sample` gives up to 5 of its revealed questions with answers, spread across its topics. It never gives private or retiring ones.

## Free practice

Free practice (`/practice`) gives people preparing for a role timed practice interviews on the templates' revealed questions.

- 10 questions a topic.
- At the end: the grade and every right answer.
- Each template keeps the person's rounds and progress.
- At most 20 rounds an hour per person (`PRACTICE_ROUNDS_PER_HOUR`).

A practice page is in English and in its template's language only (see [Public site](site.md#skills-tests-by-role)).

### "Hiring for this role?"

A practice test's page and its result both offer the template for hiring. The button opens `/companies/templates/<template id>`, which:

- goes straight to the test in the user's only company,
- or lists their companies, or lets them create one, to choose where it's copied.

## Related pages

- [Public site](site.md#skills-tests-by-role): the skills test page each template gets.
- [Generation](../generation.md#generation-settings): `TEMPLATE_QUESTIONS_PER_TOPIC` and the other generation settings.
