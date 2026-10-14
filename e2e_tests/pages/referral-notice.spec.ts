import { expect, test } from "@playwright/test";

const KEPT = "prepza_ref";

async function referral(page) {
  return (await page.context().cookies()).find((cookie) => cookie.name === KEPT);
}

// A referral link is kept only once the visitor agrees (EU cookie consent).
test("a referral link asks before it's kept in a cookie", async ({ page }) => {
  await page.goto("/?ref=e2eRef01");
  await expect(page.getByText("You came through a referral link")).toBeVisible();
  expect(await referral(page)).toBeUndefined();
  await page.screenshot({ path: test.info().outputPath("referral-notice.png") });

  await page.getByRole("button", { name: "Keep" }).click();
  expect((await referral(page))?.value).toBe("e2eRef01");

  // Kept: not asked again.
  await page.goto("/?ref=e2eRef01");
  await page.waitForTimeout(1_000);
  await expect(page.getByText("You came through a referral link")).toHaveCount(0);
});

test("turning a referral link down keeps nothing", async ({ page }) => {
  await page.goto("/?ref=e2eRef02");
  await page.getByRole("button", { name: "No thanks" }).click();
  expect(await referral(page)).toBeUndefined();

  // A code that doesn't read right isn't offered.
  await page.goto("/?ref=bad!");
  await page.waitForTimeout(1_000);
  await expect(page.getByText("You came through a referral link")).toHaveCount(0);
});
