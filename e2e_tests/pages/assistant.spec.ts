import { expect, type Page, test } from "@playwright/test";

// Signed out, "ask agent" opens the assistant with FAQ answers only: the welcome for visitors,
// an answer from the help chat (stubbed here: no OpenAI in tests), and a sign-in card when the
// visitor asks to sign in. No history, company or voice.

/** The help chat answering with these server-sent events. */
async function helpAnswers(page: Page, events: object[]) {
  await page.route("**/api/rounds/help/chat", (route) =>
    route.fulfill({
      contentType: "text/event-stream",
      body: [...events, { done: true }].map((event) => `data: ${JSON.stringify(event)}\n\n`).join(""),
    })
  );
}

async function openPanel(page: Page) {
  await page.goto("/");
  await page.getByRole("banner").getByRole("button", { name: "ask agent" }).click();
  const panel = page.getByRole("dialog", { name: "Assistant" });
  await expect(panel).toBeVisible();

  return panel;
}

test("a visitor asks the assistant about prepza", async ({ page }) => {
  await helpAnswers(page, [{ delta: "Each candidate costs " }, { delta: "**$1–3**." }]);
  const panel = await openPanel(page);

  await expect(panel.getByText("Sign in to ask about your companies and candidates.")).toBeVisible();
  await expect(panel.getByRole("button", { name: "History" })).toHaveCount(0);
  await expect(panel.getByRole("button", { name: "Hold to talk" })).toHaveCount(0);

  // Open, the input is ready to type in, but not on a touch phone, where the keyboard would
  // cover the welcome.
  const field = panel.getByRole("textbox");
  if (test.info().project.name === "phone") {
    await expect(field).not.toBeFocused();
  } else {
    await expect(field).toBeFocused();
  }

  // A welcome question is sent as the message; the answer's markdown is rendered.
  await panel.getByRole("button", { name: "How much does it cost?" }).click();
  await expect(panel.getByRole("list").getByText("How much does it cost?")).toBeVisible();
  await expect(panel.locator("strong", { hasText: "$1–3" })).toBeVisible();
  if (test.info().project.name !== "phone") {
    await expect(field).toBeFocused();
  }

  // The wheel over the panel never scrolls the page behind it; over the page, it does.
  if (test.info().project.name !== "phone") {
    const before = await page.evaluate(() => window.scrollY);
    const box = (await panel.boundingBox())!;
    await page.mouse.move(box.x + box.width / 2, box.y + 40);
    await page.mouse.wheel(0, 600);
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.mouse.wheel(0, 600);
    await page.waitForTimeout(300);
    expect(await page.evaluate(() => window.scrollY)).toBe(before);
    await page.mouse.move(100, 400);
    await page.mouse.wheel(0, 600);
    await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(before);
  }

  // A click beside the panel closes it on wider screens; reopened, the chat is still there.
  if (test.info().project.name !== "phone") {
    await page.mouse.click(100, 500);
    await expect(panel).toHaveCount(0);
    await page.getByRole("banner").getByRole("button", { name: "ask agent" }).click();
    await expect(panel.locator("strong", { hasText: "$1–3" })).toBeVisible();
  }

  // New chat starts over; the panel closes and comes back empty of nothing it kept.
  await panel.getByRole("button", { name: "New chat" }).click();
  await expect(panel.getByRole("button", { name: "What is prepza?" })).toBeVisible();
  await panel.getByRole("button", { name: "Close" }).click();
  await expect(panel).toHaveCount(0);
});

test("a visitor asking to sign in gets the sign-in card, their way first", async ({ page }) => {
  await helpAnswers(page, [
    { block: { kind: "sign_in", items: [], links: [], provider: "github" } },
    { delta: "Sign in below with GitHub." },
  ]);
  const panel = await openPanel(page);
  await panel.getByRole("textbox").fill("sign me in with github");
  await panel.getByRole("button", { name: "Send" }).click();

  await expect(panel.getByRole("list").getByText("Sign in below with GitHub.")).toBeVisible();
  const ways = panel.getByRole("button", { name: /continue with/i });
  await expect(ways).toHaveCount(3);
  await expect(ways.first()).toHaveAccessibleName(/GitHub/);
});

test("a failed answer shows its error and Try again asks again", async ({ page }) => {
  let calls = 0;
  await page.route("**/api/rounds/help/chat", (route) => {
    calls += 1;

    return calls === 1
      ? route.fulfill({ status: 503, json: { detail: "Paused for now." } })
      : route.fulfill({ contentType: "text/event-stream", body: 'data: {"delta":"Back."}\n\n' });
  });
  const panel = await openPanel(page);
  await panel.getByRole("textbox").fill("Hi");
  await panel.getByRole("button", { name: "Send" }).click();
  await expect(panel.getByRole("list").getByText("Paused for now.")).toBeVisible();

  await panel.getByRole("button", { name: "Try again" }).click();
  await expect(panel.getByRole("list").getByText("Back.")).toBeVisible();
  await expect(panel.getByRole("list").getByText("Paused for now.")).toHaveCount(0);
});

test("a reload in the middle of a visitor's chat brings it back", async ({ page }) => {
  await helpAnswers(page, [{ delta: "A hiring test." }]);
  const panel = await openPanel(page);
  await panel.getByRole("button", { name: "What is prepza?" }).click();
  await expect(panel.getByRole("list").getByText("A hiring test.")).toBeVisible();

  await page.reload();
  const again = page.getByRole("dialog", { name: "Assistant" });
  await expect(again.getByRole("list").getByText("What is prepza?")).toBeVisible();
  await expect(again.getByRole("list").getByText("A hiring test.")).toBeVisible();

  // A chat older than the service's window (GET /config) isn't brought back.
  await page.evaluate(() => {
    const kept = JSON.parse(sessionStorage.getItem("prepza:assistant:visitor") ?? "{}");
    kept.lastAt = new Date(Date.now() - 31 * 60_000).toISOString();
    sessionStorage.setItem("prepza:assistant:visitor", JSON.stringify(kept));
  });
  await page.reload();
  await expect(page.getByRole("banner").getByRole("button", { name: "ask agent" })).toBeVisible();
  await expect(again).toHaveCount(0);

  // Opened, it's a new chat; closed, it stays closed after a reload.
  await page.getByRole("banner").getByRole("button", { name: "ask agent" }).click();
  await expect(again.getByRole("button", { name: "What is prepza?" })).toBeVisible();
  await again.getByRole("button", { name: "Close" }).click();
  await page.reload();
  await expect(page.getByRole("banner").getByRole("button", { name: "ask agent" })).toBeVisible();
  await expect(again).toHaveCount(0);
});
