import { expect, test } from "@playwright/test";

// The home page's invite section shows the four ways candidates get an interview, each with a
// piece of the screen it happens on; the last, from an ATS, shows every ATS's logo.
test("the invite section shows the four ways to invite candidates", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("#invite");
  await section.scrollIntoViewIfNeeded();

  const cards = section.getByRole("listitem");
  await expect(cards).toHaveCount(4);

  // Each card has its icon.
  for (const card of await cards.all()) {
    await expect(card.locator("svg").first()).toBeVisible();
  }

  // Every ATS shows its logo, and each loads.
  const logos = cards.nth(3).locator("img");
  await expect(logos).toHaveCount(5);
  expect(await logos.evaluateAll((items) => items.every((img) => (img as HTMLImageElement).naturalWidth > 0))).toBe(true);
  await section.screenshot({ path: test.info().outputPath("invite-section.png") });
});
