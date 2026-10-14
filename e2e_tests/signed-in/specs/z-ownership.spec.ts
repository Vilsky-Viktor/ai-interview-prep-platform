import type { Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { api, createCompany } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

type Member = { id: string; email: string; token: string | null }

async function openDeleteAccount(page: Page) {
  await visit(page, "/settings")
  await page.getByRole("button", { name: "Delete account" }).click()

  return page.getByRole("dialog")
}

// The owner hands the company to an admin who joined: the admin becomes its owner (told in the
// bell), the owner an admin. Deleting an account waits while it owns a company others joined,
// and names the companies (with their credits) deleted with it.
test("the owner makes an admin the owner, and an account owning a shared company waits", async ({
  signInAs,
}) => {
  const annEmail = throwawayEmail("owner-ann")
  const bobEmail = throwawayEmail("owner-bob")
  const ann = await signInAs(annEmail)
  const company = await createCompany(ann)
  const own = await createCompany(ann)
  const path = `/companies/members?company_id=${company.id}`
  await api(ann, "POST", path, { email: bobEmail, role: "admin" })
  const [invited] = (await api<Member[]>(ann, "GET", path)).filter(
    (member) => member.email === bobEmail,
  )

  const bob = await signInAs(bobEmail)
  await api(bob, "POST", `/companies/members/invites/${invited.token}/accept`)

  await visit(ann, `/companies/${company.id}/members`)
  const row = ann.getByRole("listitem").filter({ hasText: bobEmail })
  await row.getByRole("button", { name: "Role" }).click()
  const menu = ann.getByRole("menu")
  await expect(
    menu.getByText("Manages the team, can delete the company and hand it on."),
  ).toBeVisible()
  await shot(ann, "owner-choice")
  await menu.getByRole("menuitemradio", { name: /^owner/ }).click()
  const dialog = ann.getByRole("dialog")
  await expect(dialog.getByText(`Make ${bobEmail} the owner?`)).toBeVisible()
  await shot(ann, "make-owner")
  await dialog.getByRole("button", { name: "Make owner" }).click()
  await expect(ann.getByText(`${bobEmail} is now the owner.`)).toBeVisible()
  await shot(ann, "made-owner")

  // Bob hears it in the bell.
  await visit(bob, "/companies")
  await expect(async () => {
    await bob.reload()
    await bob.getByRole("button", { name: /notification/i }).click()
    await expect(
      bob.getByText(`You're now the owner of “${company.name}”.`),
    ).toBeVisible({ timeout: 3000 })
  }).toPass({ timeout: 60_000 })
  await shot(bob, "bell-owner")

  // Bob owns a company Ann is in: his account waits.
  const bobDialog = await openDeleteAccount(bob)
  await expect(bobDialog.getByText(company.name)).toBeVisible()
  await expect(bobDialog.getByRole("button", { name: "Delete account" })).toBeDisabled()
  await shot(bob, "delete-blocked")

  // Ann owns one company alone: it's named, with its credits, and goes with her account.
  const annDialog = await openDeleteAccount(ann)
  await expect(annDialog.getByText("These companies are deleted with your account:")).toBeVisible()
  await expect(annDialog.getByText(own.name)).toBeVisible()
  await expect(annDialog.getByRole("button", { name: "Delete account" })).toBeEnabled()
  await shot(ann, "delete-named")
})
