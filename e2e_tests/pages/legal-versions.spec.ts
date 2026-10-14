import { expect, test } from "@playwright/test";

// Every published version of a legal document stays readable, and each says whether it applies.
test("the terms show when they apply and keep every earlier version", async ({ page }) => {
  await page.goto("/terms");
  await expect(page.getByText(/^In force since \d{4}-\d{2}-\d{2}$/)).toBeVisible();
  await expect(page.getByRole("heading", { name: "All versions" })).toBeVisible();
  await page.screenshot({ path: test.info().outputPath("terms.png"), fullPage: true });

  await page.getByRole("link", { name: "2026-10-10" }).click();
  await expect(page).toHaveURL(/\/terms\?version=2026-10-10$/);
  await expect(page.getByText("This version applied from 2026-10-10 and has been replaced.")).toBeVisible();
  await page.screenshot({ path: test.info().outputPath("terms-old.png") });

  await page.getByRole("link", { name: "Read the version in force now" }).click();
  await expect(page).toHaveURL(/\/terms$/);
});
