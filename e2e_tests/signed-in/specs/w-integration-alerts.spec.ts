import { expect, test } from "../fixtures";
import { createCompany } from "../helpers/api";
import { addCompanyNotification } from "../helpers/db-integrations";
import { visit } from "../helpers/navigation";
import { shot } from "../helpers/screenshots";
import { ownerEmail } from "../helpers/users";

// An ATS that takes the key but refuses the results written back: the company's bell says so,
// in red, and opens that ATS's page to reconnect.
test("the bell says when an ATS doesn't take candidates' results", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail());
  const company = await createCompany(owner);
  const page = `/companies/${company.id}/integrations/recruitee`;
  await addCompanyNotification(company.id, "ats_cannot_write", page, {
    ats: "Recruitee",
  });

  await visit(owner, `/companies/${company.id}/interviews`);
  await owner.getByRole("button", { name: /notification/i }).click();
  const notice = owner.getByText(
    "Recruitee doesn't take candidates' results: the key has no write access.",
    { exact: false },
  );
  await expect(notice).toBeVisible();
  await shot(owner, "bell");
  await notice.click();
  await expect(owner).toHaveURL(new RegExp(`${page}$`));
});

// A connection that stopped working (Slack's web hook gone, an ATS key revoked): the bell says
// what waits meanwhile and opens its page to reconnect.
test("the bell says when Slack stopped working", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail());
  const company = await createCompany(owner);
  const page = `/companies/${company.id}/integrations/slack`;
  await addCompanyNotification(company.id, "connection_broken", page, {
    name: "Slack",
    integration: "slack",
  });

  await visit(owner, `/companies/${company.id}/interviews`);
  await owner.getByRole("button", { name: /notification/i }).click();
  const notice = owner.getByText(
    "Slack stopped working and needs reconnecting. Until then, notifications don't reach your channel.",
  );
  await expect(notice).toBeVisible();
  await shot(owner, "bell-slack");
  await notice.click();
  await expect(owner).toHaveURL(new RegExp(`${page}$`));
});

// A web hook whose member is no longer an owner or admin: the bell names it and opens the API
// page.
test("the bell says when a web hook stopped", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail());
  const company = await createCompany(owner);
  const page = `/companies/${company.id}/integrations/api`;
  await addCompanyNotification(company.id, "webhook_stopped", page, {
    url: "https://example.com/prepza",
  });

  await visit(owner, `/companies/${company.id}/interviews`);
  await owner.getByRole("button", { name: /notification/i }).click();
  const notice = owner.getByText(
    "The web hook to https://example.com/prepza stopped: the member who added it is no longer an owner or admin.",
    { exact: false },
  );
  await expect(notice).toBeVisible();
  await shot(owner, "bell-webhook");
  await notice.click();
  await expect(owner).toHaveURL(new RegExp(`${page}$`));
});
