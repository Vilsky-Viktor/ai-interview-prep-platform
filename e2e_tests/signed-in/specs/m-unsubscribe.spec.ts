import { expect, test } from "../fixtures"
import { createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { EMAIL_BOXES, emailBoxes } from "../helpers/emails"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { tokenOf } from "../helpers/sign-in"
import {
  companyUnsubscribePath,
  confirmUnsubscribe,
  userUnsubscribePath,
} from "../helpers/unsubscribe"
import { ownerEmail, throwawayEmail } from "../helpers/users"

// A user's "Unsubscribe" link from the activity digest: confirmed, it turns the digest's four
// kinds off, as Settings shows.
test("a user unsubscribes from the activity digest", async ({ signInAs }) => {
  const user = await signInAs(ownerEmail())
  const jwt = await tokenOf(user)
  const userId = JSON.parse(Buffer.from(jwt.split(".")[1], "base64url").toString()).user_id

  await visit(user, userUnsubscribePath(userId, "digest"))
  await shot(user, "digest")
  await confirmUnsubscribe(user)
  // Done, signed in: the way to the email settings.
  const settings = user.getByRole("main").locator('a[href="/settings"]')
  await expect(settings).toBeVisible()
  await shot(user, "digest-done")

  await settings.click()
  await expect(user).toHaveURL(/\/settings$/)
  const boxes = emailBoxes(user)
  await expect(boxes.nth(EMAIL_BOXES.digest)).not.toBeChecked()

  for (const kind of EMAIL_BOXES.kinds) {
    await expect(boxes.nth(kind)).not.toBeChecked()
  }

  // Only the digest: reminders stay on.
  await expect(boxes.nth(EMAIL_BOXES.reminders)).toBeChecked()
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
  // The page names the company whose emails stop.
  await expect(guest.getByRole("main")).toContainText(company.name)
  await confirmUnsubscribe(guest)
  // Signed out: nothing left to press, no settings to go to.
  await expect(guest.getByRole("main").getByRole("button")).toHaveCount(0)
  await expect(guest.getByRole("main").locator('a[href="/settings"]')).toHaveCount(0)
  await shot(guest, "company-done")
  await context.close()

  await inviteCandidate(owner, interviewId, candidate)
  await visit(owner, `/companies/${company.id}/interviews/${interviewId}?tab=candidates`)
  const row = owner.getByRole("link").filter({ hasText: candidate })

  // The invite event reaches notifications, which reports it back: it takes a moment. An
  // undelivered invite's status is the list's red one.
  await expect(async () => {
    await owner.reload()
    await expect(row.locator("[data-slot=badge][data-variant=destructive]")).toBeVisible({
      timeout: 3_000,
    })
  }).toPass({ timeout: 90_000, intervals: [2_000] })
  await shot(owner, "invite-undelivered")
})
