import { expect, test } from "../fixtures"
import { API_URL } from "../constants"
import { createCompany, createInterview } from "../helpers/api"
import { markWebhookFailing } from "../helpers/db"
import { openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail } from "../helpers/users"

// The API sits last on the integrations tab and opens its own page, where an owner makes a key
// (shown once) and adds a web hook (its secret shown once).
test("an owner makes an API key and adds a web hook", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const tab = `/companies/${company.id}/integrations`

  await owner.setViewportSize({ width: 1280, height: 1400 })
  await visit(owner, tab)
  await shot(owner, "list")
  await visit(owner, `${tab}/api`)
  await shot(owner, "empty")

  await openDialog(owner, owner.getByRole("button", { name: "New key" }))
  await owner.getByRole("dialog").getByRole("textbox").fill("Careers site")
  // When it expires: nothing picked yet, so the key can't be made; the menu doesn't move the dialog.
  const create = owner.getByRole("dialog").getByRole("button", { name: "New key" })
  const expiry = owner.getByRole("dialog").getByRole("button", { name: "Expires in" })
  await expect(expiry).toHaveText("Expires in")
  await expect(create).toBeDisabled()
  await owner.waitForTimeout(500)
  const closed = await owner.getByRole("dialog").boundingBox()
  await expiry.click()
  await expect(owner.getByRole("menu")).toBeVisible()
  expect(await owner.getByRole("dialog").boundingBox()).toEqual(closed)
  await shot(owner, "expiry-menu")
  // Never expiring is allowed, with a warning under the select while it's picked.
  const warning = owner.getByRole("dialog").getByText("A key that never expires", { exact: false })
  await owner.getByRole("menuitemradio", { name: "Never" }).click()
  await expect(warning).toBeVisible()
  await shot(owner, "never-warning")
  await expiry.click()
  await owner.getByRole("menuitemradio", { name: "12 months" }).click()
  await expect(warning).toHaveCount(0)
  await expect(create).toBeEnabled()
  await shot(owner, "new-key")
  await create.click()
  await expect(owner.getByRole("dialog").getByRole("textbox", { name: "Copy key" })).toHaveValue(
    /^pz_/
  )
  await shot(owner, "key-shown")
  const key = await owner
    .getByRole("dialog")
    .getByRole("textbox", { name: "Copy key" })
    .inputValue()
  await owner.keyboard.press("Escape")

  // The key works: the company's interview, and its candidate invited through the API.
  const headers = { Authorization: `Bearer ${key}` }
  const listed = await owner.request.get(`${API_URL}/v1/interviews`, { headers })
  expect(listed.status()).toBe(200)
  expect((await listed.json()).map((item: { id: string }) => item.id)).toEqual([interviewId])
  const invited = await owner.request.post(`${API_URL}/v1/interviews/${interviewId}/candidates`, {
    headers,
    data: { email: "delivered+e2e-api-candidate@resend.dev" },
  })
  expect(invited.status()).toBe(201)
  expect(await invited.json()).toMatchObject({ status: "invited", progress: 0 })
  const refused = await owner.request.get(`${API_URL}/v1/interviews`, {
    headers: { Authorization: "Bearer pz_wrong" },
  })
  expect(refused.status()).toBe(401)

  await shot(owner, "keys-tab")

  // The web hooks have a tab of their own, with its own button.
  await owner.locator("main nav").getByRole("link", { name: "web hooks" }).click()
  await expect(owner).toHaveURL(/\?tab=webhooks$/)
  await expect(owner.getByRole("button", { name: "New key" })).toHaveCount(0)

  // Only HTTPS addresses on the internet: anything else is refused, in a red toast.
  await openDialog(owner, owner.getByRole("button", { name: "Add web hook" }))
  await owner.getByRole("dialog").getByRole("textbox").fill("http://example.com/prepza")
  await owner.getByRole("dialog").getByRole("button", { name: "Add web hook" }).click()
  await expect(owner.getByText("Use an HTTPS address that's reachable from the internet")).toBeVisible()
  await shot(owner, "webhook-refused")
  await owner.getByRole("dialog").getByRole("textbox").fill("https://example.com/prepza")
  await owner.getByRole("dialog").getByRole("button", { name: "Add web hook" }).click()
  await expect(
    owner.getByRole("dialog").getByRole("textbox", { name: "Copy secret" })
  ).toHaveValue(/^whsec_/)
  await shot(owner, "secret-shown")
  await owner.keyboard.press("Escape")
  await expect(owner.getByText("https://example.com/prepza")).toBeVisible()
  await shot(owner, "filled")
  await visit(owner, tab)
  await shot(owner, "list-filled")

  // A web hook that stopped taking events, after days of retries, says so in its row.
  await markWebhookFailing("https://example.com/prepza", company.id)
  await visit(owner, `${tab}/api?tab=webhooks`)
  await expect(owner.getByText("Not answering: recent results didn't reach it")).toBeVisible()
  await shot(owner, "webhook-failing")
})
