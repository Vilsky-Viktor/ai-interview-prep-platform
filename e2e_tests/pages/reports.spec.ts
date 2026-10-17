import { expect, test } from "@playwright/test";

// The home page's reports section shows a report's share popup with every chat app a report's
// summary can go to: WhatsApp, Telegram, Viber and LINE.
test("the reports section shows every chat app a report can be shared to", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("#reports");
  await section.scrollIntoViewIfNeeded();

  await expect(section.getByTestId("share-apps").locator("svg")).toHaveCount(4);
  await section.screenshot({ path: test.info().outputPath("reports-section.png") });
});
