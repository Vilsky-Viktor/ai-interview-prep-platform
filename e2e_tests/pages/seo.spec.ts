import { expect, type Page, test } from "@playwright/test";

import { REQUEST_URL } from "./helpers/env";

// What search engines see on the public pages: addresses in every language, titles and
// structured data, redirects, and private pages kept out. The template pages, the sitemap and
// robots.txt are in seo-templates.spec.ts.

function head(page: Page, selector: string, attribute: string) {
  return page.locator(`head ${selector}`).first().getAttribute(attribute);
}

test("a page in another language has its own address, language and alternates", async ({
  page,
}) => {
  await page.goto("/de/pricing");

  await expect(page.locator("html")).toHaveAttribute("lang", "de");
  expect(await head(page, 'link[rel="canonical"]', "href")).toMatch(
    /\/de\/pricing$/,
  );
  // Every language and the default.
  await expect(page.locator('head link[rel="alternate"][hreflang]')).toHaveCount(
    24,
  );
  expect(
    await head(page, 'link[rel="alternate"][hreflang="x-default"]', "href"),
  ).toMatch(/\/pricing$/);
});

// A plain address is the English page whatever the browser's language, as its canonical and
// hreflang say; the language's own address has its version.
test("a page's plain address is in English for any browser language", async ({
  page,
}) => {
  await page.setExtraHTTPHeaders({ "Accept-Language": "de" });
  await page.goto("/pricing");

  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page.locator("h1")).toContainText(/pricing|price/i);
});

// Each language's titles use the words its employers search for (internal_docs/seo-plan.md), not a
// translation of the English ones: German companies search "Einstellungstest".
test("a language's home page is titled with its own search terms", async ({
  page,
}) => {
  await page.goto("/de");

  await expect(page).toHaveTitle(/^Einstellungstest /);
  expect(await head(page, 'meta[name="description"]', "content")).toContain(
    "Einstellungstest",
  );
});

test("the home page has a title, a description, a preview image and its company data", async ({
  page,
}) => {
  await page.goto("/");

  await expect(page).toHaveTitle(/· prepza\.$/);
  expect(await head(page, 'meta[name="description"]', "content")).toBeTruthy();
  expect(await head(page, 'meta[property="og:image"]', "content")).toBeTruthy();
  const data = await page
    .locator('script[type="application/ld+json"]')
    .allTextContents();
  expect(data.join()).toContain('"@type":"Organization"');

  const image = await page.request.get(`${REQUEST_URL}/opengraph-image`);
  expect(image.headers()["content-type"]).toBe("image/png");
});

// Every page's preview is the logo over its own title, in its language; the languages the
// picture can't draw keep the site's own.
test("each page's preview image shows its own title", async ({ page }) => {
  await page.goto("/de/pricing");
  const own = new URL(
    (await head(page, 'meta[property="og:image"]', "content")) ?? "",
  );

  expect(own.pathname).toBe("/preview");
  expect(own.searchParams.get("title")).toBe("preise");
  expect(own.searchParams.get("lang")).toBe("de");
  const image = await page.request.get(`${REQUEST_URL}/preview${own.search}`);
  expect(image.status()).toBe(200);
  expect(image.headers()["content-type"]).toBe("image/png");

  await page.goto("/ar/pricing");
  const fallback = new URL(
    (await head(page, 'meta[property="og:image"]', "content")) ?? "",
  );
  expect(fallback.pathname).toBe("/opengraph-image");
});

test("private pages say noindex; public ones don't", async ({ page }) => {
  const privatePage = await page.request.get(`${REQUEST_URL}/companies`);
  const publicPage = await page.request.get(`${REQUEST_URL}/pricing`);

  expect(privatePage.headers()["x-robots-tag"]).toBe("noindex");
  expect(publicPage.headers()["x-robots-tag"]).toBeUndefined();
});

test("the footer has three columns of links and the social icons", async ({
  page,
}) => {
  await page.goto("/pricing");
  const footer = page.locator("footer");

  await expect(footer.locator("nav ul")).toHaveCount(3);
  await expect(footer.locator("nav ul").first().locator("a")).toHaveCount(5);

  for (const name of ["LinkedIn", "X", "YouTube", "Facebook"]) {
    await expect(footer.getByRole("img", { name, exact: true })).toBeVisible();
  }
});

test("a translated article has its own address, language, direction and alternates", async ({
  page,
}) => {
  await page.goto("/ar/compare/testgorilla");

  const article = page.locator("article");
  await expect(article).toHaveAttribute("lang", "ar");
  await expect(article).toHaveAttribute("dir", "rtl");
  expect(await head(page, 'link[rel="canonical"]', "href")).toMatch(
    /\/ar\/compare\/testgorilla$/,
  );
  // Only the languages it's written in, and the default.
  const alternates = page.locator('head link[rel="alternate"][hreflang]');
  await expect(alternates).not.toHaveCount(0);
  expect(
    await head(page, 'link[rel="alternate"][hreflang="de"]', "href"),
  ).toMatch(/\/de\/compare\/testgorilla$/);

  // Links inside the article stay in its language; the legal pages and the API docs have one
  // address.
  const internal = await article
    .locator('a[href^="/"]')
    .evaluateAll((links) => links.map((link) => link.getAttribute("href")));
  expect(internal.length).toBeGreaterThan(0);
  expect(
    internal.every(
      (href) =>
        href!.startsWith("/ar") ||
        ["/privacy", "/terms", "/dpa", "/api-docs"].includes(href!),
    ),
  ).toBe(true);
});

test("links on a page in another language stay in it", async ({ page }) => {
  await page.goto("/de/pricing");
  const footer = page.locator("footer");

  await expect(footer.getByRole("link", { name: /faq/i })).toHaveAttribute(
    "href",
    "/de/faq",
  );
  // A page without language versions keeps its one address.
  await expect(
    footer.locator('a[href="/privacy"]'),
  ).toHaveCount(1);
});
