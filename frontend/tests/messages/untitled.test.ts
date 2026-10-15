import { readdirSync, readFileSync } from "node:fs"
import path from "node:path"
import { createTranslator } from "next-intl"
import { describe, expect, it } from "vitest"

const DIR = path.resolve(__dirname, "../../messages")
// Notifications that name an interview; the bell passes "none" when it has no title yet.
const KINDS = [
  "question_flagged",
  "question_fixed",
  "candidate_finished",
  "invite_undelivered",
  "interview_ready",
  "ats_not_invited",
]
const VALUES = {
  topic: "SQL",
  email: "a@b.c",
  grade: "none",
  ats: "Greenhouse",
  reason: "credits",
}

describe("a notification about an interview without a title", () => {
  for (const file of readdirSync(DIR).filter((name) =>
    name.endsWith(".json")
  )) {
    const locale = file.replace(".json", "")
    const messages = JSON.parse(readFileSync(path.join(DIR, file), "utf8"))
    const t = createTranslator({
      locale,
      messages,
      namespace: "notifications.kinds",
    })

    it(`names no title in ${locale}, and quotes one that's there`, () => {
      for (const kind of KINDS) {
        for (const count of [1, 2]) {
          const untitled = t(kind, { ...VALUES, count, title: "none" })
          const titled = t(kind, { ...VALUES, count, title: "Backend" })

          expect(untitled, `${kind} ${count}`).not.toMatch(/none|“”|«»|„“|「」/)
          expect(titled, `${kind} ${count}`).toContain("Backend")
        }
      }
    })
  }
})
