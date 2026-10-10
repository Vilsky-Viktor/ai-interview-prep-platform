import { expect, test } from "@playwright/test";

// The home page's integrations section shows every ATS a company can connect and Slack, as
// their full logos, then the API and MCP as their mark and name; prepza's API as an example
// request with a link to its docs; and a point each for the ATS, the API and MCP.
test("the home page shows the ATSs, Slack, the API and MCP", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("section", {
    has: page.getByRole("heading", { name: "Works with your tools" }),
  });
  await section.scrollIntoViewIfNeeded();

  for (const name of ["Workable", "Greenhouse", "Teamtailor", "Recruitee", "Breezy HR", "Slack"]) {
    await expect(section.getByRole("img", { name })).toBeVisible();
  }

  for (const name of ["API", "MCP"]) {
    await expect(section.getByText(name, { exact: true })).toBeVisible();
  }

  // Every logo loads, MCP's mark among them.
  const logos = section.locator("img");
  await expect(logos).toHaveCount(7);
  expect(await logos.evaluateAll((items) => items.every((img) => (img as HTMLImageElement).naturalWidth > 0))).toBe(true);
  // The API: an example request under its name, and its docs.
  await expect(section.getByText("prepza API")).toBeVisible();
  await expect(section.getByText("POST /api/v1/interviews/{id}/candidates", { exact: false })).toBeVisible();
  await expect(section.getByRole("button", { name: /api docs/i })).toHaveAttribute("href", "/api-docs");
  const points = section.getByRole("listitem").filter({ hasText: /^Your / });
  await expect(points).toHaveText([/^Your ATS:/, /^Your platform:.*API/, /^Your AI chat:.*MCP/]);
  await section.screenshot({ path: test.info().outputPath("ats-section.png") });
  await page.emulateMedia({ colorScheme: "dark" });
  await section.screenshot({ path: test.info().outputPath("ats-section-dark.png") });
});

// Right to left, the API's row reads from the right with the docs arrow facing left; the example
// request is code, so it stays left to right.
test("the API's docs arrow follows the reading direction", async ({ page }) => {
  await page.goto("/ar");
  const docs = page.locator('main a[href="/api-docs"]');
  await docs.scrollIntoViewIfNeeded();

  const scale = await docs.locator("svg").evaluate((icon) => getComputedStyle(icon).scale);
  expect(scale).toBe("-1 1");
  const request = page.getByText("POST /api/v1/interviews/{id}/candidates", { exact: false });
  await expect(request.locator("xpath=ancestor::*[@dir][1]")).toHaveAttribute("dir", "ltr");
});
