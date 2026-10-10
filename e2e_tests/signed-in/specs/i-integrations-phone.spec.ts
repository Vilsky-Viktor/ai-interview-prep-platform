import type { Locator, Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection, addSlackConnection, markAtsBroken } from "../helpers/db"
import { box, PHONE } from "../helpers/layout"
import { openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

/** The page's content width: the header's (the page's visible width, without the scrollbar
 * desktop Chrome draws) inside its 24px side padding. */
async function contentWidth(page: Page) {
  return (await box(page.getByRole("banner"))).width - 48
}

/** The page's buttons sit on their own line under its title, together as wide as the page. */
async function expectButtonsUnderTitle(page: Page, buttons: Locator[]) {
  const title = await box(page.getByRole("heading", { level: 1 }))
  const found = await Promise.all(buttons.map((button) => box(button)))

  for (const button of found) {
    expect(button.top).toBeGreaterThan(title.bottom)
  }

  const left = Math.min(...found.map((button) => button.left))
  const right = Math.max(...found.map((button) => button.right))
  expect(right - left).toBeGreaterThanOrEqual((await contentWidth(page)) - 2)
}

/** Reconnect takes a line of its own under the other buttons, as wide as all of them. */
async function expectReconnectOwnLine(scope: Locator) {
  const reconnect = scope.getByRole("button", { name: "Reconnect" })
  const buttons = await box(reconnect.locator("xpath=.."))
  const own = await box(reconnect)
  expect(Math.abs(own.width - buttons.width)).toBeLessThanOrEqual(2)
  expect(own.top).toBeGreaterThan((await box(scope.getByRole("button", { name: "Disconnect" }))).bottom)
}

/** The Instructions dialog `button` opens fills the screen's height. */
async function expectFullHeightDialog(page: Page, button: Locator) {
  await openDialog(page, button)
  await page.waitForTimeout(400)
  const dialog = await box(page.getByRole("dialog"))
  expect(Math.abs(dialog.height - PHONE.height)).toBeLessThanOrEqual(2)
  await page.keyboard.press("Escape")
  await expect(page.getByRole("dialog")).toHaveCount(0)
}

// On a phone the integrations tab's rows have a small logo beside the name and their buttons on
// the line under it; on Slack's, an ATS's and the API's pages the buttons go under the title,
// across the page, and the Instructions fill the screen. A connection that stopped working puts
// Reconnect on a line of its own.
test("the integrations pages on a phone", async ({ signInAs }) => {
  test.setTimeout(300_000)
  const owner = await signInAs(throwawayEmail("integrations-phone"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const tab = `/companies/${company.id}/integrations`
  await addSlackConnection(company.id)
  await addAtsConnection(company.id, interviewId, { invited: 3, notInvited: 2 })
  await owner.setViewportSize(PHONE)

  await visit(owner, tab)

  for (const name of ["Slack", "Workable", "API", "MCP server"]) {
    const row = owner.getByRole("listitem").filter({ hasText: name }).first()
    // The link's two parts: the logo, then the name and its text.
    const logo = await box(row.getByRole("link").locator("> span").first())
    const title = await box(row.getByRole("link").locator("> span").nth(1))
    const instructions = await box(row.getByRole("button").first())
    expect(logo.width, name).toBe(48)
    expect(logo.height, name).toBe(48)
    expect(title.left, name).toBeGreaterThan(logo.right)
    expect(instructions.top, name).toBeGreaterThan(Math.max(logo.bottom, title.bottom))
  }

  await shot(owner, "tab")
  await expectFullHeightDialog(
    owner,
    owner
      .getByRole("listitem")
      .filter({ hasText: "Workable" })
      .getByRole("button", { name: "Instructions" })
  )

  // Slack: the buttons under the title; the notifications' box keeps its rounded corners.
  await visit(owner, `${tab}/slack`)
  await expectButtonsUnderTitle(owner, [
    owner.getByRole("main").getByRole("button", { name: "Instructions" }),
    owner.getByRole("main").getByRole("button", { name: "Disconnect" }),
  ])
  const kinds = owner
    .locator("main div.divide-y.rounded-2xl")
    .filter({ has: owner.getByRole("checkbox", { name: "An interview is ready" }) })
  await expect(kinds).not.toHaveCSS("border-top-left-radius", "0px")
  await shot(owner, "slack")

  // Workable: the buttons under the title, "Link a job" across the page under its text, and a
  // linked job's numbers on the line under its name.
  await visit(owner, `${tab}/workable`)
  await expectButtonsUnderTitle(owner, [
    owner.getByRole("main").getByRole("button", { name: "Instructions" }),
    owner.getByRole("main").getByRole("button", { name: "Disconnect" }),
  ])
  const link = await box(owner.getByRole("button", { name: "Link a job" }))
  const linksText = await box(owner.getByText("Candidates who reach the stage in Workable", { exact: false }))
  expect(link.top).toBeGreaterThan(linksText.bottom)
  expect(link.width).toBeGreaterThanOrEqual((await contentWidth(owner)) - 2)
  const job = await box(owner.getByText("E2E Backend developer"))
  const invited = await box(owner.getByLabel("3 invited"))
  const unlink = await box(owner.getByRole("button", { name: "Unlink" }))
  expect(invited.top).toBeGreaterThan(job.bottom)
  expect(unlink.top).toBeGreaterThan(job.bottom)
  await shot(owner, "workable")
  await expectFullHeightDialog(
    owner,
    owner.getByRole("main").getByRole("button", { name: "Instructions" })
  )

  // A key that stopped working: Reconnect on its own line, on the page and on the tab.
  await markAtsBroken(company.id)
  await owner.reload()
  await expectReconnectOwnLine(owner.getByRole("main"))
  await shot(owner, "workable-broken")
  await visit(owner, tab)
  await expectReconnectOwnLine(owner.getByRole("listitem").filter({ hasText: "Workable" }))
  await shot(owner, "tab-broken")

  // The API: the docs and New key under the title.
  await visit(owner, `${tab}/api`)
  await expectButtonsUnderTitle(owner, [
    owner.getByRole("main").getByRole("button", { name: "API docs" }),
    owner.getByRole("main").getByRole("button", { name: "New key" }),
  ])
  await shot(owner, "api")
})
