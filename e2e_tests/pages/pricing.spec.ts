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
  const section = page.locator("section", {
    has: page.getByRole("heading", { name: /pay per candidate/i }),
  });

  await expect(section).toContainText(
    `your first ${prices.free_candidates} candidates are free`,
  );

  for (const tier of prices.candidate_prices) {
    await expect(
      section.getByText(price(tier.cents, prices.currency), { exact: true }),
    ).toBeVisible();
  }

  const range = new Intl.NumberFormat("en", {
    style: "currency",
    currency: prices.currency,
    maximumFractionDigits: 0,
  }).formatRange(prices.candidate_cents_min / 100, prices.candidate_cents_max / 100);
  await expect(section).toContainText(`${range} per candidate`);
  // All the prices on one row on a desktop.
  await section.scrollIntoViewIfNeeded();
  await section.screenshot({ path: test.info().outputPath("pricing.png") });
});

test("the pricing page shows the catalog's free candidates", async ({ page }) => {
  const prices = await catalog(page);
  await page.goto("/pricing");

  await expect(page.locator("main")).toContainText(
    `Your first ${prices.free_candidates} candidates`,
  );
});
