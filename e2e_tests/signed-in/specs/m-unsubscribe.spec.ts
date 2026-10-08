import { expect, test } from "../fixtures"
import { createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { tokenOf } from "../helpers/sign-in"
import { companyUnsubscribePath, userUnsubscribePath } from "../helpers/unsubscribe"
import { ownerEmail, throwawayEmail } from "../helpers/users"

const KINDS = [
  "Candidates who finished",
  "Undelivered invites",
  "ATS candidates not invited",
  "Interviews ready",
]

// A user's "Unsubscribe" link from the activity digest: confirmed, it turns the digest's four
// kinds off, as Settings shows.
test("a user unsubscribes from the activity digest", async ({ signInAs }) => {
  const user = await signInAs(ownerEmail())
  const jwt = await tokenOf(user)
  const userId = JSON.parse(Buffer.from(jwt.split(".")[1], "base64url").toString()).user_id

  await visit(user, userUnsubscribePath(userId, "digest"))
  await expect(user.getByText("You won't get the activity digest anymore.")).toBeVisible()
  await shot(user, "digest")
  await user.getByRole("button", { name: "Confirm" }).click()
  await expect(user.getByRole("heading", { name: /^You're unsubscribed/ })).toBeVisible()
  await shot(user, "digest-done")

  await user.getByRole("button", { name: "Email settings" }).click()
  await expect(user).toHaveURL(/\/settings$/)
  await expect(user.getByRole("checkbox", { name: /^Activity digest/ })).not.toBeChecked()

  for (const kind of KINDS) {
    await expect(user.getByRole("checkbox", { name: kind, exact: true })).not.toBeChecked()
  }

  // Only the digest: reminders stay on.
  await expect(user.getByRole("checkbox", { name: /^Reminders/ })).toBeChecked()
})

// A candidate's "Don't email me for <company>" link, opened signed out: the company's next
// invite to that address isn't sent, and its candidates list shows it undelivered.
test("a candidate stops a company's emails", async ({ signInAs, browser }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const candidate = throwawayEmail("unsubscribed")

  const context = await browser.newContext()
  const guest = await context.newPage()
  await visit(guest, companyUnsubscribePath(candidate, company.id, company.name))
  await expect(guest.getByText(`You won't get emails from ${company.name} anymore.`)).toBeVisible()
  await guest.getByRole("button", { name: "Confirm" }).click()
  await expect(guest.getByRole("heading", { name: /^You're unsubscribed/ })).toBeVisible()
  // Signed out: no settings to go to.
  await expect(guest.getByRole("button", { name: "Email settings" })).toHaveCount(0)
  await shot(guest, "company-done")
  await context.close()

  await inviteCandidate(owner, interviewId, candidate)
  await visit(owner, `/companies/${company.id}/interviews/${interviewId}?tab=candidates`)
  const row = owner.getByRole("link").filter({ hasText: candidate })

  // The invite event reaches notifications, which reports it back: it takes a moment.
  await expect(async () => {
    await owner.reload()
    await expect(row.getByText("undelivered", { exact: true })).toBeVisible({ timeout: 3_000 })
  }).toPass({ timeout: 90_000, intervals: [2_000] })
  await shot(owner, "invite-undelivered")
})
