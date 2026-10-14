import { expect, test } from "../fixtures"
import { createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { inviteToken } from "../helpers/db"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, randomId } from "../helpers/users"

test("superadmin finds, suspends, lifts, renames and deletes a company", async ({
  signInAs,
  signInSuperadmin,
}) => {
  const owner = await signInAs(ownerEmail())
  const name = `E2E Moderated ${randomId()}`
  const company = await createCompany(owner, name)
  const interviewId = await createInterview(owner, company.id)
  const candidate = `candidate-${randomId()}@example.com`
  await inviteCandidate(owner, interviewId, candidate)
  const invitePath = `/invite/${await inviteToken(candidate)}`

  // An unverified company: the invite says so, quietly.
  await visit(owner, invitePath)
  await expect(owner.getByText("prepza hasn't verified this company.")).toBeVisible()
  await shot(owner, "invite-unverified")

  const superadmin = await signInSuperadmin()
  await visit(superadmin, "/superadmin/companies")
  await shot(superadmin, "companies")
  await superadmin.getByRole("textbox", { name: "Company name" }).fill(name)
  await superadmin.getByRole("button", { name: "Find" }).click()
  const row = superadmin.getByRole("listitem").filter({ hasText: name })
  await expect(row).toHaveCount(1)
  await shot(superadmin, "companies-found")

  await row.getByRole("button", { name: "Suspend" }).click()
  await shot(superadmin, "suspend-confirm")
  await superadmin.getByRole("dialog").getByRole("button", { name: "Suspend" }).click()
  await expect(row.getByText("Suspended", { exact: true })).toBeVisible()
  await shot(superadmin, "suspended")

  // The members see why nothing changes; the candidate who hasn't started, no interview.
  await visit(owner, `/companies/${company.id}/interviews`)
  await expect(owner.getByText(/This company is suspended/)).toBeVisible()
  await shot(owner, "members-notice")
  await owner.setViewportSize({ width: 390, height: 844 })
  await shot(owner, "members-notice-phone")
  await owner.setViewportSize({ width: 1280, height: 800 })
  await visit(owner, invitePath)
  await shot(owner, "invite-suspended")

  await row.getByRole("button", { name: "Lift suspension" }).click()
  await expect(row.getByText("Suspended", { exact: true })).toHaveCount(0)

  await row.getByRole("button", { name: `Rename ${name}` }).click()
  await shot(superadmin, "rename")
  await superadmin.getByRole("dialog").getByRole("textbox").fill(`${name} renamed`)
  await superadmin.getByRole("dialog").getByRole("button", { name: "Save" }).click()
  const renamed = superadmin.getByRole("listitem").filter({ hasText: `${name} renamed` })
  await expect(renamed).toHaveCount(1)

  await renamed.getByRole("button", { name: `Delete ${name} renamed` }).click()
  await shot(superadmin, "delete-confirm")
  await superadmin.getByRole("dialog").getByRole("button", { name: "Delete company" }).click()
  await expect(renamed).toHaveCount(0)
})
