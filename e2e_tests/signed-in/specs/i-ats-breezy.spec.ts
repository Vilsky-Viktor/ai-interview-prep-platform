import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection } from "../helpers/db"
import { openDialog, visit } from "../helpers/navigation"
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
  await expect(owner.getByRole("link", { name: /^Breezy HR/ })).toHaveAttribute(
    "href",
    `${tab}/breezy`
  )
  await owner.setViewportSize({ width: 1280, height: 900 })
  await shot(owner, "list")
  await visit(owner, `${tab}/breezy`)
  await expect(owner.getByText("Breezy HR isn't connected yet.", { exact: false })).toBeVisible()

  // Where to make the key; Connect needs it.
  await openDialog(owner, owner.getByRole("button", { name: "Connect" }))
  const connect = owner.getByRole("dialog")
  await expect(connect.getByText("API Keys")).toBeVisible()
  await expect(connect.getByText("We add the web hook in Breezy HR ourselves.")).toBeVisible()
  await expect(connect.getByRole("button", { name: "Connect" })).toBeDisabled()
  await connect.getByLabel("API key").fill("e2e")
  await shot(owner, "connect")
  await owner.route("**/api/ats/breezy?*", async (route) => {
    if (route.request().method() !== "PUT") {
      return route.fallback()
    }

    await addAtsConnection(company.id, interviewId, { invited: 1 }, "breezy")
    await route.fulfill({ status: 204 })
  })
  await connect.getByRole("button", { name: "Connect" }).click()

  // Connected, without a dialog to follow: the page lists the linked jobs.
  await expect(owner.getByText("connected", { exact: true })).toBeVisible({ timeout: 60_000 })
  await expect(owner.getByRole("dialog")).toHaveCount(0)
  await expect(owner.getByText("E2E Backend developer")).toBeVisible()
  await shot(owner, "page")

  // Its Instructions are the candidate flow alone.
  await openDialog(owner, owner.getByRole("button", { name: "Instructions" }))
  await expect(owner.getByRole("dialog").getByRole("listitem")).toHaveCount(6)
  await expect(owner.getByText("Set up the web hook")).toHaveCount(0)
})
