import { expect, test } from "../fixtures"
import { createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { expireInvite, inviteToken } from "../helpers/db"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, throwawayEmail } from "../helpers/users"

// An invite not started in time expired: its page says so and that the company can send it
// again, rather than only that the link isn't valid.
test("an expired invite asks the candidate to have it sent again", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const email = throwawayEmail("expired")
  await inviteCandidate(owner, interviewId, email)
  const token = await inviteToken(email)
  await expireInvite(email)

  const candidate = await signInAs(email)
  await visit(candidate, `/invite/${token}`)
  await expect(
    candidate.getByText("This invite has expired. Ask the company to send it again."),
  ).toBeVisible()
  await expect(candidate.getByRole("button", { name: "Accept & Start" })).toHaveCount(0)
  await shot(candidate, "expired")
})
