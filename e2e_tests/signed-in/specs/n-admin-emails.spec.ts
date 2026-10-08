import type { Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
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
// account's optional emails off and stops one inviting company's emails, then resumes them.
test("superadmin stops and resumes the emails to an address", async ({
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
    companies.push(company.name)
  }

  const superadmin = await signInSuperadmin()
  await visit(superadmin, "/superadmin/emails")
  await shot(superadmin, "emails-empty")
  await find(superadmin, address)

  // The account's settings as a new user has them: updates on (the first sign-in), offers off.
  await expect(superadmin.getByRole("checkbox", { name: /^Reminders/ })).toBeChecked()
  await expect(superadmin.getByRole("checkbox", { name: /^Offers and promotions/ })).not.toBeChecked()

  for (const name of companies) {
    await expect(companyRow(superadmin, name)).toContainText("Emails are sent")
  }

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

  // One company's emails stopped, the other's still sent; then resumed.
  const [stopped, other] = companies
  await companyRow(superadmin, stopped).getByRole("button", { name: "Stop emails" }).click()
  await expect(companyRow(superadmin, stopped)).toContainText("All emails stopped")
  await expect(companyRow(superadmin, other)).toContainText("Emails are sent")
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
