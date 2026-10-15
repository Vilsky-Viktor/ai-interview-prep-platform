import { expect, test } from "@playwright/test";

// The error page's "Report": a dialog with a text field, sent to Sentry with the error.
test("the error page reports what the user was doing", async ({ page }) => {
  // An invite whose company isn't text: the page can't render it.
  await page.route("**/api/companies/invites/e2e-error-report", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ company: { broken: true }, title: "Broken", status: "invited" }),
    }),
  );

  await page.goto("/invite/e2e-error-report");
  await expect(page.getByRole("heading", { name: "Something went wrong" })).toBeVisible();
  await page.screenshot({ path: test.info().outputPath("error-page.png") });

  await page.getByRole("button", { name: "Report" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByRole("button", { name: "Send" })).toBeDisabled();
  await dialog.getByRole("textbox").fill("Opened my invite from the email.");
  await page.waitForTimeout(400);
  await page.screenshot({ path: test.info().outputPath("report-dialog.png") });
  await dialog.getByRole("button", { name: "Send" }).click();
  await expect(page.getByText("Thanks, we got it.")).toBeVisible();
  await expect(dialog).toHaveCount(0);
});

// Retry reads the page again: once what broke it is fixed, the page shows.
test("Retry on the error page shows the page once it can be shown", async ({ page }) => {
  let broken = true;
  await page.route("**/api/companies/invites/e2e-error-retry", (route) =>
    broken
      ? route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ company: { broken: true }, title: "Broken", status: "invited" }),
        })
      : route.fulfill({ status: 404, json: { detail: "Invite not found" } }),
  );

  await page.goto("/invite/e2e-error-retry");
  await expect(page.getByRole("heading", { name: "Something went wrong" })).toBeVisible();
  broken = false;
  // A click before the page is interactive is lost, so it's repeated until the page shows.
  await expect(async () => {
    await page.getByRole("button", { name: "Try again" }).click({ timeout: 2000 });
    await expect(page.getByText("This invite isn't valid anymore.")).toBeVisible({ timeout: 2000 });
  }).toPass();
});
