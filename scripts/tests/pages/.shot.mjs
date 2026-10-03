import { chromium } from "@playwright/test"
const browser = await chromium.launch({ args: ["--host-rules=MAP localhost:8090 gateway:80"] })
const locales = (process.env.LOCALES || "en").split(",")
const paths = (process.env.PATHS || "/").split(",")
for (const locale of locales) {
  for (const path of paths) {
    for (const [name, width] of [["desktop", 1280], ["phone", 390]]) {
      const page = await browser.newPage({ viewport: { width, height: 800 }, locale })
      const errors = []
      page.on("console", (m) => m.type() === "error" && errors.push(m.text()))
      await page.goto("http://localhost:8090" + path, { timeout: 90000 })
      await page.waitForTimeout(1500)
      const slug = path.replace(/\W/g, "") || "home"
      await page.screenshot({ path: `/tests/test-results/shot-${locale}-${slug}-${name}.png`, fullPage: true })
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)
      console.log(locale, path, name, "overflow:", overflow, "errors:", errors.length ? errors : "none")
    }
  }
}
await browser.close()
