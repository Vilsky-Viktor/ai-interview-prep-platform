import { expect, test } from "@playwright/test";

// The home page's reports section names every chat app a report's summary can go to (its share
// popup, a drawing hidden from screen readers, shows their icons).
test("the reports section names every chat app a report can be shared to", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("section", {
    has: page.getByRole("heading", { name: "Share results in one click" }),
  });
  await section.scrollIntoViewIfNeeded();

  await expect(
    section.getByText("Email the PDF, or share on WhatsApp, Telegram, Viber or LINE"),
  ).toBeVisible();
  await section.screenshot({ path: test.info().outputPath("reports-section.png") });
});
