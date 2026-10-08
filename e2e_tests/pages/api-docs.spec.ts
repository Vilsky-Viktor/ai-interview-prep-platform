import { expect, test } from "@playwright/test";

// The footer's "api docs" opens the public API's reference, read from the API itself: how to get
// a key, every route with what it returns, the web hook and the objects.
test("the API docs explain keys, routes, the web hook and the objects", async ({ page }) => {
  await page.goto("/");
  // The footer's link leads to the page; opened directly, so a click before the page is ready
  // can't miss it.
  await expect(page.locator("footer").getByRole("link", { name: "api docs" })).toHaveAttribute("href", "/api-docs");
  await page.goto("/api-docs");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("API docs");

  for (const title of ["getting an API key", "authentication", "rate limits and pagination", "web hooks"]) {
    await expect(page.getByRole("heading", { level: 2, name: title }).first()).toBeVisible();
  }

  // The steps to a key, as a numbered list.
  await expect(page.locator("ol").first().locator("li")).toHaveCount(5);
  // The base URL to copy, and the five routes.
  await expect(page.getByRole("textbox", { name: "Copy URL" })).toHaveValue(/\/api\/v1$/);
  const routes = page.locator("article").filter({ has: page.getByText(/^(GET|POST)$/) });
  await expect(routes).toHaveCount(6);
  await expect(routes.filter({ hasText: "/interviews/{interview_id}/candidates" }).first()).toBeVisible();
  // The web hook, and the objects its types link to.
  await expect(page.getByText("candidate.finished", { exact: true }).first()).toBeVisible();
  await page.getByRole("link", { name: "Candidate", exact: true }).first().click();
  await expect(page).toHaveURL(/#Candidate$/);
  await expect(page.locator("#Candidate")).toContainText("results_url");
  await page.screenshot({ path: test.info().outputPath("api-docs.png"), fullPage: true });
});
