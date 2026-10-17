import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection } from "../helpers/db-integrations"
import { integrationRow, openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// Recruitee sits beside the other ATSs on the ATS tab; its page has no linked jobs yet. A
// real connection needs a Recruitee account, so Connect is answered in the browser while the
// connection is saved straight into the database; its Instructions then open with the web hook to
// set up, where the secret Recruitee shows is pasted and saved for real.
test("an owner connects Recruitee and saves its web hook's secret", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("ats-rc"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const tab = `/companies/${company.id}/integrations`

  await visit(owner, tab)
  await expect(integrationRow(owner, "/recruitee")).toBeVisible()
  await shot(owner, "list")

  // Not connected yet: no tag and no linked jobs; Instructions and Connect.
  await visit(owner, `${tab}/recruitee`)
  const main = owner.getByRole("main")
  const actions = main.getByTestId("integration-actions").getByRole("button")
  await expect(main.locator("[data-slot=badge]")).toHaveCount(0)
  await expect(main.getByRole("listitem")).toHaveCount(0)
  await expect(owner.getByTestId("link-job")).toHaveCount(0)
  await expect(actions).toHaveCount(2)
  await shot(owner, "not-connected")

  // Connect needs the address and the token.
  await openDialog(owner, actions.last())
  const connect = owner.getByRole("dialog")
  const fields = connect.locator("form input")
  const submit = connect.locator("button[type=submit]")
  await expect(fields).toHaveCount(2)
  await expect(submit).toBeDisabled()
  await fields.first().fill("acme.recruitee.com")
  await fields.last().fill("e2e")
  await shot(owner, "connect")
  await owner.route("**/api/ats/recruitee?*", async (route) => {
    if (route.request().method() !== "PUT") {
      return route.fallback()
    }

    await addAtsConnection(company.id, interviewId, { invited: 1 }, "recruitee")
    await route.fulfill({ status: 204 })
  })
  await submit.click()

  // Connected: the Instructions open by themselves with the web hook, our address, and a field
  // for the secret Recruitee shows, saved once it changes.
  const webhook = owner.getByRole("dialog").locator("section")
  // The web hook shows once the page has reloaded the connection (slow on the dev server).
  await expect(webhook).toBeVisible({ timeout: 60_000 })
  // The address first, then the field for the secret.
  await expect(webhook.getByRole("textbox").first()).toHaveValue(
    /\/api\/ats\/webhooks\/recruitee\/[0-9a-f-]{36}$/
  )
  const secret = webhook.locator('input[type="password"]')
  const save = webhook.locator("form:has(input[type=password]) button[type=submit]")
  await expect(secret).toHaveValue("")
  await secret.fill("e2e-recruitee-secret")
  await save.click()
  await expect(owner.locator('[data-sonner-toast][data-type="success"]')).toBeVisible()
  await expect(save).toBeDisabled()
  await owner.setViewportSize({ width: 1280, height: 1400 })
  await shot(owner, "info")
  await owner.keyboard.press("Escape")

  // Connected, the page has the tag and lists its linked jobs.
  await expect(main.locator("[data-slot=badge]").filter({ visible: true })).toBeVisible()
  await expect(main.getByRole("listitem").filter({ hasText: "E2E Backend developer" })).toBeVisible()
})
