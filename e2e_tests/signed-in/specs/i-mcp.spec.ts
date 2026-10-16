import type { Locator, Page } from "@playwright/test"
import { createHash, randomBytes } from "node:crypto"

import { FRONTEND_URL } from "../constants"
import { expect, test } from "../fixtures"
import { createCompany } from "../helpers/api"
import { addAiConnections, deleteAiConnections } from "../helpers/db-integrations"
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

  // A request that runs out while the card is open says it expired, not "something went wrong".
  await user.route("**/assistant/connect/e2e-expiring", (route) =>
    route.fulfill({
      json: { client_name: "E2E App", redirect_host: "e2e.example.com", known_client: false },
    })
  )
  await user.route("**/assistant/connect/e2e-expiring/approve", (route) =>
    route.fulfill({ status: 404, json: { detail: "Not found" } })
  )
  await visit(user, "/connect?request=e2e-expiring")
  await user.getByRole("button", { name: "Allow" }).click()
  await expect(user.getByText("This link has expired or was already used.", { exact: false })).toBeVisible()
})

// Allow completes the connection for real: an app on the user's computer registers and asks
// prepza through /authorize, as Claude Code does; Allow sends the browser back to the app with a
// code and the state it sent, and the app exchanges the code for its tokens. The app's own page
// isn't there, so the browser's return to it is answered by the test.
test("Allow on the consent page connects the AI app", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("mcp-allow"))
  const uid = await uidOf(owner)
  const company = await createCompany(owner)
  const callback = "http://127.0.0.1:53682/callback"
  const name = "E2E Local App"
  const registered = await owner.request.post(`${FRONTEND_URL}/register`, {
    data: {
      client_name: name,
      redirect_uris: [callback],
      token_endpoint_auth_method: "none",
      grant_types: ["authorization_code", "refresh_token"],
      response_types: ["code"],
    },
  })
  expect(registered.status()).toBe(201)
  const clientId: string = (await registered.json()).client_id
  const verifier = randomBytes(32).toString("base64url")
  const challenge = createHash("sha256").update(verifier).digest("base64url")
  await owner.route(`${callback}*`, (route) => route.fulfill({ body: "Back in the app" }))

  try {
    const query = new URLSearchParams({
      response_type: "code",
      client_id: clientId,
      redirect_uri: callback,
      code_challenge: challenge,
      code_challenge_method: "S256",
      state: "e2e-state",
    })
    await visit(owner, `/authorize?${query}`)
    await expect(owner).toHaveURL(/\/connect\?request=/)
    await expect(owner.getByRole("heading", { name: `Connect ${name} to prepza` })).toBeVisible()
    await expect(owner.getByText("prepza doesn't know this app.", { exact: false })).toHaveCount(0)
    await shot(owner, "consent-local-app")
    await owner.getByRole("button", { name: "Allow" }).click()
    await expect(owner).toHaveURL(/^http:\/\/127\.0\.0\.1:53682\/callback\?code=[^&]+&state=e2e-state$/)
    const code = new URL(owner.url()).searchParams.get("code") ?? ""

    // The app's side: the code buys its tokens, once.
    const exchange = () =>
      owner.request.post(`${FRONTEND_URL}/token`, {
        form: {
          grant_type: "authorization_code",
          code,
          redirect_uri: callback,
          client_id: clientId,
          code_verifier: verifier,
        },
      })
    const tokens = await exchange()
    expect(tokens.status()).toBe(200)
    expect((await tokens.json()).access_token).toMatch(/^pzm_/)
    expect((await exchange()).status()).toBe(400)

    // The user sees the app connected.
    await visit(owner, `/companies/${company.id}/integrations/ai`)
    const app = owner.getByRole("main").getByRole("listitem").filter({ hasText: name })
    await expect(app.getByRole("button", { name: "Disconnect" })).toBeVisible()
    await shot(owner, "apps-after-allow")
  } finally {
    await deleteAiConnections(uid, [clientId])
  }
})
