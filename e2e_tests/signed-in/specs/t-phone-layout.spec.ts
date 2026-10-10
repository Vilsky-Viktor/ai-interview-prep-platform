import { type Locator, type Page } from "@playwright/test";

import { expect, test } from "../fixtures";
import {
  api,
  createCompany,
  createInterview,
  deleteOwnCompanies,
} from "../helpers/api";
import { visit } from "../helpers/navigation";
import { throwawayEmail } from "../helpers/users";

// How the signed-in pages fit a phone: lists and panels out to the screen's edges, actions on
// their own lines, dialogs across the screen with their buttons side by side, and timed questions
// with nothing around them.

const PHONE = { width: 390, height: 844 };

async function box(locator: Locator) {
  const found = (await locator.boundingBox({ timeout: 15_000 }))!;

  return {
    left: Math.round(found.x),
    top: Math.round(found.y),
    width: Math.round(found.width),
    bottom: Math.round(found.y + found.height),
  };
}

// The page's visible width: the header's, which spans it (without the scrollbar desktop Chrome
// draws; phones draw none).
async function pageWidth(page: Page) {
  return (await box(page.getByRole("banner"))).width;
}

// Out to both edges of the screen.
async function expectEdgeToEdge(page: Page, locator: Locator) {
  const found = await box(locator);
  expect(found.left).toBeLessThanOrEqual(0);
  expect(found.left + found.width).toBeGreaterThanOrEqual(
    await pageWidth(page),
  );
}

test("a company's pages on a phone", async ({ signInAs }) => {
  test.setTimeout(300_000);
  const user = await signInAs(throwawayEmail("phone"));
  const company = await createCompany(user);
  const interview = await createInterview(user, company.id);
  await api(user, "POST", `/companies/members?company_id=${company.id}`, {
    email: throwawayEmail("phone-member"),
    role: "admin",
  });
  await user.setViewportSize(PHONE);

  try {
    // The companies list: "new company" at full width under the title, rows without the logo.
    await visit(user, "/companies");
    const width = await pageWidth(user);
    const title = user.getByRole("heading", { name: /^companies/i });
    const create = user.getByRole("button", { name: "New company" });
    expect((await box(create)).top).toBeGreaterThan((await box(title)).bottom);
    expect((await box(create)).width).toBeGreaterThan(width - 60);
    const list = user.locator("main .divide-y").first();
    await expectEdgeToEdge(user, list);
    await expect(
      list.getByText(company.name.slice(0, 1), { exact: true }),
    ).toBeHidden();

    // A dialog spans the screen, its two buttons side by side, as tall and in the same font.
    await create.click();
    const dialog = user.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await user.waitForTimeout(400);
    expect((await box(dialog)).left).toBe(0);
    const cancel = await box(dialog.getByRole("button", { name: "Cancel" }));
    const submit = await box(dialog.getByRole("button", { name: "Create" }));
    expect(submit.top).toBe(cancel.top);
    expect(submit.width).toBe(cancel.width);
    await expect(dialog.getByRole("button", { name: "Create" })).toHaveCSS(
      "font-size",
      "16px",
    );
    await user.keyboard.press("Escape");

    // A company's interviews: the back arrow above the name, "new interview" under it, and
    // rows with only the title and date.
    await visit(user, `/companies/${company.id}/interviews`);
    const back = await box(user.getByRole("button", { name: "Companies" }));
    const name = await box(user.getByRole("heading", { level: 1 }));
    expect(back.bottom).toBeLessThanOrEqual(name.top + 4);
    const newInterview = user.getByRole("button", { name: "New interview" });
    expect((await box(newInterview)).top).toBeGreaterThan(name.bottom);
    expect((await box(newInterview)).width).toBeGreaterThan(width - 60);
    const row = user.locator("main .divide-y > *").first();
    await expect(row.getByRole("link", { name: /^Try/ })).toBeHidden();
    await expect(row.locator("[data-slot=interview-stats]")).toBeHidden();

    // The team: each member's role on the line under their email.
    await visit(user, `/companies/${company.id}/members`);
    const member = user.locator("main .divide-y > *").first();
    const email = await box(member.getByText(/@/).first());
    const role = await box(member.getByText("owner", { exact: true }));
    expect(role.top).toBeGreaterThanOrEqual(email.bottom);

    // Integrations: the buttons beside the logo, under the name.
    await visit(user, `/companies/${company.id}/integrations`);
    const slack = user.getByRole("listitem").filter({ hasText: "Slack" });
    const slackName = await box(slack.getByText("Slack", { exact: true }));
    const instructions = await box(
      slack.getByRole("button", { name: "Instructions" }),
    );
    expect(instructions.top).toBeGreaterThan(slackName.top);
    expect(instructions.left).toBeGreaterThan(40);
  } finally {
    await deleteOwnCompanies(user);
  }
});

// While questions run against the clock there's only the question: no header, footer or
// "ask agent". The preview before it keeps them, and they're back once it's finished.
test("timed questions on their own, with nothing around them", async ({
  signInAs,
}) => {
  test.setTimeout(300_000);
  const user = await signInAs(throwawayEmail("timed"));
  const company = await createCompany(user);
  const interview = await createInterview(user, company.id);

  try {
    await visit(user, `/companies/${company.id}/interviews/${interview}/try`);
    await expect(user.getByRole("banner")).toBeVisible();
    await expect(user.getByRole("contentinfo")).toBeVisible();
    await user.getByRole("button", { name: /accept & start/i }).click();
    await expect(user).toHaveURL(/\/sessions\//, { timeout: 90_000 });
    await expect(
      user.getByRole("button", { name: /finish interview/i }),
    ).toBeVisible();
    await expect(user.getByRole("banner")).toHaveCount(0);
    await expect(user.getByRole("contentinfo")).toHaveCount(0);
    await expect(user.getByRole("button", { name: "ask agent" })).toHaveCount(
      0,
    );

    // Once it's finished, they're back, and the footer is in view without scrolling.
    await user.getByRole("button", { name: /finish interview/i }).click();
    await user
      .getByRole("dialog")
      .getByRole("button", { name: "Finish", exact: true })
      .click();
    await expect(user.getByText("You have finished the interview")).toBeVisible(
      { timeout: 60_000 },
    );
    await expect(user.getByRole("banner")).toBeVisible();
    await expect(user.getByRole("contentinfo")).toBeInViewport();
  } finally {
    await deleteOwnCompanies(user);
  }
});

// On a phone the invitation's rules come before "accept & start".
test("an invitation's rules come before its start on a phone", async ({
  signInAs,
}) => {
  test.setTimeout(300_000);
  const user = await signInAs(throwawayEmail("rules"));
  const company = await createCompany(user);
  const interview = await createInterview(user, company.id);
  await user.setViewportSize(PHONE);

  try {
    await visit(user, `/companies/${company.id}/interviews/${interview}/try`);
    const rules = await box(
      user.getByRole("list").filter({ hasText: /four options/i }),
    );
    const start = await box(
      user.getByRole("button", { name: /accept & start/i }),
    );
    expect(start.top).toBeGreaterThan(rules.bottom);
    await expectEdgeToEdge(
      user,
      user.getByRole("list").filter({ hasText: /four options/i }),
    );
  } finally {
    await deleteOwnCompanies(user);
  }
});
