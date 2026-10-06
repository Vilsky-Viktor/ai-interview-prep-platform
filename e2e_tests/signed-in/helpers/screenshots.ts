import { type Page, test } from "@playwright/test"
import path from "node:path"

import { SCREENSHOTS } from "../constants"

// Screenshots taken so far in each spec, to number them in order.
const counts = new Map<string, number>()

/** A screenshot in screenshots/<spec>/<number>-<name>.png, of the whole page unless `fullPage`
 * is false (the home page's landing sections are long). */
export async function shot(page: Page, name: string, fullPage = true) {
  const spec = path.basename(test.info().file, ".spec.ts")
  const count = (counts.get(spec) ?? 0) + 1
  counts.set(spec, count)
  // Dialogs and toasts finish animating first.
  await page.waitForTimeout(400)
  await page.screenshot({
    path: `${SCREENSHOTS}/${spec}/${String(count).padStart(2, "0")}-${name}.png`,
    fullPage,
  })
}
