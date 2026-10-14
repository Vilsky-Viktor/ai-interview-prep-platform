import { expect, test } from "@playwright/test";

// The footer's "developer docs" opens the reference, read from the API itself, in four tabs: the
// API (how to get a key, every route with what it returns), its web hooks, the SDK that embeds
// the interview, and the objects.
test("the developer docs explain the API, web hooks, the SDK and the objects", async ({ page }) => {
  await page.goto("/");
  // The footer's link leads to the page; opened directly, so a click before the page is ready
  // can't miss it.
  await expect(page.locator("footer").getByRole("link", { name: "developer docs" })).toHaveAttribute("href", "/api-docs");
  await page.goto("/api-docs");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Developer docs");
  const tabs = page.getByRole("navigation").filter({ hasText: "Objects" });
  await expect(tabs.getByRole("link")).toHaveText(["API", "Web hooks", "SDK", "Objects"]);

  for (const title of ["getting an API key", "authentication", "rate limits and pagination", "verified companies"]) {
    await expect(page.getByRole("heading", { level: 2, name: title }).first()).toBeVisible();
  }

  // The steps to a key, as a numbered list.
  await expect(page.locator("ol").first().locator("li")).toHaveCount(5);
  // The base URL to copy and the routes.
  await expect(page.getByRole("textbox", { name: "Copy URL" })).toHaveValue(/\/api\/v1$/);
  const routes = page.locator("article").filter({ has: page.getByText(/^(GET|POST)$/) });
  await expect(routes).toHaveCount(5);
  await expect(routes.filter({ hasText: "/interviews/{interview_id}/candidates" }).first()).toBeVisible();
  await page.screenshot({ path: test.info().outputPath("api.png"), fullPage: true });

  // Links are checked, then opened directly, so a click before the page is ready can't miss.
  // A mention of the web hook opens its tab: how to check a request, and its one event.
  await expect(page.getByRole("link", { name: "web hook", exact: true })).toHaveAttribute(
    "href",
    "/api-docs?tab=webhooks",
  );
  await page.goto("/api-docs?tab=webhooks");
  await expect(page.getByText("Prepza-Signature", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("candidate.finished", { exact: true }).first()).toBeVisible();
  // A finished candidate's results never change, so nothing is sent after it.
  await expect(page.getByText("candidate.rescored", { exact: true })).toHaveCount(0);

  // The SDK: the script and how to embed the interview.
  await expect(tabs.getByRole("link", { name: "SDK" })).toHaveAttribute("href", "/api-docs?tab=sdk");
  await page.goto("/api-docs?tab=sdk");
  await expect(page.locator("pre")).toContainText("Prepza.embed(");

  // A type opens its object on the objects tab.
  await page.goto("/api-docs");
  await expect(page.getByRole("link", { name: "Candidate", exact: true }).first()).toHaveAttribute(
    "href",
    "/api-docs?tab=objects#Candidate",
  );
  await page.goto("/api-docs?tab=objects#Candidate");
  await expect(page.locator("#Candidate")).toContainText("results_url");
  await page.screenshot({ path: test.info().outputPath("objects.png"), fullPage: true });
});
