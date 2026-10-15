import pg from "pg";

import { POSTGRES_HOST } from "../constants";
import { env } from "./env";

/** Runs `work` on a fresh connection to one of the stack's databases. */
export async function withDatabase<T>(
  database: string,
  work: (client: pg.Client) => Promise<T>,
) {
  const client = new pg.Client({
    host: POSTGRES_HOST,
    user: "prepza",
    password: env("POSTGRES_PASSWORD"),
    database,
  });
  await client.connect();

  try {
    return await work(client);
  } finally {
    await client.end();
  }
}

/** The token in the invite link a candidate is emailed, read from the companies database like
 * e2e.py does: the email itself isn't readable. Only rows the tests made are asked for. */
export async function inviteToken(email: string): Promise<string> {
  return withDatabase("companies", async (client) => {
    const result = await client.query(
      "SELECT token FROM candidate_invites WHERE email = $1 ORDER BY created_at DESC LIMIT 1",
      [email.toLowerCase()],
    );

    if (!result.rows[0]) {
      throw new Error("no invite for that email");
    }

    return result.rows[0].token;
  });
}

/** How many emails with their own link a candidate who started through a test's link got:
 * the candidate.joined events saved for them. */
export async function joinedEmails(email: string): Promise<number> {
  return withDatabase("companies", async (client) => {
    const result = await client.query(
      "SELECT count(*) FROM outbox WHERE event_type = 'candidate.joined' AND data->>'email' = $1",
      [email.toLowerCase()],
    );

    return Number(result.rows[0].count);
  });
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
      [companyId],
    );

    return found.rows[0].id as string;
  });
  await withDatabase("companies", (client) =>
    client.query(
      `UPDATE interviews SET set_id = NULL, title = NULL, generation_id = $2,
         generation_failed = true WHERE id = $1`,
      [interviewId, generationId],
    ),
  );
}

/** A throwaway company verified on `domain`, as a superadmin's approval leaves it (the
 * verification flow itself has its own tests). */
export async function verifyCompany(companyId: string, domain: string) {
  await withDatabase("companies", (client) =>
    client.query(
      `UPDATE companies SET website_domain = $2, verified_domain = $2,
         verification_status = 'approved' WHERE id = $1`,
      [companyId, domain],
    ),
  );
}

/** Moves a throwaway candidate's invite to `iso`, as if they were invited then. */
export async function setInvitedAt(email: string, iso: string) {
  await withDatabase("companies", (client) =>
    client.query(
      "UPDATE candidate_invites SET created_at = $2 WHERE email = $1",
      [email, iso],
    ),
  );
}

/** Expires a throwaway candidate's invites, as the daily job does to one not started in time. */
export async function expireInvite(email: string) {
  await withDatabase("companies", (client) =>
    client.query("UPDATE candidate_invites SET status = 'expired' WHERE email = $1", [email]),
  );
}
