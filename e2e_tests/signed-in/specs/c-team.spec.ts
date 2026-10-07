import type { Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { openTab, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, throwawayEmail } from "../helpers/users"

/** Picks a role in the open role menu, which closes on the pick: left open, it would cover the
 * dialog's buttons. */
async function pickRole(page: Page, role: string) {
  const menu = page.getByRole("menu")
  await menu.getByRole("menuitemradio", { name: new RegExp(`^${role}`) }).click()
  await expect(menu).toBeHidden()
  await shot(page, `role-picked-${role}`)
}

// The team tab: a viewer invited and their role changed by the owner; the viewer then sees the
// company without the ways to change it, and can still download and share reports.
test("owner adds a viewer, who sees the company read-only", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  // A candidate, so the candidates tab has reports to download and share.
  await inviteCandidate(owner, interviewId, throwawayEmail("candidate"))
  const viewer = throwawayEmail("viewer")

  await visit(owner, `/companies/${company.id}/interviews`)
  await openTab(owner, "Team")
  await shot(owner, "team")
  await owner.getByRole("button", { name: "Add member" }).click()
  const dialog = owner.getByRole("dialog")
  await dialog.getByLabel("Member email").fill(viewer)
  // The role select: a gray pill opening a menu of roles, each with what it may do.
  await dialog.getByRole("button", { name: "Role" }).click()
  const menu = owner.getByRole("menu")
  await expect(menu.getByText("Sees interviews and results, shares reports. Changes nothing.")).toBeVisible()
  await expect(menu.getByText("Creates and changes interviews, invites candidates, tops up.")).toBeVisible()
  await shot(owner, "role-menu")
  await pickRole(owner, "viewer")
  await expect(dialog.getByRole("button", { name: "Role" })).toHaveText("viewer")
  await shot(owner, "add-member-dialog")
  await dialog.getByRole("button", { name: "Add member" }).click()

  // The new row: invited, its role select, the trash icon and the join link.
  const row = owner.getByRole("listitem").filter({ hasText: viewer })
  await expect(row.getByText("Invited")).toBeVisible()
  await expect(row.getByRole("button", { name: "Role" })).toHaveText("viewer")
  await expect(row.getByRole("button", { name: "Remove" })).toBeVisible()
  await shot(owner, "member-row")

  // The role changes in place, and back.
  await row.getByRole("button", { name: "Role" }).click()
  await pickRole(owner, "admin")
  await expect(row.getByRole("button", { name: "Role" })).toHaveText("admin")
  await shot(owner, "member-admin")
  await row.getByRole("button", { name: "Role" }).click()
  await pickRole(owner, "viewer")
  await expect(row.getByRole("button", { name: "Role" })).toHaveText("viewer")

  // The trash icon asks first; kept here.
  await row.getByRole("button", { name: "Remove" }).click()
  await expect(owner.getByRole("dialog")).toContainText(viewer)
  await shot(owner, "remove-confirm")
  await owner.getByRole("dialog").getByRole("button", { name: "Keep" }).click()

  const joinLink = await row.getByRole("textbox").inputValue()
  const page = await signInAs(viewer)
  await visit(page, new URL(joinLink).pathname)
  await shot(page, "join")
  await page.getByRole("button", { name: "Join company" }).click()
  await expect(page).toHaveURL(/\/companies$/)
  await page.getByText(company.name).first().click()

  // Read-only: no New interview, the name isn't a button to rename it, no verify.
  await expect(page.getByRole("heading", { name: company.name })).toBeVisible()
  await expect(page.getByRole("button", { name: "New interview" })).toHaveCount(0)
  await expect(page.getByRole("heading").getByRole("button")).toHaveCount(0)
  await expect(page.getByRole("button", { name: "Verify" })).toHaveCount(0)
  await shot(page, "viewer-interviews")

  await visit(page, `/companies/${company.id}/interviews/${interviewId}`)
  await expect(page.getByRole("button", { name: "Manage questions" }).first()).toBeVisible()
  await expect(page.getByRole("heading").getByRole("button")).toHaveCount(0)
  await expect(page.getByRole("button", { name: "Settings" })).toHaveCount(0)
  await shot(page, "viewer-interview")

  await visit(page, `/companies/${company.id}/interviews/${interviewId}?tab=candidates`)
  await expect(page.getByRole("button", { name: "Download PDF" })).toBeVisible()
  await expect(page.getByRole("button", { name: "Share report" })).toBeVisible()
  await expect(page.getByRole("button", { name: "New candidate(s)" })).toHaveCount(0)
  await shot(page, "viewer-candidates")
  // A sort menu closes on the pick too.
  await page.getByRole("button", { name: "Sort by: grade" }).click()
  await page.getByRole("menu").getByRole("menuitemradio", { name: "date" }).click()
  await expect(page.getByRole("menu")).toBeHidden()
  await expect(page).toHaveURL(/sort=date/)
  await expect(page.getByRole("button", { name: "Sort by: date" })).toBeVisible()

  // Their own row in the team: a role badge, nothing to change.
  await visit(page, `/companies/${company.id}/members`)
  await expect(page.getByRole("button", { name: "Add member" })).toHaveCount(0)
  await expect(page.getByRole("button", { name: "Role" })).toHaveCount(0)
  await shot(page, "viewer-team")
})
