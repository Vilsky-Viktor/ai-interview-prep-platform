import type { Page } from "@playwright/test"

/** How many questions count as answered in the session's header ("3 / 10" beside the clock):
 * the header's own text, without the clock's. */
export async function answered(page: Page): Promise<string> {
  return page
    .locator("p", { has: page.getByRole("timer") })
    .evaluate((header) =>
      [...header.childNodes]
        .filter((node) => node.nodeType === Node.TEXT_NODE)
        .map((node) => node.textContent)
        .join("")
        .split("/")[0]
        .trim()
    )
}
