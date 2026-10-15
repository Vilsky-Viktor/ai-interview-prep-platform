import { expect, test } from "@playwright/test";

// Every published version of a legal document stays readable, and each says whether it applies.
test("the terms show when they apply and keep every earlier version", async ({ page }) => {
  await page.goto("/terms");
  // Dates as the language writes them, not as the API names them.
  await expect(page.getByText(/^In force since [A-Z][a-z]{2} \d{1,2}, \d{4}$/)).toBeVisible();
  await expect(page.getByRole("heading", { name: "All versions" })).toBeVisible();
  await page.screenshot({ path: test.info().outputPath("terms.png"), fullPage: true });

  await page.getByRole("link", { name: "Oct 10, 2026" }).click();
  await expect(page).toHaveURL(/\/terms\?version=2026-10-10$/);
  await expect(page.getByText("This version applied from Oct 10, 2026 and has been replaced.")).toBeVisible();
  await page.screenshot({ path: test.info().outputPath("terms-old.png") });

  await page.getByRole("link", { name: "Read the version in force now" }).click();
  await expect(page).toHaveURL(/\/terms$/);
});

// Each document in the page's language, saying the English is binding, with a link to it.
test("the terms show in the page's language with a link to the binding English", async ({ page, baseURL }) => {
  await page.context().addCookies([{ name: "prepza_locale", value: "de", url: baseURL! }]);
  await page.goto("/terms");
  await expect(page.getByText("Dies ist eine Übersetzung; verbindlich ist nur die englische Fassung.")).toBeVisible();
  const text = page.locator("main div[lang]");
  await expect(text).toHaveAttribute("lang", "de");
  await expect(page.getByText(/Gültig seit \d{2}\.\d{2}\.\d{4}/)).toBeVisible();
  await page.screenshot({ path: test.info().outputPath("terms-de.png") });

  await page.getByRole("link", { name: "Auf Englisch lesen" }).click();
  await expect(page).toHaveURL(/\/terms\?language=en$/);
  await expect(text).toHaveAttribute("lang", "en");

  await page.context().addCookies([{ name: "prepza_locale", value: "ar", url: baseURL! }]);
  await page.goto("/privacy");
  await expect(text).toHaveAttribute("dir", "rtl");
  await page.screenshot({ path: test.info().outputPath("privacy-ar.png") });
});
