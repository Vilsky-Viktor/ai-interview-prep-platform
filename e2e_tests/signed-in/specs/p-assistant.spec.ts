import { expect, test } from "../fixtures";
import { createCompany } from "../helpers/api";
import { visit } from "../helpers/navigation";
import { shot } from "../helpers/screenshots";
import { ownerEmail } from "../helpers/users";
import type { Locator, Page, Route } from "@playwright/test";

// The assistant's panel signed in: the welcome for the user's stage (the real service), an
// answer with a candidate row, voice with Chrome's fake microphone, the history, and a reload
// in the middle of a chat; and a visitor who signs in from the sign-in card keeps their chat.
// Answers and transcripts are stubbed in the browser: no OpenAI in tests.

const CONVERSATION = "11111111-2222-4333-8444-555555555555";
const CANDIDATE_LINK = "/companies/c/interviews/i/candidates/1";

// Chrome's fake microphone, beside the host rules the config sets.
test.use({
  launchOptions: {
    args: [
      ...(process.env.HOST_RULES ? [`--host-resolver-rules=${process.env.HOST_RULES}`] : []),
      "--use-fake-device-for-media-stream",
      "--use-fake-ui-for-media-stream",
    ],
  },
});

/** Server-sent events, as the chat routes stream them. */
function events(...items: object[]) {
  return items.map((item) => `data: ${JSON.stringify(item)}\n\n`).join("");
}

/** The assistant answering every message; the bodies it was sent. */
async function assistantAnswers(page: Page) {
  const sent: Record<string, unknown>[] = [];
  await page.route("**/api/assistant/chat", (route: Route) => {
    sent.push(route.request().postDataJSON());

    return route.fulfill({
      contentType: "text/event-stream",
      body: events(
        { conversation: { id: CONVERSATION } },
        { tool: { name: "list_candidates", state: "running", label: "Reading candidates…" } },
        {
          block: {
            kind: "candidate_rows",
            items: [{ email: "ann@example.com", status: "finished", grade: 82, passed: true, progress: 100, tab_leaves: 0, copies: 0, fast_answers: 0 }],
            links: [CANDIDATE_LINK],
          },
        },
        { delta: "**Ann** passed with 82%." },
        { done: { message_id: "m1" } }
      ),
    });
  });
  // The conversation as the service would keep it.
  const saved = {
    id: CONVERSATION,
    company_id: null,
    title: "Who passed?",
    created_at: "2026-10-09T10:00:00Z",
    updated_at: "2026-10-09T10:00:00Z",
  };
  await page.route(`**/api/assistant/conversations/${CONVERSATION}`, (route) =>
    route.request().method() === "DELETE"
      ? route.fulfill({ status: 204 })
      : route.fulfill({
          json: {
            ...saved,
            messages: [
              { id: "q", role: "user", source: "text", content: "Who passed?", blocks: [], status: "complete", created_at: saved.created_at },
              { id: "a", role: "assistant", source: "text", content: "**Ann** passed with 82%.", blocks: [], status: "complete", created_at: saved.created_at },
            ],
          },
        })
  );
  await page.route("**/api/assistant/conversations?*", (route) => route.fulfill({ json: [saved] }));
  await page.route("**/api/assistant/conversations", (route) => route.fulfill({ json: [saved] }));

  return sent;
}

async function openPanel(page: Page): Promise<Locator> {
  await page.getByRole("banner").getByRole("button", { name: "ask agent" }).click();
  const panel = page.getByRole("dialog", { name: "Assistant" });
  await expect(panel).toBeVisible();

  return panel;
}

test("the assistant welcomes by stage, answers, takes voice, keeps history and survives a reload", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail());
  let panel = await openPanel(owner);
  // Open, the input is ready to type in.
  await expect(panel.getByRole("textbox")).toBeFocused();

  // No company yet, then a company that isn't verified: the service decides the stage.
  await expect(panel.getByText("Let's get you started")).toBeVisible();
  await expect(panel.getByRole("button", { name: "How do I create a company?" })).toBeVisible();
  await shot(owner, "welcome-no-company");
  await panel.getByRole("button", { name: "Close" }).click();
  const company = await createCompany(owner);
  panel = await openPanel(owner);
  await expect(panel.getByText("Verify your company so candidates see")).toBeVisible();

  // The company picker: all companies outside a company's pages, the page's company on them.
  const picker = panel.getByRole("button", { name: "Company", exact: true });
  await expect(picker).toHaveText(/all companies/i);
  await panel.getByRole("button", { name: "Close" }).click();
  await visit(owner, `/companies/${company.id}/interviews`);
  panel = await openPanel(owner);
  await expect(picker).toHaveText(company.name);

  // An answer: the tool at work, the markdown, and the candidate's row linking to their page.
  const sent = await assistantAnswers(owner);
  await panel.getByRole("textbox").fill("Who passed?");
  await panel.getByRole("button", { name: "Send" }).click();
  await expect(panel.locator("strong", { hasText: "Ann" })).toBeVisible();
  await expect(panel.getByRole("link", { name: /ann@example\.com/ })).toHaveAttribute("href", CANDIDATE_LINK);
  await shot(owner, "answer");
  expect(sent[0]).toMatchObject({
    message: "Who passed?",
    source: "text",
    company_id: company.id,
    earlier: [],
  });

  // Picking all companies sends no company with the next message.
  await picker.click();
  await owner.getByRole("menuitemradio", { name: /all companies/i }).click();
  await expect(picker).toHaveText(/all companies/i);

  // Voice from the keyboard: Enter starts, Enter stops; the transcript is sent as the message.
  await owner.route("**/api/assistant/transcribe", (route) => {
    expect(route.request().headers()["content-type"]).toMatch(/^audio\//);

    return route.fulfill({ json: { text: "Who else passed?" } });
  });
  const mic = panel.getByRole("button", { name: "Hold to talk" });
  await mic.focus();
  await owner.keyboard.press("Enter");
  await expect(panel.getByRole("button", { name: "Stop recording" })).toHaveAttribute("aria-pressed", "true");
  await expect(panel.getByRole("status")).toContainText("Recording…");
  await shot(owner, "recording");
  await owner.waitForTimeout(1_200);
  await owner.keyboard.press("Enter");
  await expect(panel.getByRole("list").getByText("Who else passed?")).toBeVisible();
  expect(sent[1]).toMatchObject({ message: "Who else passed?", source: "voice", conversation_id: CONVERSATION });
  expect(sent[1].company_id).toBeUndefined();

  // Esc cancels a recording without closing the panel; nothing is sent.
  await mic.focus();
  await owner.keyboard.press("Enter");
  await expect(panel.getByRole("button", { name: "Stop recording" })).toBeVisible();
  await owner.keyboard.press("Escape");
  await expect(mic).toBeVisible();
  expect(sent).toHaveLength(2);

  // A click beside the panel closes it; reopened, the conversation is still there.
  await owner.mouse.click(100, 500);
  await expect(panel).toHaveCount(0);
  panel = await openPanel(owner);
  await expect(panel.getByRole("list").getByText("Who else passed?")).toBeVisible();

  // Its width: wider with the arrow keys, no narrower than 360px however far it's dragged.
  const handle = panel.getByRole("separator", { name: "Resize the panel" });
  const width = async () => (await panel.boundingBox())!.width;
  await expect.poll(width).toBe(448);
  await shot(owner, "width-default");
  await handle.focus();
  await owner.keyboard.press("ArrowLeft");
  await owner.keyboard.press("ArrowLeft");
  await expect.poll(width).toBe(480);
  const box = (await handle.boundingBox())!;
  await owner.mouse.move(box.x + box.width / 2, box.y + 300);
  await owner.mouse.down();
  await owner.mouse.move(200, box.y + 300, { steps: 5 });
  await owner.mouse.up();
  await expect.poll(width).toBe(896);
  await shot(owner, "width-wide");
  const wide = (await handle.boundingBox())!;
  await owner.mouse.move(wide.x + wide.width / 2, wide.y + 300);
  await owner.mouse.down();
  await owner.mouse.move(1270, wide.y + 300, { steps: 5 });
  await owner.mouse.up();
  await expect.poll(width).toBe(360);
  await shot(owner, "width-narrow");

  // A reload in the middle of the chat brings the panel and the conversation back.
  await owner.reload();
  panel = owner.getByRole("dialog", { name: "Assistant" });
  await expect(panel.getByRole("list").getByText("Who passed?")).toBeVisible();
  // The pick and the width came back with it.
  await expect(panel.getByRole("button", { name: "Company", exact: true })).toHaveText(/all companies/i);
  await expect.poll(async () => (await panel.boundingBox())!.width).toBe(360);

  // The history lists it; deleting asks first.
  await panel.getByRole("button", { name: "History" }).click();
  await expect(panel.getByRole("button", { name: /^Who passed\? / })).toBeVisible();
  await shot(owner, "history");
  await panel.getByRole("button", { name: "Delete “Who passed?”" }).click();
  await owner.getByRole("dialog", { name: "Delete this chat?" }).getByRole("button", { name: "Delete" }).click();
  await expect(panel.getByText("No chats yet.")).toBeVisible();

  // New chat forgets it, with the input ready again: a reload shows the welcome.
  await panel.getByRole("button", { name: "New chat" }).click();
  await expect(panel.getByRole("textbox")).toBeFocused();
  await owner.reload();
  panel = owner.getByRole("dialog", { name: "Assistant" });
  await expect(panel.getByText("Verify your company so candidates see")).toBeVisible();
});

test("a visitor who signs in from the sign-in card keeps their chat", async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.route("**/api/rounds/help/chat", (route) =>
    route.fulfill({
      contentType: "text/event-stream",
      body: events(
        { block: { kind: "sign_in", items: [], links: [], provider: "google" } },
        { delta: "Sign in below to create it." },
        { done: true }
      ),
    })
  );
  await visit(page, "/");
  const panel = await openPanel(page);
  await panel.getByRole("textbox").fill("Create a company");
  await panel.getByRole("button", { name: "Send" }).click();
  await expect(panel.getByRole("list").getByText("Sign in below to create it.")).toBeVisible();

  // A reload keeps the visitor's chat and the open panel.
  await page.reload();
  const again = page.getByRole("dialog", { name: "Assistant" });
  await expect(again.getByRole("list").getByText("Create a company")).toBeVisible();

  const sent = await assistantAnswers(page);
  const opened = context.waitForEvent("page");
  await again.getByRole("button", { name: /continue with google/i }).click();
  const popup = await opened;
  await popup.waitForLoadState();
  await popup.getByText(/add new account/i).click();
  await popup.locator("#email-input").fill(ownerEmail());
  await popup.locator("#display-name-input").fill("e2e owner");
  await popup.locator("#sign-in").click();
  await popup.waitForEvent("close");

  // Signed in, the panel is still open with the chat, and the next message carries it.
  await expect(again.getByRole("button", { name: "History" })).toBeVisible();
  await expect(again.getByRole("list").getByText("Create a company")).toBeVisible();
  await again.getByRole("textbox").fill("Call it Acme");
  await again.getByRole("button", { name: "Send" }).click();
  await expect(again.locator("strong", { hasText: "Ann" })).toBeVisible();
  expect(sent[0]).toMatchObject({
    message: "Call it Acme",
    earlier: [
      { role: "user", content: "Create a company" },
      { role: "assistant", content: "Sign in below to create it." },
    ],
  });
  await context.close();
});
