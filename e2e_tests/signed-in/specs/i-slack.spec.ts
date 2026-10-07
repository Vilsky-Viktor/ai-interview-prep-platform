import { expect, test } from "../fixtures"
import { createCompany } from "../helpers/api"
import { addSlackConnection } from "../helpers/db"
import { openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// Slack sits first on the integrations tab, with its Instructions and "Add to Slack". A real
// connection needs a Slack workspace, so it is saved straight into the database; picking which
// notifications go to the channel and disconnecting then go through the API for real.
test("an owner adds Slack, picks its notifications and disconnects it", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("slack"))
  const company = await createCompany(owner)
  const tab = `/companies/${company.id}/integrations`

  await visit(owner, tab)
  await expect(owner.getByRole("heading", { name: "Messaging" })).toBeVisible()
  const row = owner.getByRole("listitem").filter({ hasText: "Slack" })
  await expect(row.getByRole("link", { name: /^Slack/ })).toHaveAttribute("href", `${tab}/slack`)
  await expect(row.getByRole("button", { name: "Add to Slack" })).toBeVisible()
  await owner.setViewportSize({ width: 1280, height: 1100 })
  await shot(owner, "list")

  // How it works, before going to Slack.
  await openDialog(owner, row.getByRole("button", { name: "Instructions" }))
  const steps = owner.getByRole("dialog").getByRole("listitem")
  await expect(steps).toHaveCount(4)
  await expect(steps.last()).toContainText("It can't read your Slack")
  await owner.keyboard.press("Escape")

  await visit(owner, `${tab}/slack`)
  await expect(owner.getByText("Slack isn't connected yet.", { exact: false })).toBeVisible()
  await shot(owner, "not-connected")

  // Back from Slack: the channel, and the notifications it gets, saved as they change.
  await addSlackConnection(company.id)
  await visit(owner, `${tab}/slack?slack=connected`)
  await expect(owner.getByText("Slack is connected.")).toBeVisible()
  await expect(owner).toHaveURL(new RegExp(`${tab}/slack$`))
  await expect(owner.getByText("E2E Acme · #hiring")).toBeVisible()
  const ready = owner.getByRole("checkbox", { name: "An interview is ready" })
  await expect(ready).not.toBeChecked()
  await ready.click()
  await expect(ready).toBeChecked()
  await shot(owner, "connected")
  await owner.reload()
  await expect(owner.getByRole("checkbox", { name: "An interview is ready" })).toBeChecked()

  // Disconnecting asks first, then the page is back to "isn't connected".
  await openDialog(owner, owner.getByRole("button", { name: "Disconnect" }))
  await owner.getByRole("dialog").getByRole("button", { name: "Disconnect" }).click()
  await expect(owner.getByText("Slack isn't connected yet.", { exact: false })).toBeVisible()
  await expect(owner.getByRole("button", { name: "Add to Slack" })).toBeVisible()
})
