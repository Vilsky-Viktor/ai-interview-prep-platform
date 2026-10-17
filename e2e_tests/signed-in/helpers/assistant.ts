import { expect, type Locator, type Page, type Route } from "@playwright/test";

// The assistant's panel in the p-assistant specs: the panel opened from the header, and the
// assistant's answers stubbed in the browser (no OpenAI in tests).

export const CONVERSATION = "11111111-2222-4333-8444-555555555555";
export const CANDIDATE_LINK = "/companies/c/interviews/i/candidates/1";

/** Server-sent events, as the chat routes stream them. */
export function events(...items: object[]) {
  return items.map((item) => `data: ${JSON.stringify(item)}\n\n`).join("");
}

/** The assistant answering every message; the bodies it was sent. */
export async function assistantAnswers(page: Page) {
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
        { block: { kind: "link", items: [], links: ["/companies/c/interviews/i"], page: "interview", label: "Senior Backend" } },
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
  // The service brings back a recent conversation after a reload, until it's deleted.
  let active = true;
  await page.route(`**/api/assistant/conversations/${CONVERSATION}`, (route) => {
    if (route.request().method() === "DELETE") {
      active = false;

      return route.fulfill({ status: 204 });
    }

    return route.fulfill({
          json: {
            ...saved,
            messages: [
              { id: "q", role: "user", source: "text", content: "Who passed?", blocks: [], status: "complete", created_at: saved.created_at },
              { id: "a", role: "assistant", source: "text", content: "**Ann** passed with 82%.", blocks: [], status: "complete", created_at: saved.created_at },
            ],
          },
        });
  });
  await page.route("**/api/assistant/conversations?*", (route) => route.fulfill({ json: [saved] }));
  await page.route("**/api/assistant/conversations", (route) => route.fulfill({ json: [saved] }));
  await page.route("**/api/assistant/conversations/active", (route) =>
    active ? route.fulfill({ json: saved }) : route.fulfill({ status: 204 })
  );

  return sent;
}

export async function openPanel(page: Page): Promise<Locator> {
  await page.getByRole("banner").locator("[data-assistant-toggle]").click();
  const panel = page.getByRole("dialog");
  await expect(panel).toBeVisible();

  return panel;
}
