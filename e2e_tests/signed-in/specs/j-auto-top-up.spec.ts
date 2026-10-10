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
  // Off, it's a button that says what it does.
  await openDialog(owner, owner.getByRole("button", { name: "Set up automatic top-up" }))
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

// On, it's the setting as text, with the edit icon that changes it.
test("an automatic top-up that's on shows its setting and changes from the edit icon", async ({
  signInAs,
}) => {
  const owner = await signInAs(throwawayEmail("auto-top-up-on"))
  await createCompany(owner)
  await owner.route("**/api/companies/companies/*/auto-top-up", (route) =>
    route.fulfill({
      json: {
        offered: true,
        on: true,
        waiting: false,
        product: "topup_30",
        threshold: 500,
        products: ["topup_30", "topup_150"],
        thresholds: [500, 2000],
      },
    })
  )

  await visit(owner, "/top-up")
  await expect(owner.getByText("Automatic top-up: $30 under 500 credits")).toBeVisible()
  await expect(owner.getByRole("button", { name: "Set up automatic top-up" })).toHaveCount(0)
  await openDialog(owner, owner.getByRole("button", { name: "Change automatic top-up" }))
  await expect(owner.getByRole("dialog").getByText("When the balance falls")).toBeVisible()
})
