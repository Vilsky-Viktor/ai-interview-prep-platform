import { expect, test } from "../fixtures";
import { createCompany } from "../helpers/api";
import { CONVERSATION, events, openPanel } from "../helpers/assistant";
import { visit } from "../helpers/navigation";
import { shot } from "../helpers/screenshots";
import { ownerEmail } from "../helpers/users";

// The assistant's panel signed in, continued from p-assistant: an action runs once its card is
// confirmed, asking to sign out signs out, and a pasted secret never stays in the chat. Answers
// are stubbed in the browser: no OpenAI in tests.

test("an action runs once its card is confirmed, and asking to sign out signs out", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail());
  const actionId = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee";
  const card = {
    kind: "confirm",
    items: [],
    links: [],
    action_id: actionId,
    tool: "create_company",
    preview: { name: "Acme" },
    company_id: null,
    destructive: false,
    state: "pending",
  };
  let confirms = 0;
  await owner.route("**/api/assistant/chat", (route) => {
    const asked = route.request().postDataJSON().message;

    return route.fulfill({
      contentType: "text/event-stream",
      body:
        asked === "Sign me out"
          ? events({ conversation: { id: CONVERSATION } }, { sign_out: true }, { delta: "Bye." })
          : events(
              { conversation: { id: CONVERSATION } },
              { block: card },
              { delta: "Confirm it below." },
              { done: { message_id: "m1" } }
            ),
    });
  });
  await owner.route(`**/api/assistant/conversations/${CONVERSATION}/actions/${actionId}/confirm`, (route) => {
    confirms += 1;

    return route.fulfill({
      contentType: "text/event-stream",
      body: events(
        { conversation: { id: CONVERSATION } },
        { action: { ...card, state: "done", links: ["/companies/c1/interviews"] } },
        { delta: "Acme is ready." },
        { done: { message_id: "m2" } }
      ),
    });
  });
  const panel = await openPanel(owner);
  await panel.getByRole("textbox").fill("Create a company called Acme");
  await panel.getByRole("button", { name: "Send" }).click();

  // The card shows exactly what runs; Confirm runs it once.
  await expect(panel.getByText("Create a company", { exact: true })).toBeVisible();
  await expect(panel.getByText("Acme", { exact: true })).toBeVisible();
  await shot(owner, "action-card");
  await panel.getByRole("button", { name: "Confirm" }).click();
  await expect(panel.getByText("Done", { exact: true })).toBeVisible();
  await expect(panel.getByRole("link", { name: /interviews/i })).toHaveAttribute("href", "/companies/c1/interviews");
  await expect(panel.getByRole("list").getByText("Acme is ready.")).toBeVisible();
  await expect(panel.getByRole("button", { name: "Confirm" })).toHaveCount(0);
  expect(confirms).toBe(1);
  await shot(owner, "action-done");

  // Asked to sign out, the panel signs out at once and shows the visitor's welcome.
  await panel.getByRole("textbox").fill("Sign me out");
  await panel.getByRole("button", { name: "Send" }).click();
  await expect(owner.getByRole("banner").getByRole("button", { name: /sign in/i })).toBeVisible();
  await expect(panel.getByRole("button", { name: "History" })).toHaveCount(0);
  await expect(panel.getByRole("button", { name: "What is prepza?" })).toBeVisible();
});

test("a pasted secret is removed from the chat and explained, with the page it belongs on", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail());
  const company = await createCompany(owner);
  await visit(owner, `/companies/${company.id}/integrations`);
  const panel = await openPanel(owner);
  // The case seen on localhost: no known format, named by the message.
  const secret = "94uf9jf394ur0fj394g3ffh3";
  await panel.getByRole("textbox").fill(`Add my secret to Greenhouse ATS integration: ${secret}`);
  await panel.getByRole("button", { name: "Send" }).click();

  await expect(panel.getByText("Message removed: it contained a secret")).toBeVisible();
  await expect(panel.getByRole("list").getByText(/Enter it yourself on the integrations page\./)).toBeVisible();
  await expect(panel.getByRole("link", { name: "open integrations" })).toHaveAttribute(
    "href",
    `/companies/${company.id}/integrations`
  );
  await shot(owner, "secret-removed");
  // Nowhere on the page, nor in what the browser keeps.
  await expect(panel.getByText(secret)).toHaveCount(0);
  const kept = await owner.evaluate(() => JSON.stringify({ ...localStorage, ...sessionStorage }));
  expect(kept).not.toContain(secret);

  // Nothing of it was saved: a reload brings no conversation back.
  await owner.reload();
  await expect(owner.getByRole("banner").getByRole("button", { name: "ask agent" })).toBeVisible();
  await expect(owner.getByRole("dialog", { name: "Assistant" })).toHaveCount(0);
});
