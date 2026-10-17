import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection } from "../helpers/db-integrations"
import { integrationRow, openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// Teamtailor sits beside Workable and Greenhouse on the ATS tab. A real connection needs a
// Teamtailor account, so Connect is answered in the browser while the connection is saved straight
// into the database; its info dialog then opens with the web hook to set up, where the signature
// key Teamtailor makes is pasted and saved for real.
test("an owner connects Teamtailor and saves its web hook's signature key", async ({
  signInAs,
}) => {
  const owner = await signInAs(throwawayEmail("ats-tt"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const tab = `/companies/${company.id}/integrations`

  await visit(owner, tab)
  await expect(integrationRow(owner, "/teamtailor")).toBeVisible()
  await shot(owner, "list")
  await visit(owner, `${tab}/teamtailor`)
  const main = owner.getByRole("main")
  const actions = main.getByTestId("integration-actions").getByRole("button")

  // One key; Connect needs it.
  await openDialog(owner, actions.last())
  const connect = owner.getByRole("dialog")
  const submit = connect.locator("button[type=submit]")
  await expect(connect.locator("form input")).toHaveCount(1)
  await expect(submit).toBeDisabled()
  await connect.locator("form input").fill("e2e")
  await shot(owner, "connect")
  await owner.route("**/api/ats/teamtailor?*", async (route) => {
    if (route.request().method() !== "PUT") {
      return route.fallback()
    }

    await addAtsConnection(company.id, interviewId, { invited: 1 }, "teamtailor")
    await route.fulfill({ status: 204 })
  })
  await submit.click()

  // Connected: the info dialog opens by itself with the web hook, our address, and a field for
  // Teamtailor's signature key, saved once it changes.
  const webhook = owner.getByRole("dialog").locator("section")
  // The web hook shows once the page has reloaded the connection (slow on the dev server).
  await expect(webhook).toBeVisible({ timeout: 60_000 })
  // The address first, then the field for the secret.
  await expect(webhook.getByRole("textbox").first()).toHaveValue(
    /\/api\/ats\/webhooks\/teamtailor\/[0-9a-f-]{36}$/
  )
  const key = webhook.locator('input[type="password"]')
  const save = webhook.locator("form:has(input[type=password]) button[type=submit]")
  await expect(key).toHaveValue("")
  await expect(save).toBeDisabled()
  await key.fill("e2e-signature-key")
  await save.click()
  await expect(owner.locator('[data-sonner-toast][data-type="success"]')).toBeVisible()
  await expect(save).toBeDisabled()
  await owner.setViewportSize({ width: 1280, height: 1500 })
  await shot(owner, "info")
  await owner.keyboard.press("Escape")

  // Saved for good: the dialog shows it again after a reload.
  await visit(owner, `${tab}/teamtailor`)
  await expect(main.locator("[data-slot=badge]").filter({ visible: true })).toBeVisible()
  await expect(main.getByRole("listitem").filter({ hasText: "E2E Backend developer" })).toBeVisible()
  await openDialog(owner, main.getByTestId("instructions"))
  await expect(
    owner.getByRole("dialog").locator('section input[type="password"]')
  ).toHaveValue("e2e-signature-key")
})
