import { expect, test } from "@playwright/test";

// The home page offers prepza's demo videos twice: beside the promise (under it on phones) and
// at the end, between the demos and "Go to FAQ" there, "ask agent" opens the assistant. The demos
// open YouTube in a new tab.
test("the home page links to the demo videos at the top and at the end", async ({
  page,
}) => {
  await page.goto("/");
  const demos = page
    .getByRole("link", { name: "Demos" })
    .filter({ visible: true });
  await expect(demos).toHaveCount(2);

  for (const link of await demos.all()) {
    await expect(link).toHaveAttribute(
      "href",
      "https://www.youtube.com/@prepza",
    );
    await expect(link).toHaveAttribute("target", "_blank");
    await expect(link).toHaveAttribute("rel", /noopener/);
  }

  // Hovering says where it leads (again if the first hover came before the page was ready).
  await expect(async () => {
    await page.mouse.move(0, 0);
    await demos.first().hover();
    await expect(page.getByText("Watch demos on YouTube")).toBeVisible({
      timeout: 2_000,
    });
  }).toPass();

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

// Every page's footer has "ask agent" under the social icons; it opens the assistant's panel.
test("the footer's ask agent opens the assistant", async ({ page }) => {
  await page.goto("/faq");
  await page
    .getByRole("contentinfo")
    .getByRole("button", { name: "ask agent" })
    .click();
  await expect(page.getByRole("dialog", { name: "Assistant" })).toBeVisible();
});

// The agent's section shows a request with the card it prepares; its button opens the panel.
test("the agent's section shows the chat and opens the assistant", async ({
  page,
}) => {
  await page.goto("/");
  const section = page.locator("section", {
    has: page.getByRole("heading", { name: /ask the agent/i }),
  });
  await expect(section.getByText("Invite a candidate")).toBeVisible();
  await expect(
    section.getByText("Every page has a dedicated help icon"),
  ).toBeVisible();
  await section.getByRole("button", { name: "ask agent" }).click();
  await expect(page.getByRole("dialog", { name: "Assistant" })).toBeVisible();
});

// The preview's input types its questions one after another, each on one line: the whole question
// where it fits, its end where it doesn't (on a phone, before the buttons).
test("the agent's preview types questions on one line", async ({ page }) => {
  // It waits through the animation, on top of the page load.
  test.slow();
  await page.goto("/");
  const input = page.locator("[inert] textarea");
  await input.scrollIntoViewIfNeeded();
  const height = (await input.boundingBox())!.height;

  for (const question of [
    "Who scored best on Architect?",
    "Create an interview for a data analyst",
  ]) {
    // Held whole for a moment once typed: its end, the longest that fits, shows then.
    await expect
      .poll(
        async () => {
          const value = await input.inputValue();

          return value.length > 8 && question.endsWith(value);
        },
        { timeout: 15_000 },
      )
      .toBe(true);
    expect((await input.boundingBox())!.height).toBe(height);
  }
});

// With reduced motion nothing is typed: the input shows its placeholder.
test("the agent's preview stays still with reduced motion", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const input = page.locator("[inert] textarea");
  await expect(input).toHaveAttribute("placeholder", "ask anything…");
  await page.waitForTimeout(2_000);
  await expect(input).toHaveValue("");
});
