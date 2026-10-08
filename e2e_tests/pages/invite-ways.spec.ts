import { expect, test } from "@playwright/test";

// The home page's invite section shows the four ways candidates get an interview, each with a
// piece of the screen it happens on, and the job ad link section is gone.
test("the invite section shows the four ways to invite candidates", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("section", {
    has: page.getByRole("heading", { name: "Invite candidates four ways" }),
  });
  await section.scrollIntoViewIfNeeded();

  const cards = section.getByRole("listitem");
  await expect(cards).toHaveCount(4);
  await expect(cards.nth(0)).toContainText("By email");
  await expect(cards.nth(1)).toContainText("candidates.csv");
  await expect(cards.nth(2)).toContainText("prepza.ai/apply/");
  // Every ATS shows its logo.
  await expect(cards.nth(3)).toContainText("From your ATS");
  await expect(cards.nth(3).locator("img")).toHaveCount(5);
  await expect(page.getByRole("heading", { name: "One link for your job ad" })).toHaveCount(0);
  await section.screenshot({ path: test.info().outputPath("invite-section.png") });
});
