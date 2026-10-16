import type { Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { companyUnsubscribePath } from "../helpers/unsubscribe"
import { ownerEmail, throwawayEmail } from "../helpers/users"

// Every optional email, as Settings → Emails names them.
const SETTINGS = [
  /^Activity digest/,
  /^Candidates who finished$/,
  /^Undelivered invites$/,
  /^ATS candidates not invited$/,
  /^Interviews ready$/,
  /^Reminders/,
  /^Product updates and news/,
  /^Offers and promotions/,
]

/** Finds the address on the admin zone's emails tab, typed in capitals. */
async function find(page: Page, address: string) {
  await page.getByRole("textbox", { name: "Email address" }).fill(address.toUpperCase())
  await page.getByRole("button", { name: "Find" }).click()
  await expect(page.getByText(`${address} has an account.`, { exact: false })).toBeVisible()
}

/** A company's row in "Emails from companies". */
function companyRow(page: Page, name: string) {
  return page.locator("div.divide-y > div", { hasText: name })
}

// Someone asked prepza by email to stop its emails: a superadmin finds the address, turns its
// account's optional emails off and stops one inviting company's emails, then resumes them. Only
// the person turns marketing on, and a stop they made from an email's link stays theirs.
test("superadmin stops and resumes the emails to an address", async ({
  browser,
  signInAs,
  signInSuperadmin,
}) => {
  const address = throwawayEmail("asked")
  const person = await signInAs(address)
  await person.context().close()
  const companies = []

  for (let i = 0; i < 2; i++) {
    const owner = await signInAs(ownerEmail())
    const company = await createCompany(owner)
    await inviteCandidate(owner, await createInterview(owner, company.id), address)
    companies.push(company)
  }

  // The person stopped the second company's emails themselves, from an email's link.
  const context = await browser.newContext()
  const guest = await context.newPage()
  await visit(guest, companyUnsubscribePath(address, companies[1].id, companies[1].name))
  await guest.getByRole("button", { name: "Confirm" }).click()
  await expect(guest.getByRole("heading", { name: /^You're unsubscribed/ })).toBeVisible()
  await context.close()

  const superadmin = await signInSuperadmin()
  await visit(superadmin, "/superadmin/emails")
  await shot(superadmin, "emails-empty")
  await find(superadmin, address)

  // The account's settings as a new user has them: updates on (the first sign-in), offers off.
  await expect(superadmin.getByRole("checkbox", { name: /^Reminders/ })).toBeChecked()
  await expect(superadmin.getByRole("checkbox", { name: /^Offers and promotions/ })).not.toBeChecked()

  await expect(companyRow(superadmin, companies[0].name)).toContainText("Emails are sent")
  const theirs = companyRow(superadmin, companies[1].name)
  await expect(theirs).toContainText("They stopped all emails themselves")
  await expect(theirs.getByRole("button")).toHaveCount(0)

  await shot(superadmin, "emails-found")

  // Every optional email off, still off once found again after a reload.
  await superadmin.getByRole("button", { name: "Turn off all optional emails" }).click()

  for (const name of SETTINGS) {
    await expect(superadmin.getByRole("checkbox", { name })).not.toBeChecked()
  }

  await superadmin.reload()
  await find(superadmin, address)

  for (const name of SETTINGS) {
    await expect(superadmin.getByRole("checkbox", { name })).not.toBeChecked()
  }

  // Marketing goes back on only by the person's own choice.
  await superadmin.getByRole("checkbox", { name: /^Offers and promotions/ }).click()
  await expect(
    superadmin.getByText("Only the person can turn on product updates and offers.", { exact: false })
  ).toBeVisible()
  await shot(superadmin, "emails-marketing-refused")
  await superadmin.reload()
  await find(superadmin, address)
  await expect(superadmin.getByRole("checkbox", { name: /^Offers and promotions/ })).not.toBeChecked()

  // One company's emails stopped (the person's own stop stays as it is); then resumed.
  const stopped = companies[0].name
  await companyRow(superadmin, stopped).getByRole("button", { name: "Stop emails" }).click()
  await expect(companyRow(superadmin, stopped)).toContainText("All emails stopped")
  await expect(theirs).toContainText("They stopped all emails themselves")
  await shot(superadmin, "emails-stopped")
  await superadmin.setViewportSize({ width: 390, height: 844 })
  await shot(superadmin, "emails-stopped-phone")
  await superadmin.setViewportSize({ width: 1280, height: 800 })
  await companyRow(superadmin, stopped).getByRole("button", { name: "Resume emails" }).click()
  await expect(companyRow(superadmin, stopped)).toContainText("Emails are sent")
  await expect(companyRow(superadmin, stopped).getByRole("button", { name: "Stop emails" })).toBeVisible()
})

test("anyone else gets not found on the emails tab", async ({ signInAs }) => {
  const user = await signInAs(ownerEmail())
  await visit(user, "/superadmin/emails")
  await expect(user.getByRole("heading", { name: "Page not found" })).toBeVisible()
  await expect(user.getByRole("textbox", { name: "Email address" })).toHaveCount(0)
})
