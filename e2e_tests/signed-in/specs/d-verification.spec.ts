import type { Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { createCompany } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, randomId } from "../helpers/users"

/** The superadmin's row for this test's company: the only one the test decides on. */
async function requestRow(superadmin: Page, name: string) {
  await visit(superadmin, "/superadmin/verification")

  return superadmin.getByRole("listitem").filter({ hasText: name })
}

// Verification: a website on the owner's own email domain goes for review; the superadmin
// declines it, a rename sends it again, and the superadmin approves it.
test("company verification: pending, declined, renamed, approved", async ({
  signInAs,
  signInSuperadmin,
}) => {
  // A throwaway domain that isn't a free mail service, with the owner's email on it.
  const domain = `e2e-${randomId()}.test`
  const owner = await signInAs(ownerEmail(domain))
  const company = await createCompany(owner)
  const interviews = `/company/${company.id}/interviews`
  await visit(owner, interviews)

  await owner.getByRole("button", { name: "Verify" }).click()
  await owner.getByRole("dialog").getByLabel("Company website").fill(domain)
  await shot(owner, "verify-dialog")
  await owner.getByRole("dialog").getByRole("button", { name: "Save" }).click()
  const pending = owner.getByRole("button", { name: "Pending verification" })
  await expect(pending).toBeVisible()
  await pending.hover()
  await expect(owner.getByText("Pending verification", { exact: true })).toBeVisible()
  await shot(owner, "pending")

  const superadmin = await signInSuperadmin()
  let row = await requestRow(superadmin, company.name)
  await expect(row.getByText("waiting for review")).toBeVisible()
  await expect(row.getByText(domain)).toBeVisible()
  await shot(superadmin, "superadmin-pending")
  await row.getByRole("button", { name: "Decline" }).click()
  const reason = "E2E: the website doesn't match the name."
  await superadmin.getByRole("dialog").getByLabel("Reason (optional)").fill(reason)
  await shot(superadmin, "decline-dialog")
  await superadmin.getByRole("dialog").getByRole("button", { name: "Decline" }).click()
  await expect(row.getByText("declined", { exact: true })).toBeVisible()
  await expect(row.getByText(`Reason: ${reason}`)).toBeVisible()
  await shot(superadmin, "superadmin-declined")

  // The company sees why, in the verify dialog.
  await visit(owner, interviews)
  await expect(pending).toHaveCount(0)
  await owner.getByRole("button", { name: "Verify" }).click()
  await expect(owner.getByRole("dialog").getByText(`Declined: ${reason}`)).toBeVisible()
  await shot(owner, "declined")
  await owner.keyboard.press("Escape")

  // A rename sends it for review again; the field says so while renaming.
  const renamed = `${company.name} Renamed`
  await owner.getByRole("heading").getByRole("button", { name: company.name }).click()
  await expect(owner.getByText("Renaming sends your company for verification again.")).toBeVisible()
  await shot(owner, "rename-hint")
  await owner.getByLabel("Title").fill(renamed)
  await owner.getByLabel("Title").press("Enter")
  await expect(owner.getByRole("heading", { name: renamed })).toBeVisible()
  await visit(owner, interviews)
  await expect(pending).toBeVisible()
  await shot(owner, "pending-again")

  row = await requestRow(superadmin, renamed)
  await expect(row.getByText("waiting for review")).toBeVisible()
  await row.getByRole("button", { name: "Approve" }).click()
  await expect(row.getByText("approved", { exact: true })).toBeVisible()
  await shot(superadmin, "superadmin-approved")

  await visit(owner, interviews)
  await expect(owner.getByRole("img", { name: `Verified: ${domain}` })).toBeVisible()
  await shot(owner, "verified")
})
