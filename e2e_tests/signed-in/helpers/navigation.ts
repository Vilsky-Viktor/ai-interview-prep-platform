import { expect, type Locator, type Page } from "@playwright/test"

/** Opens the dialog `button` opens, clicking again if the first click came before the page was
 * ready for it. */
export async function openDialog(page: Page, button: Locator) {
  await expect(async () => {
    await button.click()
    await expect(page.getByRole("dialog")).toBeVisible({ timeout: 2_000 })
  }).toPass()
}

/** Opens one of a page's tabs (a company's, the admin zone's) by its name, clicking again if the
 * first click came before the page was ready for it. */
export async function openTab(page: Page, name: string) {
  const tab = page.getByRole("main").getByRole("navigation").getByRole("link", { name, exact: true })
  const href = await tab.getAttribute("href")

  await expect(async () => {
    await tab.click()
    await expect(page).toHaveURL(new RegExp(`${href}$`), { timeout: 3_000 })
  }).toPass()
}

/** Opens `path`. The local frontend is a dev server that can restart (the gateway then answers
 * 502), so it's tried again until it's back. Other statuses count: maintenance mode is a 503. */
export async function visit(page: Page, path: string) {
  await expect(async () => {
    const response = await page.goto(path)
    expect(response?.status(), `${path} answers`).not.toBe(502)
  }).toPass({ timeout: 90_000, intervals: [2_000] })
}
