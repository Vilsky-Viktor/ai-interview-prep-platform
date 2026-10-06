import pg from "pg"

import { POSTGRES_HOST } from "../constants"
import { env } from "./env"

/** The token in the invite link a candidate is emailed, read from the companies database like
 * e2e.py does: the email itself isn't readable. Only rows the tests made are asked for. */
export async function inviteToken(email: string): Promise<string> {
  const client = new pg.Client({
    host: POSTGRES_HOST,
    user: "prepza",
    password: env("POSTGRES_PASSWORD"),
    database: "companies",
  })
  await client.connect()

  try {
    const result = await client.query(
      "SELECT token FROM candidate_invites WHERE email = $1 ORDER BY created_at DESC LIMIT 1",
      [email.toLowerCase()]
    )

    if (!result.rows[0]) {
      throw new Error("no invite for that email")
    }

    return result.rows[0].token
  } finally {
    await client.end()
  }
}
