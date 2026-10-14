import { expect, test } from "../fixtures"
import { createCompany } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail } from "../helpers/users"

test("a balance says it's the current balance on hover", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)

  // In the company's header.
  await visit(owner, `/companies/${company.id}/interviews`)
  await owner.locator("span.tabular-nums").first().hover()
  await expect(owner.getByText("Current balance: 900", { exact: true })).toBeVisible()
  await shot(owner, "header")

  // On the billing page.
  await visit(owner, `/companies/${company.id}/billing`)
  await owner.locator("span.font-heading.tabular-nums").first().hover()
  await expect(owner.getByText("Current balance: 900", { exact: true })).toBeVisible()
  await shot(owner, "billing")
})
