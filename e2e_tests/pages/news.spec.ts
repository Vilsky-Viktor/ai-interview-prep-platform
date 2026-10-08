import { expect, test, type Page } from "@playwright/test";

// The news page and its RSS feed, whatever posts exist: what search engines and feed readers
// read, and the footer's link. Posts themselves are checked by the signed-in news spec.

// Requests made outside the browser go to the gateway itself (pages.sh sets REQUEST_URL).
const REQUEST_URL = process.env.REQUEST_URL ?? "http://localhost:8090";
const LANGUAGES = 23;

async function structuredData(page: Page) {
  const scripts = await page
    .locator('script[type="application/ld+json"]')
    .allTextContents();

  return scripts.flatMap((text) => [JSON.parse(text)].flat());
}

for (const [path, language, title] of [
  ["/news", "en", "prepza news"],
  ["/de/news", "de", "Neuigkeiten von prepza"],
] as const) {
  test(`${path} is indexable with its title, description, addresses, data and feed`, async ({
    page,
  }) => {
    const response = await page.goto(path);

    expect(response?.status()).toBe(200);
    expect(response?.headers()["x-robots-tag"]).toBeUndefined();
    await expect(page).toHaveTitle(`${title} · prepza.`);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(title);
    await expect(page.locator('meta[name="robots"]')).toHaveCount(0);

    const description =
      (await page
        .locator('meta[name="description"]')
        .getAttribute("content")) ?? "";
    expect(description.length).toBeGreaterThan(50);
    expect(description.length).toBeLessThanOrEqual(170);

    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute(
      "href",
      new RegExp(`${path}$`),
    );
    const alternates = page.locator('link[rel="alternate"][hreflang]');
    await expect(alternates).toHaveCount(LANGUAGES + 1);
    await expect(page.locator('link[hreflang="x-default"]')).toHaveAttribute(
      "href",
      /\/news$/,
    );
    await expect(page.locator('meta[property="og:image"]')).toHaveAttribute(
      "content",
      /\/(preview\?|opengraph-image)/,
    );

    const feed = path.replace("/news", "/news/rss.xml");
    await expect(
      page.locator('link[rel="alternate"][type="application/rss+xml"]'),
    ).toHaveAttribute("href", new RegExp(`${feed}$`));
    await expect(
      page.getByRole("link", {
        name: language === "en" ? "RSS feed" : "RSS-Feed",
      }),
    ).toHaveAttribute("href", feed);

    const blog = (await structuredData(page)).find(
      (item) => item["@type"] === "Blog",
    );
    expect(blog).toMatchObject({
      inLanguage: language,
      publisher: { name: "prepza" },
    });
    expect(Array.isArray(blog.blogPost)).toBe(true);

    for (const post of blog.blogPost) {
      expect(post).toMatchObject({
        "@type": "BlogPosting",
        inLanguage: language,
      });
      expect(post.headline).toBeTruthy();
      expect(post.datePublished).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    }
  });
}

test("the feed is RSS 2.0 in each language, its posts linking to their place on the page", async ({
  request,
}) => {
  for (const [path, language] of [
    ["/news/rss.xml", "en"],
    ["/de/news/rss.xml", "de"],
  ]) {
    const response = await request.get(`${REQUEST_URL}${path}`);

    expect(response.status(), path).toBe(200);
    expect(response.headers()["content-type"], path).toContain(
      "application/rss+xml",
    );

    const xml = await response.text();
    expect(xml).toMatch(
      /^<\?xml version="1.0" encoding="UTF-8"\?>\s*<rss version="2.0">/,
    );
    expect(xml).toContain(`<language>${language}</language>`);
    expect(xml).toMatch(
      /<channel>\s*<title>[^<]+<\/title>\s*<link>[^<]+\/news<\/link>/,
    );
    expect(xml).toMatch(/<\/channel>\s*<\/rss>\s*$/);

    for (const item of xml.match(/<item>[\s\S]*?<\/item>/g) ?? []) {
      expect(item).toMatch(/<guid isPermaLink="false">([^<]+)<\/guid>/);
      expect(item).toMatch(/<link>[^<]+\/news#[^<]+<\/link>/);
      expect(item).toMatch(
        /<pubDate>\w{3}, \d{2} \w{3} \d{4} 00:00:00 GMT<\/pubDate>/,
      );
    }
  }
});

test("the sitemap lists the news page in every language but not its feed", async ({
  request,
}) => {
  const sitemap = await (
    await request.get(`${REQUEST_URL}/sitemap.xml`)
  ).text();

  expect(sitemap).toMatch(/<loc>[^<]+\/news<\/loc>/);
  expect(sitemap).toMatch(/<loc>[^<]+\/de\/news<\/loc>/);
  expect(sitemap).not.toContain("rss.xml");
});

test("the footer links to the news page", async ({ page }) => {
  await page.goto("/");
  const link = page
    .getByRole("navigation", { name: "Footer" })
    .getByRole("link", {
      name: "News",
    });

  await expect(link).toHaveAttribute("href", "/news");
  await link.click();
  await expect(page).toHaveURL(/\/news$/);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "prepza news",
  );
});
