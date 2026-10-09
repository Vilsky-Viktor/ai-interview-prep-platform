import { expect, test } from "@playwright/test";

// How the public pages fit a phone: wider previews, a centered footer in one column, popups
// across the screen, no keyboard hint on a touch screen. Desktop keeps its layout.

const isPhone = (name: string) => name === "phone";

// The home page's title: its two lines close together, as on desktop.
test("the home page's title lines sit close together", async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto("/");
  const title = page.locator("h1");
  const [lineHeight, fontSize] = await title.evaluate((element) => {
    const style = getComputedStyle(element);

    return [parseFloat(style.lineHeight), parseFloat(style.fontSize)];
  });
  expect(lineHeight).toBe(fontSize);
});

// On phones the previews' gray panels reach the screen's edges, with square corners.
test("the previews' panels span a phone's width", async ({ page }, info) => {
  test.setTimeout(120_000);
  await page.goto("/");
  const width = page.viewportSize()!.width;
  const boxes = await page
    .locator("div.bg-muted\\/60")
    .evaluateAll((elements) =>
      elements.map((element) => {
        const box = element.getBoundingClientRect();

        return {
          left: Math.round(box.left),
          width: Math.round(box.width),
          radius: getComputedStyle(element).borderTopLeftRadius,
        };
      }),
    );
  expect(boxes.length).toBeGreaterThan(0);

  for (const box of boxes) {
    if (isPhone(info.project.name)) {
      expect(box).toEqual({ left: 0, width, radius: "0px" });
    } else {
      expect(box.left).toBeGreaterThan(0);
      expect(box.radius).not.toBe("0px");
    }
  }
});

// The demos keep the room of their tallest moment, so the page below never moves back up.
test("the demos never shrink while they play", async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto("/");
  const demos = page.locator("div[style*='min-height']");
  await expect(demos).toHaveCount(2);
  const heights = () =>
    demos.evaluateAll((elements) =>
      elements.map((element) => element.getBoundingClientRect().height),
    );
  let last = await heights();

  for (let second = 0; second < 16; second += 1) {
    await page.waitForTimeout(1_000);
    const now = await heights();
    // Once both have been measured, neither gets shorter.
    now.forEach((height, index) =>
      expect(height).toBeGreaterThanOrEqual(last[index] - 1),
    );
    last = now;
  }
});

// The agent's preview types into its input without reaching the mic and send buttons.
test("the agent's preview types before its buttons", async ({ page }) => {
  test.slow();
  await page.goto("/");
  const input = page.locator("[inert] textarea");
  await input.scrollIntoViewIfNeeded();
  await expect(input).not.toHaveValue("", { timeout: 15_000 });

  for (let check = 0; check < 20; check += 1) {
    const overflow = await input.evaluate((element) => {
      const style = getComputedStyle(element);
      const context = document.createElement("canvas").getContext("2d")!;
      context.font = `${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
      const room =
        element.clientWidth -
        parseFloat(style.paddingInlineStart) -
        parseFloat(style.paddingInlineEnd);

      return context.measureText(element.value).width - room;
    });
    expect(overflow).toBeLessThanOrEqual(0);
    await page.waitForTimeout(250);
  }
});

// On phones the footer is one centered column; on desktop its links stand in three columns.
test("the footer is one centered column on phones", async ({ page }, info) => {
  await page.goto("/faq");
  const footer = page.getByRole("contentinfo");
  const links = footer.getByRole("navigation").getByRole("link");
  const lefts = await links.evaluateAll((elements) =>
    elements.map((element) => Math.round(element.getBoundingClientRect().left)),
  );
  const columns = new Set(lefts).size;

  if (!isPhone(info.project.name)) {
    expect(columns).toBe(3);

    return;
  }

  const width = page.viewportSize()!.width;
  const centers = await links.evaluateAll((elements) =>
    elements.map((element) => {
      const box = element.getBoundingClientRect();

      return box.left + box.width / 2;
    }),
  );

  for (const center of centers) {
    expect(Math.abs(center - width / 2)).toBeLessThan(4);
  }

  const icon = footer.getByRole("img", { name: "LinkedIn" }).locator("svg");
  expect((await icon.boundingBox())!.width).toBe(32);
  await expect(footer.getByRole("button", { name: "ask agent" })).toHaveCSS(
    "height",
    "48px",
  );
});

// On phones a dialog spans the screen's width, with square corners.
test("a dialog spans a phone's width", async ({ page }, info) => {
  test.setTimeout(120_000);
  await page.goto("/");
  await page
    .getByRole("button", { name: "About this page" })
    .filter({ visible: true })
    .click();
  const dialog = page.getByRole("dialog", { name: "How prepza works" });
  await expect(dialog).toBeVisible();
  // It finishes opening first.
  await page.waitForTimeout(400);
  const box = (await dialog.boundingBox())!;

  if (isPhone(info.project.name)) {
    expect(Math.round(box.x)).toBe(0);
    expect(Math.round(box.width)).toBe(page.viewportSize()!.width);
    await expect(dialog).toHaveCSS("border-top-left-radius", "0px");
    // The help fills the screen, and Close is in sight without scrolling, and after it.
    expect(Math.round(box.height)).toBe(page.viewportSize()!.height);
    const close = dialog.getByRole("button", { name: "Close" });
    await expect(close).toBeInViewport();
    await dialog.evaluate((element) => element.scrollBy(0, 2_000));
    await expect(close).toBeInViewport();
  } else {
    expect(box.x).toBeGreaterThan(0);
    await expect(dialog).not.toHaveCSS("border-top-left-radius", "0px");
  }
});

// "⌘/Ctrl + Enter to send" only where there's a keyboard: not on a touch screen.
test("the send shortcut hint shows only without a touch screen", async ({
  page,
}, info) => {
  await page.goto("/contact");
  const hint = page.getByText("⌘/Ctrl + Enter to send");

  if (isPhone(info.project.name)) {
    await expect(hint).toBeHidden();
  } else {
    await expect(hint).toBeVisible();
  }
});

// On phones the home page's box to start in and the price lists reach the screen's edges.
test("the home page's box and the prices span a phone's width", async ({
  page,
}, info) => {
  test.skip(!isPhone(info.project.name), "phones only");
  test.setTimeout(120_000);
  const width = page.viewportSize()!.width;

  await page.goto("/");
  const start = page.locator("main form").first();
  const startBox = (await start.boundingBox())!;
  expect(Math.round(startBox.x)).toBe(0);
  expect(Math.round(startBox.width)).toBe(width);

  await page.goto("/pricing");
  const prices = (await page.locator("main ul").first().boundingBox())!;
  expect(Math.round(prices.x)).toBe(0);
  expect(Math.round(prices.width)).toBe(width);
});

// Opening the home page doesn't put the cursor in its box: on a phone the keyboard would cover
// the page.
test("the home page's box isn't focused on load", async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto("/");
  await page.waitForTimeout(1_000);
  await expect(page.locator("main textarea").first()).not.toBeFocused();
});

// With reduced motion the API's example shows whole, its request and its answer.
test("the API example shows whole with reduced motion", async ({ page }) => {
  test.setTimeout(120_000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const example = page.locator("pre").first();
  await expect(example).toContainText("POST /api/v1/interviews");
  await page.waitForTimeout(1_500);
  await expect(example).toContainText("POST /api/v1/interviews");
});

// On phones a test's practice page has its level and language under the title, then its start.
test("a practice page starts under its tags on a phone", async ({
  page,
}, info) => {
  test.skip(!isPhone(info.project.name), "phones only");
  test.setTimeout(120_000);
  await page.goto("/practice");
  const href = await page
    .locator("main a[href^='/practice/']")
    .first()
    .getAttribute("href");
  await page.goto(href!);
  const tags = (await page
    .locator("main [data-slot=badge]")
    .first()
    .boundingBox())!;
  const start = (await page
    .getByRole("button", { name: "Start practice" })
    .boundingBox())!;
  expect(start.y).toBeGreaterThan(tags.y + tags.height);
});
