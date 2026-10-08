import { expect, test } from "../fixtures"
import { createCompany } from "../helpers/api"
import { openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// The automatic top-up's amount and level are picked from the site's menu, not the browser's.
// It is offered only where Paddle is set up, so its setting is answered here as if it were.
test("an owner picks the automatic top-up's amount and level", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("auto-top-up"))
  await createCompany(owner)
  await owner.route("**/api/companies/companies/*/auto-top-up", (route) =>
    route.fulfill({
      json: {
        offered: true,
        on: false,
        waiting: false,
        product: null,
        threshold: null,
        products: ["topup_30", "topup_150"],
        thresholds: [500, 2000],
      },
    })
  )

  await visit(owner, "/top-up")
  await openDialog(owner, owner.getByRole("button", { name: "Automatic top-up: off" }))
  const dialog = owner.getByRole("dialog")
  await expect(dialog.getByText("Top up", { exact: true })).toBeVisible()
  await expect(dialog.getByText("When the balance falls")).toBeVisible()
  await expect(owner.locator("select")).toHaveCount(0)
  await shot(owner, "dialog")

  for (const name of ["Top up", "When the balance falls"]) {
    const pill = dialog.getByRole("button", { name, exact: true })
    await pill.click()
    const items = owner.getByRole("menu").getByRole("menuitemradio")
    await expect(items.nth(1)).toBeVisible()
    await shot(owner, `menu-${name === "Top up" ? "amount" : "level"}`)
    const picked = (await items.last().textContent()) ?? ""
    await items.last().click()
    await expect(owner.getByRole("menu")).toHaveCount(0)
    await expect(pill).toHaveText(picked)
  }
})
