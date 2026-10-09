import type { Page } from "@playwright/test";

import { expect, test } from "./helpers/templates";

// What search engines see on the public pages: addresses in every language, titles and
// structured data, the sitemap and robots.txt, redirects, and private pages kept out. Template
// pages are checked on the test's own throwaway templates (helpers/templates.ts).

// Requests made outside the browser go to the gateway itself: the container's "localhost" isn't
// the site (pages.sh sets REQUEST_URL; locally the site's address works).
const REQUEST_URL = process.env.REQUEST_URL ?? "http://localhost:8090";

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

// The two ways on are links drawn as the site's buttons.
test("a role test page is for hiring, with the way to practise second", async ({
  page,
  addTemplate,
}) => {
  const template = await addTemplate();
  await page.goto(`/tests/${template.slug}`);

  await expect(page.locator("h1")).toContainText("skills test for hiring");
  await expect(
    page.getByRole("button", { name: /create a test for your candidates/i }),
  ).toHaveAttribute("href", "/");
  await expect(
    page.getByRole("button", { name: /practise it free/i }),
  ).toHaveAttribute("href", `/practice/${template.slug}`);
  const data = await page
    .locator('script[type="application/ld+json"]')
    .allTextContents();
  expect(data.join()).toContain('"@type":"BreadcrumbList"');
  // The site FAQ's answers to companies' questions, opening on a click; no FAQ data, as the
  // same answers repeat on every role page (/faq carries it).
  const faq = page.locator("section", {
    has: page.getByRole("heading", { name: /questions companies ask/i }),
  });
  await expect(faq.locator("details")).toHaveCount(5);
  await faq.getByText("How much does it cost?").click();
  await expect(faq.getByText(/credits/).first()).toBeVisible();
  expect(data.join()).not.toContain('"@type":"FAQPage"');
});

// A template's pages (role test and free practice) exist in English and in the template's
// language only: an English template's pages have no other language versions, and their
// addresses under another language aren't found.
test("a template's pages are only in English and its template's language", async ({
  page,
  addTemplate,
}) => {
  const template = await addTemplate();

  for (const base of ["/tests", "/practice"]) {
    await page.goto(`${base}/${template.slug}`);
    await expect(page.locator('head link[rel="alternate"][hreflang]')).toHaveCount(0);
    const other = await page.request.get(`${REQUEST_URL}/de${base}/${template.slug}`);
    expect(other.status()).toBe(404);
  }
});

test("old addresses move to their readable ones for good", async ({ page, addTemplate }) => {
  const template = await addTemplate();

  const practice = await page.request.get(`${REQUEST_URL}/practice/${template.id}`, {
    maxRedirects: 0,
  });
  expect(practice.status()).toBe(308);
  expect(practice.headers().location).toBe(`/practice/${template.slug}`);

  const companies = await page.request.get(`${REQUEST_URL}/company/abc/interviews`, {
    maxRedirects: 0,
  });
  expect(companies.status()).toBe(308);
  expect(companies.headers().location).toBe("/companies/abc/interviews");
});

test("private pages say noindex; public ones don't", async ({ page }) => {
  const privatePage = await page.request.get(`${REQUEST_URL}/companies`);
  const publicPage = await page.request.get(`${REQUEST_URL}/pricing`);

  expect(privatePage.headers()["x-robots-tag"]).toBe("noindex");
  expect(publicPage.headers()["x-robots-tag"]).toBeUndefined();
});

test("robots.txt and the sitemap list what should be found", async ({
  page,
  addTemplate,
}) => {
  const full = await addTemplate("en", 3);
  const thin = await addTemplate("en", 1);
  const robots = await (await page.request.get(`${REQUEST_URL}/robots.txt`)).text();
  expect(robots).toContain("Disallow: /api/");
  expect(robots).not.toContain("Disallow: /companies");
  expect(robots).toContain("/sitemap.xml");

  const sitemap = await (await page.request.get(`${REQUEST_URL}/sitemap.xml`)).text();

  // Only the templates the API calls indexable (enough topics, not a near-duplicate).
  for (const [template, indexable] of [
    [full, true],
    [thin, false],
  ] as const) {
    for (const base of ["/tests", "/practice"]) {
      const listed = sitemap.includes(`${base}/${template.slug}</loc>`);
      expect(listed, `${base}/${template.slug}`).toBe(indexable);
    }
  }

  for (const path of [
    "/de/pricing",
    "/tests",
    "/compare/testgorilla",
    "/guides/hiring-engineers",
    "/pre-employment-testing",
    "/de/guides/hiring-engineers",
    "/ja/compare/testgorilla",
  ]) {
    expect(sitemap).toContain(`${path}</loc>`);
  }

  expect(sitemap).toContain('hreflang="x-default"');
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

// A template the API doesn't call indexable (too few topics, or a near-duplicate) keeps its pages
// out of search results; an indexable one doesn't.
test("only an indexable template's pages may be found", async ({ page, addTemplate }) => {
  const thin = await addTemplate("en", 1);
  const full = await addTemplate("en", 3);

  for (const [template, robots] of [
    [thin, "noindex"],
    [full, null],
  ] as const) {
    for (const base of ["/tests", "/practice"]) {
      await page.goto(`${base}/${template.slug}`);
      // Read at once: an indexable page has no robots tag to wait for.
      const meta = await page
        .locator('head meta[name="robots"]')
        .evaluateAll((tags) => tags.map((tag) => tag.getAttribute("content")).join());
      expect(meta.includes("noindex") ? "noindex" : null).toBe(robots);
    }
  }
});

// A template in another language has its pages at that language's address too: their links,
// back to the list, to the home page and between its two pages, stay in it, and the level is
// in the page's language.
test("a template's page in its language keeps its links and level in it", async ({
  page,
  addTemplate,
}) => {
  const template = await addTemplate("de");

  await page.goto(`/de/tests/${template.slug}`);
  await expect(page.locator("h1")).toContainText("Test für Bewerber");
  await expect(page.locator('main a[aria-label="Einstellungstests nach Rolle"]')).toHaveAttribute(
    "href",
    "/de/tests",
  );
  await expect(
    page.getByRole("button", { name: /test für deine kandidaten erstellen/i }),
  ).toHaveAttribute("href", "/de");
  await expect(page.getByRole("button", { name: /kostenlos üben/i })).toHaveAttribute(
    "href",
    `/de/practice/${template.slug}`,
  );
  await expect(page.getByText(/^(grundlegend|mittel|schwer)$/)).toBeVisible();

  await page.goto("/de/tests");
  await expect(page.locator(`a[href="/de/tests/${template.slug}"]`)).toHaveCount(1);
});
