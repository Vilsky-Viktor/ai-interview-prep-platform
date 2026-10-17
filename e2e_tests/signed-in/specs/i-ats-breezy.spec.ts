import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection } from "../helpers/db-integrations"
import { integrationRow, openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// Breezy HR connects with one key: prepza adds the web hook in Breezy itself, so its Instructions
// have no web hook to set up. A real connection needs a Breezy account (and its web hooks an HTTPS
// address), so Connect is answered in the browser while the connection is saved straight into the
// database.
test("an owner connects Breezy HR with one key", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("ats-bz"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const tab = `/companies/${company.id}/integrations`

  await visit(owner, tab)
  await expect(integrationRow(owner, "/breezy")).toBeVisible()
  await owner.setViewportSize({ width: 1280, height: 900 })
  await shot(owner, "list")
  await visit(owner, `${tab}/breezy`)
  // Not connected yet: no tag and no linked jobs; Instructions and Connect.
  const main = owner.getByRole("main")
  const actions = main.getByTestId("integration-actions").getByRole("button")
  await expect(main.locator("[data-slot=badge]")).toHaveCount(0)
  await expect(main.getByRole("listitem")).toHaveCount(0)
  await expect(actions).toHaveCount(2)

  // One key; Connect needs it.
  await openDialog(owner, actions.last())
  const connect = owner.getByRole("dialog")
  const submit = connect.locator("button[type=submit]")
  await expect(connect.locator("form input")).toHaveCount(1)
  await expect(submit).toBeDisabled()
  await connect.locator("form input").fill("e2e")
  await shot(owner, "connect")
  await owner.route("**/api/ats/breezy?*", async (route) => {
    if (route.request().method() !== "PUT") {
      return route.fallback()
    }

    await addAtsConnection(company.id, interviewId, { invited: 1 }, "breezy")
    await route.fulfill({ status: 204 })
  })
  await submit.click()

  // Connected, without a dialog to follow: the tag, and the page lists the linked jobs.
  await expect(main.locator("[data-slot=badge]").filter({ visible: true })).toBeVisible({ timeout: 60_000 })
  await expect(owner.getByRole("dialog")).toHaveCount(0)
  await expect(owner.getByText("E2E Backend developer")).toBeVisible()
  await shot(owner, "page")

  // Its Instructions are the candidate flow alone: no web hook to set up.
  await openDialog(owner, main.getByTestId("instructions"))
  await expect(owner.getByRole("dialog").getByRole("listitem")).toHaveCount(6)
  await expect(owner.getByRole("dialog").locator("section")).toHaveCount(0)
})
