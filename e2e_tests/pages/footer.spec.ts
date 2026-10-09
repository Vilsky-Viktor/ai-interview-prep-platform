import { expect, test } from "@playwright/test";

// The footer's links in three columns: the product, resources to read, and the company.
test("the footer groups its links by product, resources and company", async ({ page }) => {
  await page.goto("/faq");
  const columns = page.getByRole("contentinfo").getByRole("navigation").getByRole("list");
  await expect(columns).toHaveCount(3);
  await expect(columns.nth(0).getByRole("link")).toHaveText([
    /skills tests/i,
    /pre-employment testing/i,
    /ai interviews/i,
    /free practice/i,
    /compare/i,
  ]);
  await expect(columns.nth(1).getByRole("link")).toHaveText([
    /guides/i,
    /faq/i,
    /^docs/i,
    /api docs/i,
    /news/i,
  ]);
  await expect(columns.nth(2).getByRole("link")).toHaveText([
    /about us/i,
    /contact us/i,
    /privacy/i,
    /terms/i,
  ]);
});
