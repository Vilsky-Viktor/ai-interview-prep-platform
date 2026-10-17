import { expect, test } from "@playwright/test";

// ⌘/Ctrl+Enter pressed twice before the first send finished sends the message once.
test("a contact message sent twice quickly goes once", async ({ page }) => {
  let sent = 0;
  await page.route("**/api/rounds/help/contact", async (route) => {
    sent += 1;
    await new Promise((resolve) => setTimeout(resolve, 1500));
    await route.fulfill({ status: 204 });
  });

  await page.goto("/contact");
  const form = page.locator("main form");
  await form.locator('input[autocomplete="name"]').fill("Ann");
  await form.locator('input[type="email"]').fill("ann@example.com");
  const message = form.locator("textarea");
  await message.fill("Hello");
  await message.press("ControlOrMeta+Enter");
  await message.press("ControlOrMeta+Enter");

  // Sent: the reply goes to the address given.
  await expect(page.getByRole("status")).toContainText("ann@example.com");
  expect(sent).toBe(1);
});
