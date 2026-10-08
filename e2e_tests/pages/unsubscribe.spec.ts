import { createHash, createHmac, randomBytes } from "node:crypto";

import { expect, test } from "@playwright/test";

// The page an email's unsubscribe link opens, signed out. Links are signed the way notifications
// signs them (services/notifications/app/helpers/unsubscribe.py) with EMAIL_LINK_SECRET, which
// pages.sh passes; e2e_tests/signed-in/helpers/unsubscribe.ts keeps the signed-in suite's copy.
function companyLink(email: string, companyId: string, company: string): string {
  const address = createHash("sha256").update(email).digest("hex");
  const payload = { type: "company", address, company_id: companyId, company };
  const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const signature = createHmac("sha256", process.env.EMAIL_LINK_SECRET ?? "local-email-link-secret")
    .update(`unsubscribe:${body}`)
    .digest("base64url");

  return `/unsubscribe?token=${body}.${signature}`;
}

test("an invalid unsubscribe link says so and isn't indexed", async ({ page }) => {
  const response = await page.goto("/unsubscribe?token=not-a-real-link");

  expect(response?.headers()["x-robots-tag"]).toBe("noindex");
  await expect(page.getByText("This unsubscribe link isn't valid.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Confirm" })).toHaveCount(0);
});

test("a candidate confirms stopping a company's emails", async ({ page }) => {
  // A made-up company and address of this run's own: nothing real is changed.
  const id = randomBytes(4).toString("hex");
  const posts: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST" && request.url().includes("/unsubscribe/")) {
      posts.push(request.url());
    }
  });

  await page.goto(companyLink(`e2e-${id}@example.com`, `e2e-${id}`, `Acme ${id}`));
  await expect(page.getByText(`You won't get emails from Acme ${id} anymore.`)).toBeVisible();
  // Opening the link changes nothing, as mail scanners open links too: only Confirm does.
  await page.waitForLoadState("networkidle");
  expect(posts).toEqual([]);

  await page.getByRole("button", { name: "Confirm" }).click();
  await expect(page.getByRole("heading", { name: /^You're unsubscribed/ })).toBeVisible();
  expect(posts).toHaveLength(1);
  await expect(page.getByText(`You won't get emails from Acme ${id} anymore.`)).toBeVisible();
});
