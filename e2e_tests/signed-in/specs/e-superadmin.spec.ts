import type { Locator, Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { api, createCompany } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail } from "../helpers/users"

const PAUSE_NOTICE = "New interviews are paused for now"
const MAINTENANCE_NOTICE = "Maintenance mode is on: only superadmins can use prepza right now."

/** A switch on the admin zone's controls page, by its card's title. */
function control(page: Page, title: string) {
  return page.locator("div.rounded-2xl", { hasText: title }).getByRole("switch")
}

test("superadmin sorts pass rates", async ({ signInSuperadmin }) => {
  const superadmin = await signInSuperadmin()
  await visit(superadmin, "/superadmin/pass-rates")
  // The sort: a gray pill opening the orders.
  const sort = superadmin.getByRole("button", { name: /^Sort by:/ })
  await expect(sort).toHaveText(/Lowest pass rate first/i)
  await shot(superadmin, "pass-rates")
  await expect(async () => {
    await sort.click()
    await expect(superadmin.getByRole("menu")).toBeVisible({ timeout: 2_000 })
  }).toPass()
  await shot(superadmin, "pass-rates-sort-menu")
  await superadmin.getByRole("menuitemradio", { name: /most finished first/i }).click()
  await expect(superadmin).toHaveURL(/sort=finished/)
  await expect(sort).toHaveText(/Most finished first/i)
  await shot(superadmin, "pass-rates-by-finished")
})

test("superadmin sees a month's stats, a year's and all time, kept after a reload", async ({
  signInSuperadmin,
}) => {
  const superadmin = await signInSuperadmin()
  await visit(superadmin, "/superadmin/stats")
  // A fresh start: this month.
  await superadmin.evaluate(() => localStorage.removeItem("prepza_stats_period"))
  await visit(superadmin, "/superadmin/stats")
  const now = new Date()
  const thisMonth = now.toLocaleString("en-US", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  })
  const thisYear = String(now.getUTCFullYear())
  const period = superadmin.getByRole("button", { name: "Period" })
  const allTime = superadmin.getByRole("checkbox")
  await expect(period).toHaveText(thisMonth)
  const cards = superadmin.locator("dl")
  await expect(cards.getByRole("term")).toHaveCount(9)
  // Every service answered: no card is left as a dash.
  await expect(cards.getByRole("definition").filter({ hasText: /^—$/ })).toHaveCount(0)
  await shot(superadmin, "stats")
  // One choice in the menu: a month with its year, or a year.
  await period.click()
  await expect(superadmin.getByRole("menuitemradio", { name: thisMonth })).toHaveAttribute(
    "aria-checked",
    "true"
  )
  await shot(superadmin, "stats-menu")
  await superadmin.getByRole("menuitemradio", { name: thisYear, exact: true }).click()
  await expect(period).toHaveText(thisYear)
  // All time turns the menu off, keeping its year.
  await allTime.click()
  await expect(allTime).toBeChecked()
  await expect(period).toBeDisabled()
  await shot(superadmin, "stats-all-time")
  // The browser keeps the choice; the address doesn't change.
  await expect(superadmin).toHaveURL(/\/superadmin\/stats$/)
  await superadmin.reload()
  await expect(allTime).toBeChecked()
  await expect(period).toHaveText(thisYear)
  await allTime.click()
  await expect(period).toBeEnabled()
})

/** Turns a switch on the controls page, opened afresh: the dev frontend may have reloaded it. */
async function flip(page: Page, title: string, on: boolean) {
  await visit(page, "/superadmin/controls")
  const toggle = control(page, title)
  await expect(toggle).toBeChecked({ checked: !on })
  await toggle.click()
  await expect(toggle).toBeChecked({ checked: on })
}

/** Opens `path` until `shown` is on it: the frontend keeps maintenance mode's state for a few
 * seconds (MAINTENANCE_CACHE_MS). */
async function visitUntil(page: Page, path: string, shown: Locator) {
  await expect(async () => {
    await visit(page, path)
    await expect(shown).toBeVisible({ timeout: 2_000 })
  }).toPass({ timeout: 60_000 })
}

async function paused(page: Page) {
  return (await api<{ paused: boolean }>(page, "GET", "/companies/pause")).paused
}

async function maintenanceOn(page: Page) {
  return (await api<{ on: boolean }>(page, "GET", "/companies/superadmin/maintenance")).on
}

// Both switches are global: they're turned on only when found off, and always turned off again,
// even when a step fails.
test("superadmin turns the pause and maintenance mode on and off", async ({
  signInAs,
  signInSuperadmin,
}) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const superadmin = await signInSuperadmin()
  test.skip(
    (await paused(superadmin)) || (await maintenanceOn(superadmin)),
    "The pause or maintenance mode is already on: left as it is"
  )

  try {
    await visit(superadmin, "/superadmin/controls")
    await shot(superadmin, "controls")
    await flip(superadmin, "Emergency pause", true)
    await expect.poll(() => paused(superadmin)).toBe(true)
    await shot(superadmin, "pause-on")

    const newInterview = `/companies/${company.id}/interviews/new`
    await visit(owner, newInterview)
    await expect(owner.getByText(PAUSE_NOTICE)).toBeVisible()
    // The start box is there but off, so it's clearly unavailable.
    await expect(owner.getByLabel("Job description")).toBeDisabled()
    await shot(owner, "new-interview-paused")
    await flip(superadmin, "Emergency pause", false)
    await expect.poll(() => paused(superadmin)).toBe(false)
    await visit(owner, newInterview)
    await expect(owner.getByText("Create an interview")).toBeVisible()
    await expect(owner.getByText(PAUSE_NOTICE)).toHaveCount(0)
    await expect(owner.getByLabel("Job description")).toBeEnabled()

    // Maintenance asks first, saying how many candidates are in an interview right now.
    await visit(superadmin, "/superadmin/controls")
    await control(superadmin, "Maintenance mode").click()
    const dialog = superadmin.getByRole("dialog")
    await expect(dialog).toContainText("Turn on maintenance mode?")
    await shot(superadmin, "maintenance-confirm")
    await dialog.getByRole("button", { name: "Turn on" }).click()
    await expect(dialog).toBeHidden()
    await expect.poll(() => maintenanceOn(superadmin)).toBe(true)

    // Everyone else gets the maintenance screen; superadmins the site, with a warning card.
    await visitUntil(owner, "/companies", owner.getByRole("heading", { name: "Under maintenance" }))
    await shot(owner, "maintenance-screen")
    await visitUntil(superadmin, "/companies", superadmin.getByText(MAINTENANCE_NOTICE))
    await shot(superadmin, "maintenance-superadmin")

    await flip(superadmin, "Maintenance mode", false)
    await expect.poll(() => maintenanceOn(superadmin)).toBe(false)
    await visitUntil(owner, "/companies", owner.getByText(company.name))
  } finally {
    await api(superadmin, "PUT", "/companies/superadmin/maintenance", { on: false })
    await api(superadmin, "PUT", "/companies/superadmin/pause", { paused: false })
  }
})
