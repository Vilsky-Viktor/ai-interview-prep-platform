import { expect, test } from "../fixtures"
import { createCompany, createInterview, finishOneAnswer, inviteCandidate } from "../helpers/api"
import { PHONE } from "../helpers/layout"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, throwawayEmail } from "../helpers/users"

// Each page a complaint may be about has "copy id", so a user can quote its ID when writing to
// prepza: a company, an interview and a candidate, each copying its own.
test("the company, interview and candidate pages copy their IDs", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  await owner.context().grantPermissions(["clipboard-read", "clipboard-write"])
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const candidate = throwawayEmail("quoted")
  await inviteCandidate(owner, interviewId, candidate)
  const copied = () => owner.evaluate(() => navigator.clipboard.readText())

  await visit(owner, `/companies/${company.id}/interviews`)
  await owner.getByRole("button", { name: "Copy ID" }).click()
  // The check shows for a moment, then the copy icon again.
  await expect(owner.getByRole("button", { name: "ID copied" })).toBeVisible()
  expect(await copied()).toBe(company.id)
  await shot(owner, "company-copied")
  await expect(owner.getByRole("button", { name: "Copy ID" })).toBeVisible()

  await visit(owner, `/companies/${company.id}/interviews/${interviewId}?tab=candidates`)
  await owner.getByRole("button", { name: "Copy ID" }).click()
  expect(await copied()).toBe(interviewId)
  await shot(owner, "interview")

  await owner.getByRole("link").filter({ hasText: "quoted" }).click()
  await expect(owner.getByRole("heading", { name: candidate })).toBeVisible()
  const candidatePage = owner.url()
  await owner.getByRole("button", { name: "Copy ID" }).click()
  expect(await copied()).toBe(candidatePage.split("/").pop())
  await shot(owner, "candidate")

  await owner.setViewportSize(PHONE)
  await visit(owner, `/companies/${company.id}/interviews`)
  await shot(owner, "company-phone")
  await owner.goto(candidatePage)
  await expect(owner.getByRole("button", { name: "Copy ID" })).toBeVisible()
  await shot(owner, "candidate-phone")
})

// The account's ID: a button in Settings, and a small one under the email in the account menu.
test("Settings and the account menu copy the account's ID", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  await owner.context().grantPermissions(["clipboard-read", "clipboard-write"])
  const copied = () => owner.evaluate(() => navigator.clipboard.readText())

  await visit(owner, "/settings")
  await owner.getByRole("button", { name: "Copy ID" }).click()
  const uid = await copied()
  expect(uid).toMatch(/^\w{20,}$/)
  await shot(owner, "settings")

  await owner.getByRole("button", { name: "Account", exact: true }).click()
  await owner.getByRole("menuitem", { name: "Copy ID" }).click()
  // The menu stays open to show the check mark.
  await expect(owner.getByRole("menuitem", { name: "ID copied" })).toBeVisible()
  expect(await copied()).toBe(uid)
  await shot(owner, "account-menu")
  await owner.keyboard.press("Escape")

  await owner.setViewportSize(PHONE)
  await visit(owner, "/settings")
  await shot(owner, "settings-phone")
})

// A long email has no spaces to wrap at: on a phone it breaks before the @ rather than running
// off the screen, and the note under the results spans the screen.
test("a long email wraps on a phone", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const email = throwawayEmail("averyveryverylongcandidateaddress")
  await inviteCandidate(owner, interviewId, email)
  await finishOneAnswer(await signInAs(email), email)

  await owner.setViewportSize(PHONE)
  await visit(owner, `/companies/${company.id}/interviews/${interviewId}?tab=candidates`)
  await owner.getByRole("link").filter({ hasText: "averyveryverylong" }).click()
  await expect(
    owner.getByText("The score supports your decision", { exact: false }).first()
  ).toBeVisible()
  // Nothing wider than the screen.
  expect(await owner.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
    PHONE.width
  )
  await shot(owner, "long-email-phone")
})
