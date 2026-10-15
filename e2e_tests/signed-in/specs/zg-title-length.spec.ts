import { expect, test } from "../fixtures";
import { createCompany, createInterview } from "../helpers/api";
import { visit } from "../helpers/navigation";
import { throwawayEmail } from "../helpers/users";

// An editable title needs at least 3 characters: a shorter one isn't saved, and says why.
test("a test's title under three characters isn't saved", async ({
  signInAs,
}) => {
  const owner = await signInAs(throwawayEmail("title-length"));
  const company = await createCompany(owner);
  const interviewId = await createInterview(owner, company.id);

  await visit(owner, `/companies/${company.id}/interviews/${interviewId}`);
  const heading = owner.getByRole("heading", { level: 1 });
  const before = await heading.innerText();
  await heading.getByRole("button", { name: "Edit title" }).click();
  const input = owner.getByRole("textbox");
  await input.fill("ab");
  await input.press("Enter");

  await expect(owner.getByText("Use at least 3 characters.")).toBeVisible();
  await input.press("Escape");
  await expect(owner.getByRole("heading", { level: 1 })).toHaveText(before);
});

// A company name needs at least 2 characters (EY and 3M are companies): one letter is refused
// under the field.
test("a one-letter company name isn't accepted", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("company-name-length"));

  await visit(owner, "/companies");
  await owner.getByRole("button", { name: "New company" }).click();
  const dialog = owner.getByRole("dialog");
  await dialog.getByLabel("Company name").fill("A");
  await dialog.getByRole("button", { name: "Create" }).click();

  await expect(dialog.getByText("Use at least 2 characters.")).toBeVisible();
  await expect(owner).toHaveURL(/\/companies$/);
});
