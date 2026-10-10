import type { Locator } from "@playwright/test"

// A phone's screen, for the phone layouts.
export const PHONE = { width: 390, height: 844 }

/** Where `locator` is on the page, in whole pixels. */
export async function box(locator: Locator) {
  const found = (await locator.boundingBox({ timeout: 15_000 }))!

  return {
    left: Math.round(found.x),
    top: Math.round(found.y),
    width: Math.round(found.width),
    height: Math.round(found.height),
    right: Math.round(found.x + found.width),
    bottom: Math.round(found.y + found.height),
  }
}
