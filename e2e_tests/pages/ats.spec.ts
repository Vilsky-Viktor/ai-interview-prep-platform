import { expect, test } from "@playwright/test";

// The home page's integrations section shows every ATS a company can connect, and Slack, as
// their full logos.
test("the home page shows the five ATS integrations and Slack", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("section", {
    has: page.getByRole("heading", { name: "Works with your ATS and Slack" }),
  });
  await section.scrollIntoViewIfNeeded();

  for (const name of ["Workable", "Greenhouse", "Teamtailor", "Recruitee", "Breezy HR", "Slack"]) {
    await expect(section.getByRole("img", { name })).toBeVisible();
  }

  // Every logo loads.
  const logos = section.locator("img");
  await expect(logos).toHaveCount(6);
  expect(await logos.evaluateAll((items) => items.every((img) => (img as HTMLImageElement).naturalWidth > 0))).toBe(true);
  // The acronym and Slack's name keep their capitals in the lowercase title.
  await expect(section.getByRole("heading").locator("span.normal-case")).toHaveText(["ATS", "Slack"]);
  await section.screenshot({ path: test.info().outputPath("ats-section.png") });
  await page.emulateMedia({ colorScheme: "dark" });
  await section.screenshot({ path: test.info().outputPath("ats-section-dark.png") });
});
