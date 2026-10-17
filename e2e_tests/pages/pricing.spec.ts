import { expect, test } from "@playwright/test";

import { REQUEST_URL } from "./helpers/env";

// Prices and the free candidates are shown exactly as billing's catalog gives them.

type Catalog = {
  currency: string;
  candidate_prices: { cents: number }[];
  candidate_cents_min: number;
  candidate_cents_max: number;
  free_candidates: number;
};

async function catalog(page: import("@playwright/test").Page) {
  const response = await page.request.get(`${REQUEST_URL}/api/billing/catalog`);

  return (await response.json()) as Catalog;
}

function price(cents: number, currency: string) {
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency,
    maximumFractionDigits: cents % 100 === 0 ? 0 : 2,
  }).format(cents / 100);
}

test("the home page's pricing shows the catalog's prices and free candidates", async ({
  page,
}) => {
  const prices = await catalog(page);
  await page.goto("/");
  const section = page.locator("#pricing");

  // The free candidates in the section's text.
  await expect(section.locator("p").first()).toContainText(String(prices.free_candidates));
  // A card per tier, its price first.
  const tiers = section.locator("ul > li");
  await expect(tiers).toHaveCount(prices.candidate_prices.length);

  for (const [index, tier] of prices.candidate_prices.entries()) {
    await expect(tiers.nth(index).locator("p").first()).toHaveText(
      price(tier.cents, prices.currency),
    );
  }

  const range = new Intl.NumberFormat("en", {
    style: "currency",
    currency: prices.currency,
    maximumFractionDigits: 0,
  }).formatRange(prices.candidate_cents_min / 100, prices.candidate_cents_max / 100);
  await expect(section).toContainText(range);
  // All the prices on one row on a desktop.
  await section.scrollIntoViewIfNeeded();
  await section.screenshot({ path: test.info().outputPath("pricing.png") });
});

test("the pricing page shows the catalog's free candidates", async ({ page }) => {
  const prices = await catalog(page);
  await page.goto("/pricing");

  // The price list's second row: the free candidates a new company gets.
  await expect(page.locator("main ul").first().locator("li").nth(1)).toContainText(
    String(prices.free_candidates),
  );
});
