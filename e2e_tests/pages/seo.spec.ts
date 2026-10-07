import { expect, test, type Page } from "@playwright/test";

// What search engines see on the public pages: addresses in every language, titles and
// structured data, the sitemap and robots.txt, redirects, and private pages kept out.

type Template = { id: string; slug: string };

// Requests made outside the browser go to the gateway itself: the container's "localhost" isn't
// the site (pages.sh sets REQUEST_URL; locally the site's address works).
const REQUEST_URL = process.env.REQUEST_URL ?? "http://localhost:8090";

async function firstTemplate(page: Page): Promise<Template> {
  const response = await page.request.get(`${REQUEST_URL}/api/library/templates?limit=1`);
  const [template] = await response.json();

  return template;
}

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
}) => {
  const template = await firstTemplate(page);
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
});

test("old addresses move to their readable ones for good", async ({ page }) => {
  const template = await firstTemplate(page);

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
}) => {
  const robots = await (await page.request.get(`${REQUEST_URL}/robots.txt`)).text();
  expect(robots).toContain("Disallow: /api/");
  expect(robots).not.toContain("Disallow: /companies");
  expect(robots).toContain("/sitemap.xml");

  const template = await firstTemplate(page);
  const sitemap = await (await page.request.get(`${REQUEST_URL}/sitemap.xml`)).text();

  for (const path of [
    "/de/pricing",
    "/tests",
    `/tests/${template.slug}`,
    `/practice/${template.slug}`,
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

  // Links inside the article stay in its language; the legal pages have one address.
  const internal = await article
    .locator('a[href^="/"]')
    .evaluateAll((links) => links.map((link) => link.getAttribute("href")));
  expect(internal.length).toBeGreaterThan(0);
  expect(
    internal.every(
      (href) =>
        href!.startsWith("/ar") || ["/privacy", "/terms", "/dpa"].includes(href!),
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
