import { expect, test } from "@playwright/test";

const DEMOS = "https://www.youtube.com/@prepza";

// The home page offers prepza's demo videos twice: beside the promise (under it on phones) and
// at the end, where "ask agent", between the demos and the FAQ, opens the assistant. The demos
// open YouTube in a new tab.
test("the home page links to the demo videos at the top and at the end", async ({
  page,
}) => {
  await page.goto("/");
  const demos = page.locator(`main a[href="${DEMOS}"]`).filter({ visible: true });
  await expect(demos).toHaveCount(2);

  for (const link of await demos.all()) {
    await expect(link).toHaveAttribute("target", "_blank");
    await expect(link).toHaveAttribute("rel", /noopener/);
  }

  // Hovering opens its tooltip (again if the first hover came before the page was ready).
  await expect(async () => {
    await page.mouse.move(0, 0);
    await demos.first().hover();
    await expect(demos.first()).toHaveAttribute("data-popup-open", {
      timeout: 2_000,
    });
  }).toPass();

  // The page's last screen: the demos, "ask agent" and the FAQ, in that order.
  const closing = page.locator("main > section").last();
  const buttons = closing.locator('div:has(> a[href="/faq"]) > *');
  await expect(buttons).toHaveCount(3);
  await expect(buttons.nth(0)).toHaveAttribute("href", DEMOS);
  await expect(buttons.nth(1)).toHaveAttribute("data-assistant-toggle");
  await expect(buttons.nth(2)).toHaveAttribute("href", "/faq");
  await buttons.nth(1).click();
  await expect(page.getByRole("dialog")).toBeVisible();
});

// Every page's footer has "ask agent" under the social icons; it opens the assistant's panel.
test("the footer's ask agent opens the assistant", async ({ page }) => {
  await page.goto("/faq");
  await page.getByRole("contentinfo").locator("[data-assistant-toggle]").click();
  await expect(page.getByRole("dialog")).toBeVisible();
});

// The agent's section shows a request with the card it prepares; its button opens the panel.
test("the agent's section shows the chat and opens the assistant", async ({
  page,
}) => {
  await page.goto("/");
  const section = page.locator("#agent");
  await expect(section.locator("[inert] textarea")).toBeVisible();
  await section.locator("[data-assistant-toggle]").click();
  await expect(page.getByRole("dialog")).toBeVisible();
});

// The preview's input types its questions one after another, each on one line.
test("the agent's preview types questions on one line", async ({ page }) => {
  // It waits through the animation, on top of the page load.
  test.slow();
  await page.goto("/");
  const input = page.locator("#agent [inert] textarea");
  await input.scrollIntoViewIfNeeded();
  const height = (await input.boundingBox())!.height;
  const seen = new Set<string>();

  // Sampled through more than one question: it types, and its height never changes.
  for (let check = 0; check < 40; check += 1) {
    seen.add(await input.inputValue());
    expect((await input.boundingBox())!.height).toBe(height);
    await page.waitForTimeout(250);
  }

  expect(seen.size).toBeGreaterThan(2);
});

// With reduced motion nothing is typed: the input shows its placeholder.
test("the agent's preview stays still with reduced motion", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const input = page.locator("#agent [inert] textarea");
  await expect(input).toHaveAttribute("placeholder", /.+/);
  await page.waitForTimeout(2_000);
  await expect(input).toHaveValue("");
});
