import { expect, test } from "@playwright/test"

// The signed-out pages. Signed-in ones are checked by hand: sign-in isn't automated.
const PAGES = ["/", "/library", "/pricing", "/terms", "/privacy", "/faq"]
// The width every page's <main> has: max-w-5xl (CLAUDE.md, rule 6).
const MAIN_MAX_WIDTH = 1024

for (const path of PAGES) {
  test(`${path} loads cleanly and follows the layout rules`, async ({ page }) => {
    const errors: string[] = []
    page.on("console", (message) => {
      if (message.type() === "error") {
        errors.push(message.text())
      }
    })
    page.on("pageerror", (error) => errors.push(error.message))

    const response = await page.goto(path)
    await page.waitForLoadState("networkidle")

    expect(response?.status()).toBe(200)
    expect(errors).toEqual([])

    const layout = await page.evaluate(() => {
      const root = document.documentElement
      const footer = document.querySelector("footer")!.getBoundingClientRect()
      const heading = document.querySelector("h1")
      const input = document.querySelector("textarea")

      return {
        viewport: window.innerWidth,
        scrollWidth: root.scrollWidth,
        clientWidth: root.clientWidth,
        scrollHeight: root.scrollHeight,
        innerHeight: window.innerHeight,
        footerBottom: footer.bottom + window.scrollY,
        mainWidth: document.querySelector("main")!.getBoundingClientRect().width,
        headingCase: heading ? getComputedStyle(heading).textTransform : "lowercase",
        inputBottom: input ? input.getBoundingClientRect().bottom : 0,
      }
    })

    // Nothing wider than the window, on a phone too.
    expect(layout.scrollWidth).toBeLessThanOrEqual(layout.clientWidth)
    // Every page is as wide as the header.
    expect(layout.mainWidth).toBe(Math.min(MAIN_MAX_WIDTH, layout.viewport))
    // The footer ends the page.
    expect(Math.abs(layout.footerBottom - layout.scrollHeight)).toBeLessThanOrEqual(1)
    // The home page's input is on the first screen, above the landing sections.
    if (path === "/") {
      expect(layout.inputBottom).toBeLessThanOrEqual(layout.innerHeight)
    }

    // Titles are lowercase, like the logo.
    expect(layout.headingCase).toBe("lowercase")
    await expect(page.getByRole("button", { name: /sign in/i }).first()).toBeVisible()
  })
}
