import { expect, test } from "@playwright/test";

// The home page's "how it works" link scrolls smoothly to its section, not in one jump.

test("how it works scrolls smoothly", async ({ page }, info) => {
  test.skip(info.project.name === "phone")
  await page.goto("/")
  await page.waitForLoadState("networkidle")
  expect(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior)).toBe("smooth")
  await page.getByRole("link", { name: /how it works|more/i }).first().click()
  // Midway through the animation the page is between the top and the section.
  await page.waitForTimeout(120)
  const midway = await page.evaluate(() => window.scrollY)
  await page.waitForTimeout(1500)
  const end = await page.evaluate(() => window.scrollY)
  expect(midway).toBeGreaterThan(0)
  expect(midway).toBeLessThan(end)
})
