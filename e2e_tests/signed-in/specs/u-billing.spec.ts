import { expect, test } from "../fixtures";
import {
  api,
  createCompany,
  createInterview,
  inviteCandidate,
} from "../helpers/api";
import { addTopUp, inviteToken } from "../helpers/db";
import { openTab, visit } from "../helpers/navigation";
import { shot } from "../helpers/screenshots";
import { ownerEmail, throwawayEmail } from "../helpers/users";

// A company's billing: owners and admins see where the credits came from and went, and the
// candidates whose credits are reserved; a viewer has no billing tab, and its address sends them
// back to the interviews.
test("owner sees the company's billing, a viewer doesn't", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail());
  const company = await createCompany(owner);
  const tabs = owner
    .getByRole("main")
    .getByRole("navigation")
    .getByRole("link");

  // A new company's history: the welcome gift.
  await visit(owner, `/companies/${company.id}/interviews`);
  await expect(tabs.last()).toHaveText("Referrals");
  await expect(tabs.nth(-2)).toHaveText("Billing");
  await openTab(owner, "Billing");
  await expect(owner.getByText("Welcome gift")).toBeVisible();
  await expect(owner.getByRole("link", { name: "Reserved (0)" })).toBeVisible();
  // Nothing reserved yet: no "0 reserved" under the balance.
  await expect(owner.getByText(/credits? reserved/)).toHaveCount(0);
  await shot(owner, "history");

  // An invited candidate holds credits until they finish.
  const interviewId = await createInterview(owner, company.id);
  const candidate = throwawayEmail("billing-candidate");
  await inviteCandidate(owner, interviewId, candidate);
  await visit(owner, `/companies/${company.id}/billing`);
  await expect(owner.getByText("500 credits reserved")).toBeVisible();
  await owner.getByRole("link", { name: "Reserved (1)" }).click();
  await expect(owner).toHaveURL(/\?tab=reserved$/);
  await expect(owner.getByText(candidate)).toBeVisible();
  await shot(owner, "reserved");

  // A viewer joins through their invite.
  const viewer = throwawayEmail("billing-viewer");
  const member = await api<{ token: string }>(
    owner,
    "POST",
    `/companies/members?company_id=${company.id}`,
    { email: viewer, role: "viewer" },
  );
  const page = await signInAs(viewer);
  await api(page, "POST", `/companies/members/invites/${member.token}/accept`);

  await visit(page, `/companies/${company.id}/interviews`);
  await expect(
    page.getByRole("main").getByRole("navigation").getByRole("link", {
      name: "Referrals",
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("main").getByRole("navigation").getByRole("link", {
      name: "Billing",
    }),
  ).toHaveCount(0);
  await shot(page, "viewer-tabs");
  await visit(page, `/companies/${company.id}/billing`);
  await expect(page).toHaveURL(
    new RegExp(`/companies/${company.id}/interviews$`),
  );
});

// The history's rows for paid credits and spent ones: a top-up with what was paid and its
// invoice, and a candidate's charge, once they answer, led by the candidate and opening them.
test("the history lists a top-up and a candidate's charge", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail());
  const company = await createCompany(owner);
  const interviewId = await createInterview(owner, company.id);
  const email = throwawayEmail("billing-charged");
  await inviteCandidate(owner, interviewId, email);
  await addTopUp(company.id, 2500, 5000);

  // The candidate answers one question and finishes, as the app's player does.
  const candidate = await signInAs(email);
  const { sessions } = await api<{ sessions: { id: string }[] }>(
    candidate,
    "POST",
    `/companies/invites/${await inviteToken(email)}/start`,
  );
  const step = await api<{
    session: { id: string };
    question: { question_id: string };
  }>(candidate, "POST", `/rounds/sessions/${sessions[0].id}/step`);
  await api(candidate, "POST", `/rounds/sessions/${step.session.id}/answers`, {
    question_id: step.question.question_id,
    option_index: 0,
  });
  await api(
    candidate,
    "POST",
    `/rounds/sessions/${sessions[0].id}/finish-interview`,
  );

  const topUp = owner.getByRole("listitem").filter({ hasText: "Top-up" });
  const charge = owner.getByRole("link").filter({ hasText: email });

  // The charge comes once the scorecard is made.
  await expect(async () => {
    await visit(owner, `/companies/${company.id}/billing`);
    await expect(charge).toBeVisible({ timeout: 3_000 });
  }).toPass({ timeout: 90_000 });
  await expect(topUp).toContainText("$50");
  await expect(topUp).toContainText("+2,500");
  await expect(topUp.getByRole("button", { name: "Invoice" })).toBeVisible();
  await expect(charge).toContainText("-500");
  await expect(owner.getByRole("link", { name: "Reserved (0)" })).toBeVisible();
  await shot(owner, "history-top-up-and-charge");

  await charge.click();
  await expect(owner).toHaveURL(
    new RegExp(`/companies/${company.id}/interviews/${interviewId}/candidates/[^/?]+$`),
    { timeout: 90_000 },
  );
});
