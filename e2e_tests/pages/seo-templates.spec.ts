import { REQUEST_URL } from "./helpers/env";
import { expect, test } from "./helpers/templates";

// What search engines see of the template pages, the sitemap and robots.txt, checked on the
// test's own throwaway templates (helpers/templates.ts).

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
