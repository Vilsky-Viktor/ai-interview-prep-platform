import { expect, test } from "../fixtures"
import { api, createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { inviteToken } from "../helpers/db"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, throwawayEmail } from "../helpers/users"

type Row = { id: string; tab_leaves: number }

// A page leave counts when it lasted 2 seconds or more: a moment's one (a notification taking
// focus) is kept but not counted. Signals are said to be the browser's report, not proof.
test("only a real page leave counts, and the results say signals are the browser's report", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const email = throwawayEmail("signals")
  await inviteCandidate(owner, interviewId, email)

  const candidate = await signInAs(email)
  await visit(candidate, `/invite/${await inviteToken(email)}`)
  await candidate.getByRole("button", { name: "Accept & Start" }).click()
  await expect(candidate).toHaveURL(/\/sessions\//)
  await expect(candidate.getByRole("main").locator("button[aria-pressed]").first()).toBeVisible()

  async function leave(milliseconds: number) {
    await candidate.evaluate(() => window.dispatchEvent(new Event("blur")))
    await candidate.waitForTimeout(milliseconds)
    await candidate.evaluate(() => window.dispatchEvent(new Event("focus")))
  }

  await leave(300)
  await leave(2_500)

  const leaves = async () => {
    const [row] = await api<Row[]>(owner, "GET", `/companies/interviews/${interviewId}/candidates`)

    return row?.tab_leaves
  }

  await expect.poll(leaves).toBe(1)

  const [row] = await api<Row[]>(owner, "GET", `/companies/interviews/${interviewId}/candidates`)
  await visit(owner, `/companies/${company.id}/interviews/${interviewId}/candidates/${row.id}`)
  await expect(owner.getByText(/reported by the candidate's browser: a reason to look closer, not proof/).first()).toBeVisible()
  await shot(owner, "results-note")
})
