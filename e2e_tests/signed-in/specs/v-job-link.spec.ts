import { expect, test } from "../fixtures";
import { api, createCompany, createInterview } from "../helpers/api";
import { inviteToken, joinedEmails } from "../helpers/db";
import { visit } from "../helpers/navigation";
import { shot } from "../helpers/screenshots";
import { ownerEmail, throwawayEmail } from "../helpers/users";

// Someone starts from a test's shareable link (a job ad): the rules say their own link comes by
// email and extra time needs a personal invite. Their own link still works after the company
// turns the shareable link off.
test("a candidate starts from the job link and continues from their own link", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail());
  const company = await createCompany(owner);
  const interviewId = await createInterview(owner, company.id);
  const { link_token: token } = await api<{ link_token: string }>(
    owner,
    "PUT",
    `/companies/interviews/${interviewId}/link`,
    { on: true },
  );

  const email = throwawayEmail("link-candidate");
  const candidate = await signInAs(email);
  await visit(candidate, `/apply/${token}`);
  await expect(
    candidate.getByText("Progress is saved: we email you a link to continue."),
  ).toBeVisible();
  await expect(
    candidate.getByText(
      `Ask ${company.name} for a personal invite before you start: extra time can't be added here.`,
      { exact: false },
    ),
  ).toBeVisible();
  await expect(candidate.getByText("use this link again")).toHaveCount(0);
  await shot(candidate, "job-link");
  await candidate.getByRole("button", { name: "Accept & Start" }).click();
  await expect(candidate).toHaveURL(/\/sessions\//);
  await expect.poll(() => joinedEmails(email)).toBe(1);

  // The company takes the link down; the emailed link still continues the interview.
  await api(owner, "PUT", `/companies/interviews/${interviewId}/link`, {
    on: false,
  });
  await visit(candidate, `/invite/${await inviteToken(email)}`);
  await candidate.getByRole("button", { name: "Continue" }).click();
  await expect(candidate).toHaveURL(/\/sessions\//);
  // Starting again sends no second email.
  expect(await joinedEmails(email)).toBe(1);
});
