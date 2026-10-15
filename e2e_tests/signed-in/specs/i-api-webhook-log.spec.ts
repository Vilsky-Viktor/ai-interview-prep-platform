import { expect, test } from "../fixtures"
import { api, createCompany } from "../helpers/api"
import { openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail } from "../helpers/users"

// An owner sends a web hook a signed test event and reads how it went in its delivery log.
test("an owner tests a web hook and reads its delivery log", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  // A public address that doesn't take events: the log says what it answered.
  await api(owner, "POST", `/v1/manage/webhooks?company_id=${company.id}`, {
    url: "https://example.com/prepza-webhook",
  })

  await visit(owner, `/companies/${company.id}/integrations/api?tab=webhooks`)
  await shot(owner, "webhooks")
  await owner.getByRole("button", { name: "Send test event" }).click()
  await expect(
    owner.getByText(/didn't take the test event|test event was delivered/)
  ).toBeVisible({ timeout: 30_000 })
  await shot(owner, "tested")

  await openDialog(owner, owner.getByRole("button", { name: "Delivery log" }))
  const log = owner.getByRole("dialog")
  await expect(log.getByText("test", { exact: true })).toBeVisible()
  await shot(owner, "log")
})
