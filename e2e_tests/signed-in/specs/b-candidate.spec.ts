import { expect, test } from "../fixtures";
import {
  createCompany,
  createInterview,
  inviteCandidate,
} from "../helpers/api";
import { inviteToken } from "../helpers/db";
import { openDialog, visit } from "../helpers/navigation";
import { shot } from "../helpers/screenshots";
import { answered } from "../helpers/session";
import { ownerEmail, throwawayEmail } from "../helpers/users";
import { MIN_QUESTION_SECONDS } from "../constants";

// A candidate takes an interview from their invite link: picks, changes the pick, goes on, lets a
// question's time run out, and finishes.
test("candidate takes the interview from the invite link", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail());
  const company = await createCompany(owner);
  const interviewId = await createInterview(owner, company.id);
  const email = throwawayEmail("candidate");
  await inviteCandidate(owner, interviewId, email);

  const candidate = await signInAs(email);
  const invitePath = `/invite/${await inviteToken(email)}`;
  await visit(candidate, invitePath);
  await expect(
    candidate.getByText(`${company.name} invited you to interview.`),
  ).toBeVisible();
  await expect(
    candidate.getByText(
      "You can change your pick until you press Next question.",
    ),
  ).toBeVisible();
  await shot(candidate, "invite");
  await candidate.getByRole("button", { name: "Accept & Start" }).click();
  await expect(candidate).toHaveURL(/\/sessions\//);

  // The pick can change until Next: one option marked at a time.
  const question = candidate.locator("[role=heading]").first();
  const options = candidate.getByRole("main").locator("button[aria-pressed]");
  await expect(options.first()).toBeVisible();
  await shot(candidate, "question");
  await options.nth(0).click();
  await expect(options.nth(0)).toHaveAttribute("aria-pressed", "true");
  await options.nth(1).click();
  await expect(options.nth(1)).toHaveAttribute("aria-pressed", "true");
  await expect(options.nth(0)).toHaveAttribute("aria-pressed", "false");
  await shot(candidate, "pick-changed");

  // A picked question can be reported; its reason comes from the site's menu, not the browser's.
  await openDialog(
    candidate,
    candidate.getByRole("button", { name: "Report question" }),
  );
  const report = candidate.getByRole("dialog");
  await report.getByRole("button", { name: "Report reason" }).click();
  await expect(candidate.locator("select")).toHaveCount(0);
  await shot(candidate, "report-reasons");
  await candidate.getByRole("menu").getByRole("menuitemradio").first().click();
  await expect(candidate.getByRole("menu")).toHaveCount(0);
  await expect(
    report.getByRole("button", { name: "Report reason" }),
  ).not.toHaveText("Select a reason");
  await shot(candidate, "report-reason-picked");
  await report.getByRole("button", { name: "Cancel" }).click();
  await expect(report).toHaveCount(0);
  const first = await question.textContent();
  await candidate.getByRole("button", { name: "Next question" }).click();
  await expect(question).not.toHaveText(first ?? "");
  await expect.poll(() => answered(candidate)).toBe("1");

  // No pick: the question's clock runs out and the next one opens by itself.
  const second = await question.textContent();
  await expect(candidate.getByRole("timer")).toBeVisible();
  await shot(candidate, "timer");
  await expect(question).not.toHaveText(second ?? "", {
    timeout: (MIN_QUESTION_SECONDS + 10) * 1000,
  });
  await expect.poll(() => answered(candidate)).toBe("2");
  await shot(candidate, "after-timeout");

  await candidate.getByRole("button", { name: "Finish interview" }).click();
  await expect(candidate.getByRole("dialog")).toContainText(
    "Finish the whole interview?",
  );
  await shot(candidate, "finish-dialog");
  await candidate
    .getByRole("dialog")
    .getByRole("button", { name: "Finish", exact: true })
    .click();
  await expect(
    candidate.getByText("You have finished the interview. Good luck!"),
  ).toBeVisible();
  await shot(candidate, "done");

  // The invite link now says the interview is finished, in an info card.
  await visit(candidate, invitePath);
  await expect(candidate.getByRole("status")).toHaveText(
    "This interview is already finished.",
  );
  await shot(candidate, "invite-finished");

  // The company sees them finished.
  await visit(
    owner,
    `/companies/${company.id}/interviews/${interviewId}?tab=candidates`,
  );
  await expect(owner.getByText(email, { exact: true }).first()).toBeVisible();
  await shot(owner, "owner-candidates");

  // Their report lists the questions they answered, without numbers.
  await owner.getByText(email, { exact: true }).first().click();
  await expect(owner.getByText(first ?? "").first()).toBeVisible();
  await expect(owner.getByText(/^\d+\.$/)).toHaveCount(0);
  await shot(owner, "owner-report");
});

// A visitor who isn't signed in sees what the invitation is for and a button to sign in, not the
// invited email; someone signed in with another email sees why they can't start, in a warning.
test("an invitation asks a visitor to sign in, and warns another email", async ({
  browser,
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail());
  const company = await createCompany(owner);
  const interviewId = await createInterview(owner, company.id);
  const email = throwawayEmail("candidate");
  await inviteCandidate(owner, interviewId, email);
  const path = `/invite/${await inviteToken(email)}`;

  const context = await browser.newContext();

  try {
    const visitor = await context.newPage();
    await visit(visitor, path);
    await expect(
      visitor.getByText(`${company.name} invited you to interview.`),
    ).toBeVisible();
    await expect(
      visitor.getByRole("button", { name: "Accept & Start" }),
    ).toHaveCount(0);
    await expect(visitor.getByText(email)).toHaveCount(0);
    await shot(visitor, "invite-signed-out");
    await visitor.getByRole("button", { name: "Sign in to start" }).click();
    await expect(visitor.getByRole("dialog")).toBeVisible();
  } finally {
    await context.close();
  }

  const other = await signInAs(throwawayEmail("other"));
  await visit(other, path);
  await expect(other.getByRole("status")).toContainText(
    "The email does not match. Sign in with the invitation email to start.",
  );
  await expect(
    other.getByRole("button", { name: "Accept & Start" }),
  ).toHaveCount(0);
  await shot(other, "invite-other-email");
});
