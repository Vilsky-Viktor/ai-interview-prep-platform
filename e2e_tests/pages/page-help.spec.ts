import { expect, test } from "@playwright/test";

// The home page's info button, beside the demos (under the promise on phones), explains how
// prepza works in a dialog that closes again.
test("the home page's info button explains how prepza works", async ({ page }) => {
  // The local dev server compiles the home page on first open.
  test.setTimeout(120_000);
  await page.goto("/");
  const button = page.getByRole("button", { name: "About this page" }).filter({ visible: true });
  await expect(button).toHaveCount(1);

  // Hovering names it (again if the first hover came before the page was ready).
  await expect(async () => {
    await page.mouse.move(0, 0);
    await button.hover();
    await expect(page.getByText("About this page", { exact: true })).toBeVisible({ timeout: 2_000 });
  }).toPass();

  await button.click();
  const dialog = page.getByRole("dialog", { name: "How prepza works" });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByText(/Paste the job description/)).toBeVisible();
  await expect(dialog.getByText(/\$1–3 per candidate/)).toBeVisible();

  await dialog.getByRole("button", { name: "Close" }).click();
  await expect(dialog).toBeHidden();
});
