import { expect, test } from "../fixtures";
import { createCompany } from "../helpers/api";
import { addCompanyNotification } from "../helpers/db";
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
