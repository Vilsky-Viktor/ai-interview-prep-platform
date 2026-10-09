import { randomUUID } from "node:crypto";

import pg from "pg";

import { env } from "./env";

// The stack's Postgres on its network (pages.sh runs the tests there).
const POSTGRES_HOST = "postgres";

export type Template = { id: string; slug: string; title: string; language: string };

/** Runs `work` on a fresh connection to the library database. */
async function withLibrary<T>(work: (client: pg.Client) => Promise<T>) {
  const client = new pg.Client({
    host: POSTGRES_HOST,
    user: "prepza",
    password: env("POSTGRES_PASSWORD"),
    database: "library",
  });
  await client.connect();

  try {
    return await work(client);
  } finally {
    await client.end();
  }
}

/** A throwaway template with its own readable address, saved straight into the library database
 * (a real one needs an OpenAI generation). Each topic has a subtopic, two private questions and
 * one revealed. Its title is unique, so with at least 3 topics (MIN_INDEXABLE_TOPICS in
 * services/library) it's indexable, and with fewer it isn't. */
export async function addTemplate(language: string, topics: number): Promise<Template> {
  const key = randomUUID().slice(0, 8);
  const title = `E2E role ${key}`;
  const slug = `e2e-${key}`;

  return withLibrary(async (client) => {
    const set = await client.query(
      `INSERT INTO sets (id, kind, owner_type, owner_id, title, slug, source_text, level,
         language, requirements, topic_count, created_at)
       VALUES (gen_random_uuid(), 'template', 'platform', 'prepza', $1, $2, 'E2E', 'basic', $3,
         '[]', $4, now())
       RETURNING id`,
      [title, slug, language, topics],
    );
    const id = set.rows[0].id;
    const options = JSON.stringify([
      { answer: "Right", correct: true },
      { answer: "Wrong", correct: false },
    ]);

    for (let position = 0; position < topics; position++) {
      const topic = await client.query(
        `INSERT INTO topics (id, set_id, position, title, subtopics)
         VALUES (gen_random_uuid(), $1, $2, $3, '["E2E subtopic"]') RETURNING id`,
        [id, position, `E2E topic ${position + 1}`],
      );

      for (const [index, stage] of ["private", "private", "revealed"].entries()) {
        await client.query(
          `INSERT INTO questions (id, topic_id, position, text, options, stage)
           VALUES (gen_random_uuid(), $1, $2, $3, $4, $5)`,
          [topic.rows[0].id, index, `E2E question ${index + 1}?`, options, stage],
        );
      }
    }

    return { id, slug, title, language };
  });
}

/** Deletes a template addTemplate made; its topics and questions go with it. */
export async function deleteTemplate(id: string) {
  await withLibrary((client) => client.query("DELETE FROM sets WHERE id = $1", [id]));
}
