import { expect, test } from "@playwright/test";

// The home page's integrations section shows every ATS a company can connect and Slack, as
// their full logos, and prepza's API as an example request with a link to its docs.
test("the home page shows the ATSs, Slack and the API", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("section", {
    has: page.getByRole("heading", { name: "Works with your tools" }),
  });
  await section.scrollIntoViewIfNeeded();

  for (const name of ["Workable", "Greenhouse", "Teamtailor", "Recruitee", "Breezy HR", "Slack"]) {
    await expect(section.getByRole("img", { name })).toBeVisible();
  }

  // Every logo loads.
  const logos = section.locator("img");
  await expect(logos).toHaveCount(6);
  expect(await logos.evaluateAll((items) => items.every((img) => (img as HTMLImageElement).naturalWidth > 0))).toBe(true);
  // The API: an example request under its name, and its docs.
  await expect(section.getByText("prepza API")).toBeVisible();
  await expect(section.getByText("POST /api/v1/interviews/{id}/candidates", { exact: false })).toBeVisible();
  await expect(section.getByRole("button", { name: /api docs/i })).toHaveAttribute("href", "/api-docs");
  await section.screenshot({ path: test.info().outputPath("ats-section.png") });
  await page.emulateMedia({ colorScheme: "dark" });
  await section.screenshot({ path: test.info().outputPath("ats-section-dark.png") });
});
