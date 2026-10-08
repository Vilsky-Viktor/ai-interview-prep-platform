import { expect, test } from "@playwright/test";

// The home page offers prepza's demo videos twice: beside the promise (under it on phones) and
// beside "Go to FAQ" at the end. Both open YouTube in a new tab.
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
});
