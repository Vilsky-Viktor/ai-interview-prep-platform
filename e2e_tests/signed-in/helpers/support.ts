import { expect, type Locator, type Page } from "@playwright/test"

import { visit } from "./navigation"

/** Searches the admin zone's support tab for `query`; the links of what it found, in order,
 * once the API has answered. Pressing Enter before the page is ready sends nothing, so it's
 * pressed again until the search goes out. */
export async function supportSearch(page: Page, query: string) {
  await visit(page, "/superadmin/support")
  const box = page.getByRole("main").getByRole("textbox")

  await expect(async () => {
    await box.fill(query)
    const answered = page.waitForResponse((response) => response.url().includes("/support/search"), {
      timeout: 5_000,
    })
    await box.press("Enter")
    await answered
  }).toPass({ timeout: 60_000 })

  return page.getByRole("main").getByRole("list").getByRole("link")
}

/** The links on the page that open `kind`'s support page ("companies", "interviews",
 * "candidates" or "users"), the one of `id` when given. */
export function supportLink(page: Page, kind: string, id = "") {
  const end = id ? `$="/superadmin/support/${kind}/${id}"` : `*="/superadmin/support/${kind}/"`

  return page.locator(`main a[href${end}]`)
}

/** The id at the end of a support page link. */
export async function supportId(link: Locator) {
  const href = await link.getAttribute("href")

  return (href ?? "").split("/").pop() ?? ""
}
