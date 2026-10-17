import { expect, test } from "@playwright/test";

// The home page's integrations section shows every ATS a company can connect and Slack, as
// their full logos, then the API and MCP as their mark and name; prepza's API as an example
// request with a link to its docs; and a point each for the ATS, the API and MCP.
test("the home page shows the ATSs, Slack, the API and MCP", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("#integrations");
  await section.scrollIntoViewIfNeeded();

  // Each logo is named for screen readers.
  for (const name of ["Workable", "Greenhouse", "Teamtailor", "Recruitee", "Breezy HR", "Slack"]) {
    await expect(section.getByRole("img", { name })).toBeVisible();
  }

  // The ATSs and Slack, then the API and MCP.
  await expect(section.locator("ul").first().locator("li")).toHaveCount(8);
  // Every logo loads, MCP's mark among them.
  const logos = section.locator("img");
  await expect(logos).toHaveCount(7);
  expect(await logos.evaluateAll((items) => items.every((img) => (img as HTMLImageElement).naturalWidth > 0))).toBe(true);
  // The API: an example request, and its docs.
  await expect(section.locator('[dir="ltr"] pre').first()).toBeVisible();
  await expect(section.locator('a[href="/api-docs"]')).toBeVisible();
  // A point each for the ATS, the API and MCP.
  await expect(section.locator("ul").last().locator("li")).toHaveCount(3);
  await section.screenshot({ path: test.info().outputPath("ats-section.png") });
  await page.emulateMedia({ colorScheme: "dark" });
  await section.screenshot({ path: test.info().outputPath("ats-section-dark.png") });
});

// Right to left, the API's row reads from the right with the docs arrow facing left; the example
// request is code, so it stays left to right.
test("the API's docs arrow follows the reading direction", async ({ page }) => {
  await page.goto("/ar");
  const section = page.locator("#integrations");
  const docs = section.locator('a[href="/api-docs"]');
  await docs.scrollIntoViewIfNeeded();

  const scale = await docs.locator("svg").evaluate((icon) => getComputedStyle(icon).scale);
  expect(scale).toBe("-1 1");
  const request = section.locator("pre").first();
  await expect(request.locator("xpath=ancestor::*[@dir][1]")).toHaveAttribute("dir", "ltr");
});
