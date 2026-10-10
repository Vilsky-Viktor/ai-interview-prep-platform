import { expect, test } from "../fixtures";
import {
  api,
  createCompany,
  createInterview,
  inviteCandidate,
} from "../helpers/api";
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
  await expect(owner.getByText("300 credits reserved")).toBeVisible();
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
