import { expect, test } from "@playwright/test";

// The home page offers prepza's demo videos twice: beside the promise (under it on phones) and
// at the end, between the demos and "Go to FAQ" there, "ask agent" opens the assistant. The demos
// open YouTube in a new tab.
test("the home page links to the demo videos at the top and at the end", async ({ page }) => {
  await page.goto("/");
  const demos = page.getByRole("link", { name: "Demos" }).filter({ visible: true });
  await expect(demos).toHaveCount(2);

  for (const link of await demos.all()) {
    await expect(link).toHaveAttribute("href", "https://www.youtube.com/@prepza");
    await expect(link).toHaveAttribute("target", "_blank");
    await expect(link).toHaveAttribute("rel", /noopener/);
  }

  // Hovering says where it leads.
  await demos.first().hover();
  await expect(page.getByText("Watch demos on YouTube")).toBeVisible();

  const closing = page.locator("section", {
    has: page.getByRole("heading", { name: /Ready to interview/i }),
  });
  await expect(closing.getByRole("link", { name: "Demos" })).toBeVisible();
  await expect(closing.getByRole("link", { name: /go to FAQ/i })).toBeVisible();

  // "ask agent" sits between them and opens the assistant's panel.
  const buttons = closing
    .locator("div", { has: page.getByRole("link", { name: /go to FAQ/i }) })
    .last()
    .locator("a, button");
  await expect(buttons.nth(0)).toHaveAccessibleName("Demos");
  await expect(buttons.nth(1)).toHaveAccessibleName("ask agent");
  await expect(buttons.nth(2)).toHaveAccessibleName(/go to FAQ/i);
  await buttons.nth(1).click();
  await expect(page.getByRole("dialog", { name: "Assistant" })).toBeVisible();
});
