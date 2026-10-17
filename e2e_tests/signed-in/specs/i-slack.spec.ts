import { expect, test } from "../fixtures"
import { createCompany } from "../helpers/api"
import { addSlackConnection } from "../helpers/db-integrations"
import { integrationRow, openDialog, visit } from "../helpers/navigation"
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
  // Not connected: Instructions and Add to Slack.
  const row = integrationRow(owner, "/slack")
  await expect(row.getByTestId("integration-actions").getByRole("button")).toHaveCount(2)
  await owner.setViewportSize({ width: 1280, height: 1100 })
  await shot(owner, "list")

  // How it works, before going to Slack.
  await openDialog(owner, row.getByTestId("instructions"))
  await expect(owner.getByRole("dialog").getByRole("listitem")).toHaveCount(4)
  await owner.keyboard.press("Escape")

  // Its page, not connected: no notifications to pick yet.
  await visit(owner, `${tab}/slack`)
  const main = owner.getByRole("main")
  const actions = main.getByTestId("integration-actions").getByRole("button")
  const kinds = main.getByRole("checkbox")
  await expect(actions).toHaveCount(2)
  await expect(kinds).toHaveCount(0)
  await shot(owner, "not-connected")

  // Back from Slack: a success note, the channel, and the notifications it gets (the four the
  // connection was saved with), saved as they change.
  await addSlackConnection(company.id)
  await visit(owner, `${tab}/slack?slack=connected`)
  await expect(owner.locator('[data-sonner-toast][data-type="success"]')).toBeVisible()
  await expect(owner).toHaveURL(new RegExp(`${tab}/slack$`))
  // The workspace and the channel, side by side with a dot between them.
  const channel = main.getByText(/^E2E Acme\W+#hiring$/)
  await expect(channel).toBeVisible()
  await expect(main.locator('[role=checkbox][aria-checked="true"]')).toHaveCount(4)
  const states = await kinds.evaluateAll((boxes) =>
    boxes.map((box) => box.getAttribute("aria-checked"))
  )
  const off = states.indexOf("false")
  const kind = kinds.nth(off)
  await kind.click()
  await expect(kind).toBeChecked()
  await shot(owner, "connected")
  await owner.reload()
  await expect(kinds.nth(off)).toBeChecked()
  await expect(main.locator('[role=checkbox][aria-checked="true"]')).toHaveCount(5)

  // Disconnecting (beside Instructions) asks first, then the page is back to not connected.
  await expect(actions).toHaveCount(2)
  await openDialog(owner, actions.last())
  await owner.getByRole("dialog").getByRole("button").last().click()
  await expect(kinds).toHaveCount(0)
  await expect(actions).toHaveCount(2)
  await expect(channel).toHaveCount(0)
})
