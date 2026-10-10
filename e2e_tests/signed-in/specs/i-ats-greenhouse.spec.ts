import { expect, test } from "../fixtures"
import { GREENHOUSE_E2E_SECRET } from "../constants"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection, nameAtsConnectionMaker } from "../helpers/db"
import { openDialog, visit } from "../helpers/navigation"
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
  await expect(owner.getByRole("link", { name: /^Workable/ })).toBeVisible()
  await shot(owner, "list")
  await expect(owner.getByRole("link", { name: /^Greenhouse/ })).toHaveAttribute(
    "href",
    `${tab}/greenhouse`
  )
  await visit(owner, `${tab}/greenhouse`)

  // Not connected: the info dialog has no web hook yet.
  await openDialog(
    owner,
    owner.getByRole("button", { name: "Instructions" })
  )
  await expect(owner.getByRole("dialog").getByRole("listitem")).toHaveCount(6)
  await expect(owner.getByText("Set up the web hook")).toHaveCount(0)
  await owner.keyboard.press("Escape")

  // Where to make the API credential; Connect needs both fields.
  await owner.getByRole("button", { name: "Connect" }).click()
  const connect = owner.getByRole("dialog")
  await expect(connect.getByText("Harvest V3 (OAuth)")).toBeVisible()
  await expect(connect.getByRole("button", { name: "Connect" })).toBeDisabled()
  await connect.getByRole("textbox", { name: "Client ID" }).fill("e2e")
  await connect.getByLabel("Client secret").fill("e2e")
  await shot(owner, "connect")
  await owner.route("**/api/ats/greenhouse?*", async (route) => {
    if (route.request().method() !== "PUT") {
      return route.fallback()
    }

    await addAtsConnection(company.id, interviewId, { invited: 2 }, "greenhouse")
    await route.fulfill({ status: 204 })
  })
  await connect.getByRole("button", { name: "Connect" }).click()

  // Connected: the info dialog opens by itself with the web hook's address and secret key.
  const dialog = owner.getByRole("dialog")
  // The web hook shows once the page has reloaded the connection (slow on the dev server).
  await expect(dialog.getByText("Set up the web hook")).toBeVisible({ timeout: 60_000 })
  await expect(dialog.getByText("Candidate or Prospect Stage Change")).toBeVisible()
  await expect(dialog.getByRole("textbox", { name: "Copy URL" })).toHaveValue(
    /\/api\/ats\/webhooks\/greenhouse\/[0-9a-f-]{36}$/
  )
  await expect(dialog.getByRole("textbox", { name: "Copy secret" })).toHaveValue(
    GREENHOUSE_E2E_SECRET
  )
  await owner.setViewportSize({ width: 1280, height: 1400 })
  await shot(owner, "info")
  await owner.keyboard.press("Escape")

  // The page: the tag, Disconnect, no other setup button, and the linked job.
  await expect(owner.getByText("connected", { exact: true }).filter({ visible: true })).toBeVisible()
  await expect(owner.getByRole("button", { name: "Disconnect" })).toBeVisible()
  await expect(owner.getByRole("button", { name: /web hook/i })).toHaveCount(0)
  await expect(owner.getByText("E2E Backend developer")).toBeVisible()
  await expect(owner.getByLabel("2 invited")).toBeVisible()
  await shot(owner, "page")

  // Greenhouse names no account: under the title is who connected it, or nothing when that's
  // unknown.
  const header = owner.getByRole("heading", { level: 1 }).locator("xpath=../..")
  await expect(header).toHaveText(/^Greenhouse\s*connected$/, { useInnerText: true })
  await nameAtsConnectionMaker(company.id, "E2E Maker")
  await owner.reload()
  await expect(header.getByText("Connected by E2E Maker")).toBeVisible()
  await visit(owner, tab)
  await expect(
    owner.getByRole("link", { name: /^Greenhouse/ }).getByText("Connected by E2E Maker")
  ).toBeVisible()
  await shot(owner, "connected-by")
})
