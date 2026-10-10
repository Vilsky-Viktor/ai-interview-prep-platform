import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection } from "../helpers/db"
import { openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// Recruitee sits beside the other ATSs on the ATS tab; its page says it isn't connected yet. A
// real connection needs a Recruitee account, so Connect is answered in the browser while the
// connection is saved straight into the database; its Instructions then open with the web hook to
// set up, where the secret Recruitee shows is pasted and saved for real.
test("an owner connects Recruitee and saves its web hook's secret", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("ats-rc"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const tab = `/companies/${company.id}/integrations`

  await visit(owner, tab)
  await expect(owner.getByRole("link", { name: /^Recruitee/ })).toHaveAttribute(
    "href",
    `${tab}/recruitee`
  )
  await shot(owner, "list")

  // Not connected yet: the page says so instead of linked jobs.
  await visit(owner, `${tab}/recruitee`)
  await expect(owner.getByText("Recruitee isn't connected yet.", { exact: false })).toBeVisible()
  await expect(owner.getByRole("heading", { name: "Linked jobs" })).toHaveCount(0)
  await shot(owner, "not-connected")

  // Where to make the token; Connect needs the address and the token.
  await openDialog(owner, owner.getByRole("button", { name: "Connect" }))
  const connect = owner.getByRole("dialog")
  await expect(connect.getByText("Personal API tokens")).toBeVisible()
  await expect(connect.getByRole("button", { name: "Connect" })).toBeDisabled()
  await connect.getByLabel("Recruitee address").fill("acme.recruitee.com")
  await connect.getByLabel("API token").fill("e2e")
  await shot(owner, "connect")
  await owner.route("**/api/ats/recruitee?*", async (route) => {
    if (route.request().method() !== "PUT") {
      return route.fallback()
    }

    await addAtsConnection(company.id, interviewId, { invited: 1 }, "recruitee")
    await route.fulfill({ status: 204 })
  })
  await connect.getByRole("button", { name: "Connect" }).click()

  // Connected: the Instructions open by themselves with the web hook, our address, and a field
  // for the secret Recruitee shows, saved once it changes.
  const dialog = owner.getByRole("dialog")
  // The web hook shows once the page has reloaded the connection (slow on the dev server).
  await expect(dialog.getByText("candidate_moved")).toBeVisible({ timeout: 60_000 })
  await expect(dialog.getByRole("textbox", { name: "Copy URL" })).toHaveValue(
    /\/api\/ats\/webhooks\/recruitee\/[0-9a-f-]{36}$/
  )
  const secret = dialog.getByLabel("Secret")
  const save = dialog.getByRole("button", { name: "Save key" })
  await expect(secret).toHaveValue("")
  await secret.fill("e2e-recruitee-secret")
  await save.click()
  await expect(owner.getByText("Key saved")).toBeVisible()
  await expect(save).toBeDisabled()
  await owner.setViewportSize({ width: 1280, height: 1400 })
  await shot(owner, "info")
  await owner.keyboard.press("Escape")

  // Connected, the page lists its linked jobs instead.
  await expect(owner.getByText("connected", { exact: true }).filter({ visible: true })).toBeVisible()
  await expect(owner.getByText("E2E Backend developer")).toBeVisible()
  await expect(owner.getByText("isn't connected yet", { exact: false })).toHaveCount(0)
})
