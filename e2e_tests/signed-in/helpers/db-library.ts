import { withDatabase } from "./db";

/** A throwaway template with one topic of `questions` private questions, saved straight into the
 * library database (a real one needs an OpenAI generation). A company can copy it only with at
 * least 10 (MIN_COPY_QUESTIONS in services/library); practice lists it either way. German, so
 * nothing that picks English templates to make interviews from (templatesBySize, the load
 * tests) takes it. Its right answers hold `inline code`. */
export async function addTemplate(
  title: string,
  questions: number,
): Promise<string> {
  return withDatabase("library", async (client) => {
    const set = await client.query(
      `INSERT INTO sets (id, kind, owner_type, owner_id, title, source_text, level, language,
         requirements, topic_count, created_at)
       VALUES (gen_random_uuid(), 'template', 'platform', 'prepza', $1, 'E2E', 'basic', 'de',
         '[]', 1, now())
       RETURNING id`,
      [title],
    );
    const id = set.rows[0].id;
    const topic = await client.query(
      `INSERT INTO topics (id, set_id, position, title, subtopics)
       VALUES (gen_random_uuid(), $1, 0, 'E2E topic', '[]') RETURNING id`,
      [id],
    );
    const options = JSON.stringify([
      { answer: "Check `if is_member:` first", correct: true },
      { answer: "Skip the check", correct: false },
    ]);

    for (let position = 0; position < questions; position++) {
      await client.query(
        `INSERT INTO questions (id, topic_id, position, text, options, stage)
         VALUES (gen_random_uuid(), $1, $2, $3, $4, 'private')`,
        [topic.rows[0].id, position, `E2E question ${position + 1}?`, options],
      );
    }

    return id;
  });
}

/** Deletes a template addTemplate made; its topics and questions go with it, and the companies'
 * copies stay. */
export async function deleteTemplate(id: string) {
  await withDatabase("library", (client) =>
    client.query("DELETE FROM sets WHERE id = $1", [id]),
  );
}

/** Keeps `oldText` as a replaced version of the first question of a template addTemplate made,
 * as the verifier does when it replaces a question (that needs OpenAI). Deleting the template
 * deletes it too. */
export async function addReplacedVersion(templateId: string, oldText: string) {
  await withDatabase("library", (client) =>
    client.query(
      `INSERT INTO question_revisions (id, question_id, text, options, answers, correct,
         option_picks, likes, dislikes, reports, replaced_at)
       SELECT gen_random_uuid(), q.id, $2, '[{"answer": "Old right", "correct": true},
         {"answer": "Old wrong", "correct": false}]', 4, 1, '{}', 0, 3, '[]', now()
       FROM questions q JOIN topics t ON t.id = q.topic_id
       WHERE t.set_id = $1 AND q.position = 0`,
      [templateId, oldText],
    ),
  );
}

/** `count` finished practice rounds of a throwaway user on `templateId`, one a day apart
 * (the newest now), saved straight into the rounds database; deleting the account deletes
 * them. */
export async function addPracticeRounds(
  userId: string,
  templateId: string,
  count: number,
) {
  await withDatabase("rounds", async (client) => {
    for (let index = 0; index < count; index++) {
      await client.query(
        `INSERT INTO sessions (id, user_id, topic_id, interview_set_id, candidate_invite_id,
           topic_title, status, questions, final_score, started_at, finished_at, preview, practice)
         VALUES (gen_random_uuid(), $1, gen_random_uuid(), $2, gen_random_uuid(), 'E2E topic',
           'finished', '[{}, {}]', NULL, now() - make_interval(days => $3),
           now() - make_interval(days => $3), false, true)`,
        [userId, templateId, index],
      );
    }
  });
}
