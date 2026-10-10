import type { Locator, Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { createCompany } from "../helpers/api"
import { addAiConnections, deleteAiConnections } from "../helpers/db"
import { box, PHONE } from "../helpers/layout"
import { openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { uidOf } from "../helpers/sign-in"
import { throwawayEmail } from "../helpers/users"

/** Checks an Instructions dialog opened on the dialog itself (not its first field), and that
 * only its body scrolls: Close sits outside the scrolling part. */
async function expectInstructionsDialog(page: Page, dialog: Locator) {
  await expect
    .poll(() => page.evaluate(() => document.activeElement?.getAttribute("role")))
    .toBe("dialog")
  const closeInBody = await dialog.evaluate((popup) => {
    const scrolling = [...popup.querySelectorAll("*")].find(
      (item) => getComputedStyle(item).overflowY === "auto"
    )
    const close = [...popup.querySelectorAll("button")].find(
      (item) => item.textContent?.trim() === "Close"
    )

    return { scrolling: Boolean(scrolling), close: Boolean(close), inside: scrolling?.contains(close!) }
  })
  expect(closeInBody).toEqual({ scrolling: true, close: true, inside: false })
}

// The MCP server sits last on the integrations tab, with its Instructions: the server's address
// and how to add it to Claude and ChatGPT. A real connection needs an AI app going through
// OAuth, so the user's connections are saved straight into the database; disconnecting goes
// through the API for real.
test("an owner sees the MCP server's instructions and disconnects AI apps", async ({
  signInAs,
}) => {
  const owner = await signInAs(throwawayEmail("mcp"))
  const uid = await uidOf(owner)
  const company = await createCompany(owner)
  const tab = `/companies/${company.id}/integrations`

  try {
    await visit(owner, tab)
    const row = owner.getByRole("listitem").filter({ hasText: "MCP server" })
    await expect(row.getByText("Connect Claude, ChatGPT and other AI apps to prepza.")).toBeVisible()
    await expect(row.getByText("connected", { exact: true })).toHaveCount(0)
    await expect(row.getByRole("link", { name: /^MCP server/ })).toHaveAttribute("href", `${tab}/ai`)

    // The address to copy, then Claude's and ChatGPT's steps.
    await openDialog(owner, row.getByRole("button", { name: "Instructions" }))
    const dialog = owner.getByRole("dialog")
    await expect(dialog.getByRole("heading", { name: "Server address" })).toBeVisible()
    await expect(dialog.getByRole("textbox", { name: "Copy URL" })).toHaveValue(/\/mcp$/)
    await expect(dialog.getByRole("button", { name: "Copy URL" })).toBeEnabled()
    await expect(dialog.getByRole("heading", { name: /^Add it to Claude$/i })).toBeVisible()
    await expect(dialog.getByRole("heading", { name: /^Add it to ChatGPT$/i })).toBeVisible()
    await expectInstructionsDialog(owner, dialog)
    await shot(owner, "instructions")
    await dialog.getByRole("button", { name: "Close" }).click()
    await expect(dialog).toHaveCount(0)

    await visit(owner, `${tab}/ai`)
    await expect(owner.getByText("No apps connected yet.")).toBeVisible()
    await shot(owner, "no-apps")

    // Connected: one "connected" tag, and the apps' names, the latest first.
    await addAiConnections(uid, ["Claude", "ChatGPT"])
    await visit(owner, tab)
    await expect(row.getByText("connected", { exact: true })).toHaveCount(1)
    await expect(row.getByText("Claude, ChatGPT", { exact: true })).toBeVisible()
    await expect(row.getByText(/Connected:/)).toHaveCount(0)
    await shot(owner, "row-connected")

    // The row opens the apps' page: each with Disconnect, which asks first.
    await row.getByRole("link", { name: /^MCP server/ }).click()
    await expect(owner).toHaveURL(new RegExp(`${tab}/ai$`))
    const apps = owner.getByRole("main").getByRole("listitem")
    await expect(apps).toHaveCount(2)
    await expect(apps.getByRole("button", { name: "Disconnect" })).toHaveCount(2)
    await shot(owner, "apps")
    const claude = apps.filter({ hasText: "Claude" })
    await openDialog(owner, claude.getByRole("button", { name: "Disconnect" }))
    await expect(owner.getByRole("dialog")).toContainText("Disconnect Claude?")
    await owner.getByRole("dialog").getByRole("button", { name: "Disconnect" }).click()
    await expect(apps).toHaveCount(1)
    await expect(apps).toContainText("ChatGPT")
    await expect(owner.getByText("Claude", { exact: true })).toHaveCount(0)
  } finally {
    await deleteAiConnections(uid)
  }
})

// On a phone the MCP server's Instructions fill the screen.
test("the MCP server's instructions fill a phone's screen", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("mcp-phone"))
  const company = await createCompany(owner)
  await owner.setViewportSize(PHONE)

  await visit(owner, `/companies/${company.id}/integrations/ai`)
  await openDialog(owner, owner.getByRole("main").getByRole("button", { name: "Instructions" }))
  await owner.waitForTimeout(400)
  const dialog = await box(owner.getByRole("dialog"))
  expect(Math.abs(dialog.height - PHONE.height)).toBeLessThanOrEqual(2)
  expect(dialog.top).toBe(0)
  await expectInstructionsDialog(owner, owner.getByRole("dialog"))
  await shot(owner, "instructions-phone", false)
})

// An AI app sends the user to /connect to allow it. A request the API doesn't know (expired or
// already answered) says so; a real one shows who asks, with a warning for an app prepza doesn't
// know, and Deny sends the browser back to the app. Real requests come from an app's OAuth, so
// that one is answered in the browser.
test("the consent page asks before an AI app may use the account", async ({ signInAs }) => {
  const email = throwawayEmail("mcp-consent")
  const user = await signInAs(email)

  await visit(user, "/connect?request=e2e-unknown")
  await expect(user.getByText("This link has expired or was already used.", { exact: false })).toBeVisible()

  await user.route("**/assistant/connect/e2e-request", (route) =>
    route.fulfill({
      json: { client_name: "E2E App", redirect_host: "e2e.example.com", known_client: false },
    })
  )
  await user.route("**/assistant/connect/e2e-request/deny", (route) =>
    route.fulfill({ json: { redirect_url: "/?error=access_denied" } })
  )
  await visit(user, "/connect?request=e2e-request")
  await expect(user.getByRole("heading", { name: "Connect E2E App to prepza" })).toBeVisible()
  await expect(user.getByText(`E2E App (e2e.example.com) wants to use your prepza account, ${email}.`)).toBeVisible()
  await expect(user.getByText("prepza doesn't know this app.", { exact: false })).toBeVisible()
  await expect(user.getByRole("button", { name: "Allow" })).toBeVisible()
  await shot(user, "consent")
  await user.getByRole("button", { name: "Deny" }).click()
  await expect(user).toHaveURL(/\/\?error=access_denied$/)
})
