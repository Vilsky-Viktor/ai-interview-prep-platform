import { expect, test, type Page } from "@playwright/test";

// What search engines and link previews read beyond seo.spec.ts: each page's own description,
// template pages' breadcrumbs and text direction, articles' data, and the preview picture.

type Template = { slug: string; language: string; title: string };

// Requests made outside the browser go to the gateway itself (pages.sh sets REQUEST_URL).
const REQUEST_URL = process.env.REQUEST_URL ?? "http://localhost:8090";

// Written right to left: their lists of topics and questions mirror.
const RTL = ["ar", "he", "fa"];

function description(page: Page) {
  return page
    .locator('head meta[name="description"]')
    .first()
    .getAttribute("content");
}

async function structuredData(page: Page) {
  const scripts = await page
    .locator('script[type="application/ld+json"]')
    .allTextContents();

  return scripts.flatMap((text) => [JSON.parse(text)].flat());
}

test("the FAQ, pricing and about pages have their own descriptions", async ({
  page,
}) => {
  for (const path of ["/faq", "/pricing", "/about"]) {
    await page.goto(path);
    const intro = await page
      .locator("main header p, main p")
      .first()
      .textContent();
    const text = (await description(page)) ?? "";

    expect(text.length, path).toBeGreaterThan(100);
    expect(text.length, path).toBeLessThanOrEqual(170);
    expect(text, path).not.toBe(intro);
  }
});

test("the compare hub's title doesn't repeat the site's name", async ({
  page,
}) => {
  await page.goto("/compare");

  await expect(page).toHaveTitle(
    "Pre-employment testing tools compared · prepza.",
  );
});

test("the FAQ page's structured data lists its questions", async ({ page }) => {
  await page.goto("/faq");
  const faq = (await structuredData(page)).find(
    (item) => item["@type"] === "FAQPage",
  );

  expect(faq.mainEntity.length).toBeGreaterThan(0);
});

test("an article names its picture, language and date, and shows the date as words", async ({
  page,
}) => {
  await page.goto("/de/guides/hiring-engineers");
  const article = (await structuredData(page)).find(
    (item) => item["@type"] === "Article",
  );
  const picture = await page
    .locator('head meta[property="og:image"]')
    .first()
    .getAttribute("content");

  expect(article.inLanguage).toBe("de");
  expect(article.image).toBe(picture);
  expect(article.dateModified).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  // The German date, not the ISO one.
  const date = page.locator("main header time");
  await expect(date).toHaveAttribute("datetime", article.dateModified);
  await expect(date).toHaveText(/^\d{2}\.\d{2}\.\d{4}$/);
});

test("a free practice page has breadcrumbs, and template text has its direction", async ({
  page,
}) => {
  const response = await page.request.get(
    `${REQUEST_URL}/api/library/templates?limit=1`,
  );
  const [template]: Template[] = await response.json();
  const direction = RTL.includes(template.language) ? "rtl" : "ltr";

  await page.goto(`/practice/${template.slug}`);
  const crumbs = (await structuredData(page)).find(
    (item) => item["@type"] === "BreadcrumbList",
  );
  expect(
    crumbs.itemListElement.map(
      (step: { item: string }) => new URL(step.item).pathname,
    ),
  ).toEqual(["/", "/practice", `/practice/${template.slug}`]);
  expect(crumbs.itemListElement[2].name).toBe(template.title);

  for (const base of ["/practice", "/tests"]) {
    await page.goto(`${base}/${template.slug}`);
    const topics = page.locator("main ul[lang]").first();
    await expect(topics).toHaveAttribute("lang", template.language);
    await expect(topics).toHaveAttribute("dir", direction);
  }
});

test("the preview picture draws only signed titles, and is kept out of image search", async ({
  page,
}) => {
  // The pricing page names its own picture, signed; the same address with another title isn't.
  await page.goto("/pricing");
  const named = new URL(
    (await page.locator('meta[property="og:image"]').getAttribute("content")) ?? "",
  );
  expect(named.pathname).toBe("/preview");
  expect(named.searchParams.get("sig")).toMatch(/^[0-9a-f]{32}$/);
  const image = await page.request.get(`${REQUEST_URL}${named.pathname}${named.search}`);
  named.searchParams.set("title", "Anything someone else wrote");
  const forged = await page.request.get(`${REQUEST_URL}${named.pathname}${named.search}`);
  const robots = await (
    await page.request.get(`${REQUEST_URL}/robots.txt`)
  ).text();

  expect(image.status()).toBe(200);
  expect(image.headers()["x-robots-tag"]).toBe("noindex");
  expect(forged.status()).toBe(404);
  expect(robots).not.toContain("Disallow: /preview");
});

test("the footer's menu is named as the footer, and its icons aren't links", async ({
  page,
}) => {
  await page.goto("/pricing");
  const footer = page.locator("footer");

  await expect(
    footer.getByRole("navigation", { name: "Footer" }),
  ).toBeVisible();
  await expect(
    footer.getByRole("img", { name: "LinkedIn" }).locator("xpath=ancestor::a"),
  ).toHaveCount(0);
});
