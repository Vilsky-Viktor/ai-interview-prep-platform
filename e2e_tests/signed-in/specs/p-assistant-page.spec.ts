import type { Page, Response } from "@playwright/test"

import { expect, test } from "../fixtures"
import { createCompany, createInterview, finishOneAnswer, inviteCandidate } from "../helpers/api"
import { openPanel } from "../helpers/assistant"
import { env } from "../helpers/env"
import { visit } from "../helpers/navigation"
import { ownerEmail, throwawayEmail } from "../helpers/users"

// The assistant knows the page it's asked on, with the real service and model (two messages, a
// cent or so): on an interview's candidates tab, "here" means that interview.

/** The events of one answer, as the chat route streamed them. */
async function events(response: Response) {
  return (await response.text())
    .split("\n")
    .filter((line) => line.startsWith("data: "))
    .map((line) => JSON.parse(line.slice(6)))
}

/** Sends a message from the open panel; the request's body and the answer's events. */
async function ask(owner: Page, message: string) {
  const panel = owner.getByRole("dialog")
  const answered = owner.waitForResponse(
    (response) => response.url().endsWith("/api/assistant/chat"),
    { timeout: 120_000 }
  )
  await panel.getByRole("textbox").fill(message)
  await panel.locator("button[type=submit]").click()
  const response = await answered

  return { sent: response.request().postDataJSON(), answer: await events(response) }
}

test("the assistant answers about the page and the interview on screen", async ({ signInAs }) => {
  // CI's stack has no OpenAI key.
  test.skip(!env("OPENAI_API_KEY"), "No OpenAI key: the assistant can't answer")
  test.setTimeout(300_000)
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const elsewhere = await createInterview(owner, company.id)
  const here = await createInterview(owner, company.id)
  // One candidate in each interview, by name.
  const people = [
    [elsewhere, throwawayEmail("other"), "Olga Elsewhere"],
    [here, throwawayEmail("here"), "Hana Here"],
  ]

  for (const [interviewId, email, name] of people) {
    await inviteCandidate(owner, interviewId, email)
    await finishOneAnswer(await signInAs(email, {}, name), email)
  }

  await visit(owner, `/companies/${company.id}/interviews/${here}?tab=candidates`)
  const panel = await openPanel(owner)

  // What the page offers: the panel sends the page, and the answer reads its guide.
  const guide = await ask(owner, "What can I do here?")
  expect(guide.sent.page).toMatchObject({
    key: "interviewCandidates",
    company_id: company.id,
    interview_id: here,
    path: `/companies/${company.id}/interviews/${here}?tab=candidates`,
  })
  expect(guide.answer).toContainEqual({
    tool: expect.objectContaining({ name: "get_page_guide", state: "done" }),
  })
  expect(guide.answer.some((event) => event.done)).toBe(true)
  expect(guide.answer.some((event) => event.delta)).toBe(true)

  // "Here" is the interview on screen: its candidate, never the other interview's.
  const best = await ask(owner, "Who's best here?")
  // The text as it streamed, and the rows shown under it.
  const said = best.answer.map((event) => event.delta ?? JSON.stringify(event)).join("")
  expect(best.answer.some((event) => event.done)).toBe(true)
  expect(said).toContain("Hana")
  expect(said).not.toContain("Olga")
  await expect(panel.getByText(/Hana/).first()).toBeVisible()
})
