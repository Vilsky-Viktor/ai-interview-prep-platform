import { expect, test } from "../fixtures"
import { api, createCompany } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail } from "../helpers/users"

test("an owner stops AI apps from using the company's data, and allows them again", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)

  await visit(owner, `/companies/${company.id}/integrations/ai`)
  const allow = owner.getByRole("switch")
  await expect(allow).toBeChecked()
  await shot(owner, "allowed")

  await allow.click()
  await expect(allow).not.toBeChecked()
  await expect
    .poll(async () => (await api<{ ai_apps_allowed: boolean }>(owner, "GET", `/companies/companies/${company.id}`)).ai_apps_allowed)
    .toBe(false)
  await shot(owner, "stopped")

  // Kept after a reload.
  await owner.reload()
  await expect(allow).not.toBeChecked()
  await allow.click()
  await expect(allow).toBeChecked()
})
