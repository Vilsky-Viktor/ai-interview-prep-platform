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
    /legal docs/i,
    /developer docs/i,
    /news/i,
  ]);
  await expect(columns.nth(2).getByRole("link")).toHaveText([
    /about us/i,
    /contact us/i,
    /privacy/i,
    /terms/i,
    /accessibility/i,
  ]);
});

// The legal operator is within reach of every page: the footer names it, and the contact page
// gives its registry code, address and email.
test("the footer and the contact page name the company that runs prepza", async ({ page }) => {
  await page.goto("/contact");
  await expect(page.getByRole("contentinfo")).toContainText(
    `© ${new Date().getFullYear()} Arcolabs OÜ`
  );
  await expect(page.getByRole("main")).toContainText(
    "prepza is run by Arcolabs OÜ, registry code 17587452, Sepapaja tn 6, 15551 Tallinn, Harju maakond, Estonia. Email: hello@prepza.ai"
  );
});

// The accessibility statement: what works, what falls short, and where to write, in the
// visitor's language.
test("the accessibility statement says where to report a problem", async ({ page }) => {
  await page.goto("/accessibility");
  const main = page.getByRole("main");
  await expect(main.getByRole("heading", { level: 1 })).toHaveText(/accessibility/i);
  await expect(main.getByRole("link", { name: "hello@prepza.ai" })).toHaveAttribute(
    "href",
    "mailto:hello@prepza.ai"
  );
  await expect(main).toContainText("WCAG 2.2");

  await page.goto("/de/accessibility");
  await expect(page.getByRole("main").getByRole("heading", { level: 1 })).not.toHaveText(
    /^accessibility\.?$/i
  );
});
