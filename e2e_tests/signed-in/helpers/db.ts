import pg from "pg"

import { POSTGRES_HOST } from "../constants"
import { env } from "./env"

/** Runs `work` on a fresh connection to one of the stack's databases. */
async function withDatabase<T>(database: string, work: (client: pg.Client) => Promise<T>) {
  const client = new pg.Client({
    host: POSTGRES_HOST,
    user: "prepza",
    password: env("POSTGRES_PASSWORD"),
    database,
  })
  await client.connect()

  try {
    return await work(client)
  } finally {
    await client.end()
  }
}

/** The token in the invite link a candidate is emailed, read from the companies database like
 * e2e.py does: the email itself isn't readable. Only rows the tests made are asked for. */
export async function inviteToken(email: string): Promise<string> {
  return withDatabase("companies", async (client) => {
    const result = await client.query(
      "SELECT token FROM candidate_invites WHERE email = $1 ORDER BY created_at DESC LIMIT 1",
      [email.toLowerCase()]
    )

    if (!result.rows[0]) {
      throw new Error("no invite for that email")
    }

    return result.rows[0].token
  })
}

/** A throwaway template with one topic of `questions` private questions, saved straight into the
 * library database (a real one needs an OpenAI generation). A company can copy it only with at
 * least 10 (MIN_COPY_QUESTIONS in services/library); practice lists it either way. German, so
 * nothing that picks English templates to make interviews from (templatesBySize, the load
 * tests) takes it. Its right answers hold `inline code`. */
export async function addTemplate(title: string, questions: number): Promise<string> {
  return withDatabase("library", async (client) => {
    const set = await client.query(
      `INSERT INTO sets (id, kind, owner_type, owner_id, title, source_text, level, language,
         requirements, topic_count, created_at)
       VALUES (gen_random_uuid(), 'template', 'platform', 'prepza', $1, 'E2E', 'basic', 'de',
         '[]', 1, now())
       RETURNING id`,
      [title]
    )
    const id = set.rows[0].id
    const topic = await client.query(
      `INSERT INTO topics (id, set_id, position, title, subtopics)
       VALUES (gen_random_uuid(), $1, 0, 'E2E topic', '[]') RETURNING id`,
      [id]
    )
    const options = JSON.stringify([
      { answer: "Check `if is_member:` first", correct: true },
      { answer: "Skip the check", correct: false },
    ])

    for (let position = 0; position < questions; position++) {
      await client.query(
        `INSERT INTO questions (id, topic_id, position, text, options, stage)
         VALUES (gen_random_uuid(), $1, $2, $3, $4, 'private')`,
        [topic.rows[0].id, position, `E2E question ${position + 1}?`, options]
      )
    }

    return id
  })
}

/** Deletes a template addTemplate made; its topics and questions go with it, and the companies'
 * copies stay. */
export async function deleteTemplate(id: string) {
  await withDatabase("library", (client) => client.query("DELETE FROM sets WHERE id = $1", [id]))
}

/** A Workable connection for a throwaway company, saved straight into the companies database
 * (a real one needs a Workable account), with one job linked to `interviewId`. Its key is a
 * placeholder, so anything that calls Workable with it marks it broken. Deleting the company
 * deletes both. */
export async function addAtsConnection(
  companyId: string,
  interviewId: string,
  candidates: { invited?: number; notInvited?: number } = {}
) {
  await withDatabase("companies", async (client) => {
    const connection = await client.query(
      `INSERT INTO ats_connections (id, company_id, provider, account, credentials, status,
         created_by, created_at)
       VALUES (gen_random_uuid(), $1, 'workable', 'e2e-acme', 'placeholder', 'connected', 'e2e',
         now())
       RETURNING id`,
      [companyId]
    )
    const link = await client.query(
      `INSERT INTO ats_job_links (id, connection_id, interview_id, job_id, job_name, stage_id,
         stage_name, created_at)
       VALUES (gen_random_uuid(), $1, $2, 'E2E01', 'E2E Backend developer', 'assessment',
         'Assessment', now())
       RETURNING id`,
      [connection.rows[0].id, interviewId]
    )
    // Candidates Workable "sent" for the job: invited, and not invited for lack of credits.
    const statuses = [
      ...Array(candidates.invited ?? 0).fill(["invited", null]),
      ...Array(candidates.notInvited ?? 0).fill(["failed", "credits"]),
    ]

    for (const [index, [status, reason]] of statuses.entries()) {
      await client.query(
        `INSERT INTO ats_candidates (id, connection_id, interview_id, link_id, candidate_id,
           email, status, reason, created_at)
         VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, now())`,
        [
          connection.rows[0].id,
          interviewId,
          link.rows[0].id,
          `e2e-${index}`,
          `e2e-${index}@example.com`,
          status,
          reason,
        ]
      )
    }
  })
}
