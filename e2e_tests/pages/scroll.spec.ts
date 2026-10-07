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

// On a long page, "back to top" shows once it's scrolled down, and goes back to the top.
test("back to top shows on a long page and returns to its top", async ({ page }) => {
  await page.goto("/")
  await expect(page.getByRole("button", { name: "Back to top" })).toHaveCount(0)
  await page.mouse.wheel(0, 2500)
  const button = page.getByRole("button", { name: "Back to top" })
  await expect(button).toBeVisible()
  await button.click()
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0)
  await expect(button).toHaveCount(0)
})
