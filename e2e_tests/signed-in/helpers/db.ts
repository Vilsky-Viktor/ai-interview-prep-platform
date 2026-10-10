import { randomUUID } from "node:crypto"

import pg from "pg"

import { GREENHOUSE_E2E_SECRET, POSTGRES_HOST } from "../constants"
import { env } from "./env"
import { fernetEncrypt } from "./fernet"

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

/** An ATS connection for a throwaway company, saved straight into the ats database (a real one
 * needs an ATS account), with one job linked to `interviewId`. Workable's key is a placeholder,
 * so anything that calls Workable with it marks it broken; Greenhouse's is sealed for real, as
 * its page shows the web hook's secret key from it. Deleting the company deletes both (the ats
 * service handles its company.deleted event). */
export async function addAtsConnection(
  companyId: string,
  interviewId: string,
  candidates: { invited?: number; notInvited?: number } = {},
  provider: "workable" | "greenhouse" | "teamtailor" | "recruitee" | "breezy" = "workable"
) {
  // Sealed for real where the page reads them (the web hook's address and secret key).
  const sealed = {
    workable: null,
    greenhouse: { client_id: "e2e", client_secret: "e2e", webhook_secret: GREENHOUSE_E2E_SECRET },
    teamtailor: { host: "https://api.teamtailor.com", key: "e2e" },
    recruitee: { company: "e2e-acme", token: "e2e" },
    breezy: { company: "e2e", token: "e2e", webhook_id: "e2e", webhook_secret: "e2e" },
  }[provider]
  const credentials = sealed
    ? fernetEncrypt(env("ATS_ENCRYPTION_KEY"), JSON.stringify(sealed))
    : "placeholder"
  const account = {
    workable: "e2e-acme",
    greenhouse: "",
    teamtailor: "E2E Acme",
    recruitee: "e2e-acme",
    breezy: "E2E Acme",
  }[provider]

  await withDatabase("ats", async (client) => {
    const connection = await client.query(
      `INSERT INTO ats_connections (id, company_id, provider, account, credentials, status,
         created_by, created_at)
       VALUES (gen_random_uuid(), $1, $2, $3, $4, 'connected', 'e2e', now())
       RETURNING id`,
      [companyId, provider, account, credentials]
    )
    const link = await client.query(
      `INSERT INTO ats_job_links (id, connection_id, interview_id, job_id, job_name, stage_id,
         stage_name, created_at)
       VALUES (gen_random_uuid(), $1, $2, 'E2E01', 'E2E Backend developer', 'assessment',
         'Assessment', now())
       RETURNING id`,
      [connection.rows[0].id, interviewId]
    )
    // Candidates the ATS "sent" for the job: invited, and not invited for lack of credits.
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

/** A Slack channel for a throwaway company, saved straight into the notifications database (a
 * real one needs prepza's Slack app and a workspace). Its web hook is a placeholder: nothing is
 * posted with it. Deleting the company deletes it. */
export async function addSlackConnection(companyId: string) {
  await withDatabase("notifications", (client) =>
    client.query(
      `INSERT INTO slack_connections (company_id, team, channel, webhook, token, kinds, status,
         created_by, created_at)
       VALUES ($1, 'E2E Acme', '#hiring', 'placeholder', 'placeholder',
         '["candidate_finished", "ats_not_invited", "invite_undelivered", "auto_top_up_failed"]',
         'connected', 'e2e', now())`,
      [companyId]
    )
  )
}

/** Marks a throwaway company's web hook as failing, as the api service does after days of
 * retries, without waiting for them. */
export async function markWebhookFailing(url: string, companyId: string) {
  await withDatabase("api", (client) =>
    client.query("UPDATE webhooks SET failing = true WHERE url = $1 AND company_id = $2", [
      url,
      companyId,
    ])
  )
}

/** Turns a throwaway company's interview into one whose generation failed: a failed generation
 * in the generation database, and the interview waiting on it, marked as companies marks it on
 * generation's failed event. */
export async function failGeneration(interviewId: string, companyId: string) {
  const generationId = await withDatabase("generation", async (client) => {
    const found = await client.query(
      `INSERT INTO generations (id, owner_uid, kind, company_id, text, language, status)
       VALUES (gen_random_uuid(), 'e2e', 'interview', $1, 'E2E', 'en', 'failed')
       RETURNING id`,
      [companyId]
    )

    return found.rows[0].id as string
  })
  await withDatabase("companies", (client) =>
    client.query(
      `UPDATE interviews SET set_id = NULL, title = NULL, generation_id = $2,
         generation_failed = true WHERE id = $1`,
      [interviewId, generationId]
    )
  )
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
      [templateId, oldText]
    )
  )
}

/** Marks a throwaway company's ATS connection broken, as the ats service does when the ATS
 * refuses its key. */
export async function markAtsBroken(companyId: string) {
  await withDatabase("ats", (client) =>
    client.query("UPDATE ats_connections SET status = 'broken' WHERE company_id = $1", [companyId])
  )
}

/** Names who made a throwaway company's ATS connection, as the ats service saves it on connecting. */
export async function nameAtsConnectionMaker(companyId: string, name: string) {
  await withDatabase("ats", (client) =>
    client.query("UPDATE ats_connections SET created_by_name = $2 WHERE company_id = $1", [
      companyId,
      name,
    ])
  )
}

/** AI apps connected to a throwaway user's account, saved straight into the assistant database
 * (a real one needs an AI app going through OAuth): an app and one connection each, the first
 * named the latest. Their tokens are random hashes nothing holds. deleteAiConnections deletes
 * them. */
export async function addAiConnections(userId: string, names: string[]) {
  await withDatabase("assistant", async (client) => {
    for (const [index, name] of names.entries()) {
      const clientId = `e2e-${randomUUID()}`
      await client.query(
        "INSERT INTO oauth_clients (client_id, info, created_at) VALUES ($1, $2, now())",
        [clientId, JSON.stringify({ client_id: clientId, client_name: name, redirect_uris: [] })]
      )
      await client.query(
        `INSERT INTO mcp_grants (id, user_id, client_id, client_name, redirect_host, created_at,
           access_hash, access_expires_at, refresh_hash, refresh_expires_at)
         VALUES (gen_random_uuid(), $1, $2, $3, 'e2e.example.com',
           now() - make_interval(hours => $4), $5, now() + interval '1 hour', $6,
           now() + interval '30 days')`,
        [userId, clientId, name, index, randomUUID(), randomUUID()]
      )
    }
  })
}

/** Deletes a throwaway user's AI apps and connections that addAiConnections made. */
export async function deleteAiConnections(userId: string) {
  await withDatabase("assistant", async (client) => {
    await client.query("DELETE FROM mcp_grants WHERE user_id = $1", [userId])
    // The tests' apps left without a connection (disconnected on the page or just now).
    await client.query(
      `DELETE FROM oauth_clients WHERE client_id LIKE 'e2e-%'
         AND client_id NOT IN (SELECT client_id FROM mcp_grants)`
    )
  })
}
