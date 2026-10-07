import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection } from "../helpers/db"
import { openDialog, visit } from "../helpers/navigation"
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
  await expect(owner.getByRole("link", { name: /^Teamtailor/ })).toHaveAttribute(
    "href",
    `${tab}/teamtailor`
  )
  await shot(owner, "list")
  await visit(owner, `${tab}/teamtailor`)

  // Where to make the key and what it needs; Connect needs the key.
  await openDialog(owner, owner.getByRole("button", { name: "Connect" }))
  const connect = owner.getByRole("dialog")
  await expect(connect.getByText("API keys")).toBeVisible()
  await expect(connect.getByText("Read/Write")).toBeVisible()
  await expect(connect.getByRole("button", { name: "Connect" })).toBeDisabled()
  await connect.getByLabel("API key").fill("e2e")
  await shot(owner, "connect")
  await owner.route("**/api/ats/teamtailor?*", async (route) => {
    if (route.request().method() !== "PUT") {
      return route.fallback()
    }

    await addAtsConnection(company.id, interviewId, { invited: 1 }, "teamtailor")
    await route.fulfill({ status: 204 })
  })
  await connect.getByRole("button", { name: "Connect" }).click()

  // Connected: the info dialog opens by itself with the web hook, the add-on it needs, our
  // address, and a field for Teamtailor's signature key, saved once it changes.
  const dialog = owner.getByRole("dialog")
  await expect(dialog.getByText("Add-on feature center", { exact: false })).toBeVisible()
  await expect(dialog.getByText("job_application.update")).toBeVisible()
  await expect(dialog.getByRole("textbox", { name: "Copy URL" })).toHaveValue(
    /\/api\/ats\/webhooks\/teamtailor\/[0-9a-f-]{36}$/
  )
  const key = dialog.getByLabel("Signature key")
  const save = dialog.getByRole("button", { name: "Save key" })
  await expect(key).toHaveValue("")
  await expect(save).toBeDisabled()
  await key.fill("e2e-signature-key")
  await save.click()
  await expect(owner.getByText("Key saved")).toBeVisible()
  await expect(save).toBeDisabled()
  await owner.setViewportSize({ width: 1280, height: 1500 })
  await shot(owner, "info")
  await owner.keyboard.press("Escape")

  // Saved for good: the dialog shows it again after a reload.
  await visit(owner, `${tab}/teamtailor`)
  await expect(owner.getByText("connected", { exact: true })).toBeVisible()
  await expect(owner.getByText("E2E Backend developer")).toBeVisible()
  await openDialog(
    owner,
    owner.getByRole("button", { name: "Instructions" })
  )
  await expect(owner.getByRole("dialog").getByLabel("Signature key")).toHaveValue(
    "e2e-signature-key"
  )
})
