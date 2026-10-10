import { expect, test } from "@playwright/test";

// The page an AI app sends a user to, to allow it the use of their account, signed out. Without
// a request it says the link expired; with one it asks to sign in first. It's never indexed.
test("the AI app consent page without a request says the link expired", async ({ page }) => {
  const response = await page.goto("/connect");

  expect(response?.headers()["x-robots-tag"]).toBe("noindex");
  await expect(
    page.getByText("This link has expired or was already used.", { exact: false }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Sign in to continue" })).toHaveCount(0);
});

test("the AI app consent page asks to sign in first", async ({ page }) => {
  // The API tells the request's app only to a signed-in user.
  const response = await page.goto("/connect?request=e2e-unknown");

  expect(response?.headers()["x-robots-tag"]).toBe("noindex");
  await expect(page.getByRole("heading", { name: "Connect an AI app to prepza" })).toBeVisible();
  await expect(
    page.getByText("Sign in to choose whether it can use your prepza account."),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign in to continue" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
});

// When the API names the app before sign-in (answered here in the browser), the title says
// which app asks.
test("the AI app consent page names the app that asks", async ({ page }) => {
  await page.route("**/assistant/connect/e2e-request", (route) =>
    route.fulfill({
      json: { client_name: "E2E App", redirect_host: "e2e.example.com", known_client: true },
    }),
  );
  await page.goto("/connect?request=e2e-request");

  await expect(page.getByRole("heading", { name: "Connect E2E App to prepza" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Sign in to continue" })).toBeVisible();
});
