import { expect, test } from "../fixtures"
import { GREENHOUSE_E2E_SECRET } from "../constants"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection } from "../helpers/db-integrations"
import { integrationRow, openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// Greenhouse sits beside Workable on the ATS tab and has its own page. A real connection needs a
// Greenhouse account, so Connect is answered in the browser while the connection is saved
// straight into the database; its info dialog then opens with the web hook to set up.
test("an owner connects Greenhouse and finds its web hook in the info dialog", async ({
  signInAs,
}) => {
  const owner = await signInAs(throwawayEmail("ats-gh"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const tab = `/companies/${company.id}/integrations`

  await visit(owner, tab)
  await expect(integrationRow(owner, "/workable")).toBeVisible()
  await shot(owner, "list")
  await expect(integrationRow(owner, "/greenhouse")).toBeVisible()
  await visit(owner, `${tab}/greenhouse`)
  const main = owner.getByRole("main")
  const actions = main.getByTestId("integration-actions").getByRole("button")

  // Not connected: the info dialog has no web hook yet.
  await openDialog(owner, main.getByTestId("instructions"))
  await expect(owner.getByRole("dialog").getByRole("listitem")).toHaveCount(6)
  await expect(owner.getByRole("dialog").locator("section")).toHaveCount(0)
  await owner.keyboard.press("Escape")

  // The API credential; Connect needs both fields, its client ID and secret.
  await actions.last().click()
  const connect = owner.getByRole("dialog")
  const fields = connect.locator("form input")
  const submit = connect.locator("button[type=submit]")
  await expect(fields).toHaveCount(2)
  await expect(submit).toBeDisabled()
  await fields.first().fill("e2e")
  await expect(submit).toBeDisabled()
  await fields.last().fill("e2e")
  await shot(owner, "connect")
  await owner.route("**/api/ats/greenhouse?*", async (route) => {
    if (route.request().method() !== "PUT") {
      return route.fallback()
    }

    await addAtsConnection(company.id, interviewId, { invited: 2 }, "greenhouse")
    await route.fulfill({ status: 204 })
  })
  await submit.click()

  // Connected: the info dialog opens by itself with the web hook's address and secret key, each
  // in a field to copy.
  const webhook = owner.getByRole("dialog").locator("section")
  // The web hook shows once the page has reloaded the connection (slow on the dev server).
  await expect(webhook).toBeVisible({ timeout: 60_000 })
  await expect(webhook.getByRole("textbox").first()).toHaveValue(
    /\/api\/ats\/webhooks\/greenhouse\/[0-9a-f-]{36}$/
  )
  await expect(webhook.getByRole("textbox").last()).toHaveValue(GREENHOUSE_E2E_SECRET)
  await owner.setViewportSize({ width: 1280, height: 1400 })
  await shot(owner, "info")
  await owner.keyboard.press("Escape")

  // The page: the tag, Instructions and Disconnect (no other setup button), and the linked job
  // with its two invited.
  await expect(main.locator("[data-slot=badge]").filter({ visible: true })).toBeVisible()
  await expect(actions).toHaveCount(2)
  const job = main.getByRole("listitem").filter({ hasText: "E2E Backend developer" })
  await expect(job.getByTestId("invited-count")).toHaveText("2")
  await shot(owner, "page")

  // Greenhouse names no account: under the title is the company's own name, on the page and the
  // tab's row.
  const header = owner.getByRole("heading", { level: 1 }).locator("xpath=../..")
  await expect(header.getByText(company.name, { exact: true })).toBeVisible()
  await visit(owner, tab)
  await expect(
    integrationRow(owner, "/greenhouse").getByText(company.name, { exact: true })
  ).toBeVisible()
  await shot(owner, "company-name")
})
