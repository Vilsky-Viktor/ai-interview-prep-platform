import { expect, test } from "../fixtures"
import { api, createCompany, createInterview } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { throwawayEmail } from "../helpers/users"

test.setTimeout(240_000)

// Deleting an interview past the first page (20) takes it off the list at once, and the
// list goes on loading from the right place.
test("an interview deleted past the first page leaves the list at once", async ({
  signInAs,
}) => {
  const owner = await signInAs(throwawayEmail("long-list"))
  const company = await createCompany(owner)

  // Oldest first, so "E2E 01" is last in the list, on its second page.
  for (let index = 1; index <= 22; index += 1) {
    const id = await createInterview(owner, company.id)
    const title = `E2E ${String(index).padStart(2, "0")}`
    await api(owner, "PATCH", `/companies/interviews/${id}/title`, { title })
  }

  await visit(owner, `/companies/${company.id}/interviews`)
  await expect(owner.getByText("E2E 22")).toBeVisible()
  const oldest = owner.getByRole("button", { name: "Delete E2E 01" })
  await expect(async () => {
    await owner.mouse.wheel(0, 4000)
    await expect(oldest).toBeVisible({ timeout: 1000 })
  }).toPass({ timeout: 30_000 })

  await oldest.click()
  await owner.getByRole("dialog").getByRole("button", { name: "Delete" }).click()
  await expect(owner.getByRole("dialog")).toHaveCount(0)
  await expect(owner.getByText("E2E 01", { exact: true })).toHaveCount(0)
  await expect(owner.getByText("E2E 02", { exact: true })).toBeVisible()
})
