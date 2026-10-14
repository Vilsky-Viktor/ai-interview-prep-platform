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
  await page.getByRole("textbox", { name: "Name" }).fill("Ann");
  await page.getByRole("textbox", { name: "Email" }).fill("ann@example.com");
  const message = page.getByRole("textbox", { name: "Message" });
  await message.fill("Hello");
  await message.press("ControlOrMeta+Enter");
  await message.press("ControlOrMeta+Enter");

  await expect(page.getByRole("status")).toBeVisible();
  expect(sent).toBe(1);
});
